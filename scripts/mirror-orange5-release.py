#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

PUBLIC_KEY = "https://disk.yandex.ru/d/3yurdx5-APOkQQ"
DOWNLOAD_API = "https://cloud-api.yandex.net/v1/disk/public/resources/download"
REPO = "VMSeregA/fpv-encyclopedia-public"
RELEASE_BASE = f"https://github.com/{REPO}/releases/download"
TAG_PREFIX = "orange5-beta4"
PART_SIZE = 900


def run(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
  return subprocess.run(args, check=check, text=True, capture_output=True)


def load_files(manifest_path: Path) -> list[dict]:
  data = json.loads(manifest_path.read_text())
  files = data.get("files", data if isinstance(data, list) else [])
  return sorted(files, key=lambda item: item["path"])


def normalize_component(value: str, fallback: str) -> str:
  replacements = {
    "Обновление": "update",
    "Фото": "photos",
    "хороший": "good",
  }
  for src, dst in replacements.items():
    value = value.replace(src, dst)
  value = value.replace(",", ".").replace("=", ".")
  value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
  value = re.sub(r"[^A-Za-z0-9._+,=@-]+", "_", value)
  value = re.sub(r"_+", "_", value).strip("._-")
  return value or fallback


def split_compound_suffix(name: str) -> tuple[str, str]:
  for suffix in (".bin.gz", ".tar.gz"):
    if name.endswith(suffix):
      return name[: -len(suffix)], suffix
  stem, suffix = os.path.splitext(name)
  return stem, suffix


def asset_name(source_path: str) -> str:
  digest = hashlib.sha1(source_path.encode("utf-8")).hexdigest()[:10]
  parts = [part for part in source_path.strip("/").split("/") if part]
  if not parts:
    return f"download--{digest}"

  filename = parts[-1]
  stem, suffix = split_compound_suffix(filename)
  safe_parts = [
    normalize_component(part, f"part-{hashlib.sha1(part.encode('utf-8')).hexdigest()[:6]}")
    for part in parts[:-1]
  ]
  safe_stem = normalize_component(stem, "file")
  base = "__".join([*safe_parts, safe_stem])
  max_base_len = 180 - len(digest) - len(suffix) - 2
  if len(base) > max_base_len:
    base = base[:max_base_len].rstrip("._-")
  return f"{base}--{digest}{suffix}"


def release_part(index: int) -> int:
  return index // PART_SIZE + 1


def release_tag(index: int) -> str:
  return f"{TAG_PREFIX}-part{release_part(index)}"


def release_url(index: int, source_path: str) -> str:
  name = urllib.parse.quote(asset_name(source_path), safe="")
  return f"{RELEASE_BASE}/{release_tag(index)}/{name}"


def yandex_download_href(source_path: str) -> str:
  url = f"{DOWNLOAD_API}?{urllib.parse.urlencode({'public_key': PUBLIC_KEY, 'path': source_path})}"
  api = subprocess.run(
    [
      "curl",
      "--fail",
      "--silent",
      "--show-error",
      "--retry",
      "8",
      "--retry-all-errors",
      "--connect-timeout",
      "20",
      "--max-time",
      "90",
      url,
    ],
    text=True,
    capture_output=True,
  )
  if api.returncode != 0:
    raise RuntimeError(api.stderr.strip() or f"curl exited {api.returncode}")
  payload = json.loads(api.stdout)
  href = payload.get("href")
  if not href:
    raise RuntimeError(f"No download href for {source_path}")
  return href


def download_file(item: tuple[int, dict], out_dir: Path) -> Path:
  index, file_info = item
  source_path = file_info["path"]
  dest = out_dir / asset_name(source_path)
  expected_size = int(file_info.get("size") or 0)
  if dest.exists() and (expected_size == 0 or dest.stat().st_size == expected_size):
    return dest

  out_dir.mkdir(parents=True, exist_ok=True)
  temp = dest.with_suffix(dest.suffix + ".tmp")
  last_error: Exception | None = None
  for attempt in range(1, 9):
    try:
      href = yandex_download_href(source_path)
      curl = subprocess.run(
        [
          "curl",
          "--fail",
          "--location",
          "--silent",
          "--show-error",
          "--retry",
          "8",
          "--retry-all-errors",
          "--connect-timeout",
          "30",
          "--max-time",
          "300",
          "--output",
          str(temp),
          href,
        ],
        text=True,
        capture_output=True,
      )
      if curl.returncode != 0:
        raise RuntimeError(curl.stderr.strip() or f"curl exited {curl.returncode}")
      if expected_size and temp.stat().st_size != expected_size:
        raise RuntimeError(
          f"Size mismatch for {source_path}: got {temp.stat().st_size}, expected {expected_size}",
        )
      temp.replace(dest)
      return dest
    except Exception as error:
      last_error = error
      if temp.exists():
        temp.unlink()
      time.sleep(attempt * 2)

  raise RuntimeError(f"Failed to download {source_path}: {last_error}")


def ensure_release(tag: str) -> None:
  if run(["gh", "release", "view", tag], check=False).returncode == 0:
    return
  part = tag.rsplit("part", 1)[-1]
  run(
    [
      "gh",
      "release",
      "create",
      tag,
      "--title",
      f"Orange 5 Beta 4 files, part {part}",
      "--notes",
      "Зеркало файлов Orange 5 Beta 4 для прямого скачивания с FPV-энциклопедии.",
    ],
  )


def release_assets(tag: str) -> set[str]:
  release = run(["gh", "api", f"repos/{REPO}/releases/tags/{tag}", "--jq", ".id"], check=False)
  if release.returncode != 0:
    return set()
  release_id = release.stdout.strip()
  result = None
  for attempt in range(1, 5):
    result = run(
      ["gh", "api", "--paginate", f"repos/{REPO}/releases/{release_id}/assets", "--jq", ".[].name"],
      check=False,
    )
    if result.returncode == 0:
      break
    print(
      f"{tag}: asset listing failed on attempt {attempt}: {result.stderr.strip() or result.stdout.strip()}",
      flush=True,
    )
    time.sleep(attempt * 5)
  if result is None or result.returncode != 0:
    raise RuntimeError(f"{tag}: failed to list release assets")
  return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def upload_assets(files: list[dict], out_dir: Path, batch_size: int) -> None:
  for part in range(1, release_part(len(files) - 1) + 1):
    tag = f"{TAG_PREFIX}-part{part}"
    ensure_release(tag)
    existing = release_assets(tag)
    part_items = [
      (index, file_info)
      for index, file_info in enumerate(files)
      if release_part(index) == part
    ]
    missing = [out_dir / asset_name(file_info["path"]) for _, file_info in part_items if asset_name(file_info["path"]) not in existing]
    print(f"{tag}: {len(existing)} assets already uploaded, {len(missing)} missing")
    for start in range(0, len(missing), batch_size):
      batch = missing[start : start + batch_size]
      if not batch:
        continue
      print(f"{tag}: uploading {start + 1}-{start + len(batch)} of {len(missing)}")
      upload_args = ["gh", "release", "upload", tag, "--clobber", *map(str, batch)]
      for attempt in range(1, 5):
        result = run(upload_args, check=False)
        if result.returncode == 0:
          break
        print(
          f"{tag}: upload batch failed on attempt {attempt}: {result.stderr.strip() or result.stdout.strip()}",
          flush=True,
        )
        time.sleep(attempt * 5)
      else:
        raise RuntimeError(f"{tag}: upload batch failed after retries")


def download_assets(files: list[dict], out_dir: Path, workers: int) -> None:
  indexed = list(enumerate(files))
  done = 0
  total = len(indexed)
  failures = []
  with ThreadPoolExecutor(max_workers=workers) as executor:
    futures = {executor.submit(download_file, item, out_dir): item for item in indexed}
    for future in as_completed(futures):
      index, file_info = futures[future]
      try:
        future.result()
      except Exception as error:
        failures.append((file_info["path"], str(error)))
        print(f"FAILED {file_info['path']}: {error}", flush=True)
      done += 1
      if done % 25 == 0 or done == total:
        print(f"downloaded {done}/{total}: {file_info['path']}", flush=True)
  if failures:
    print(f"download failures: {len(failures)}", flush=True)
    for source_path, error in failures[:20]:
      print(f"- {source_path}: {error}", flush=True)
    raise SystemExit(1)


def rewrite_content_links(files: list[dict], content_dir: Path) -> int:
  replacements = {}
  for index, file_info in enumerate(files):
    source_path = file_info["path"]
    encoded = urllib.parse.quote(source_path, safe="")
    replacements[f"https://vmserega.github.io/fpv-encyclopedia-public/static/yandex-download.html?p={encoded}"] = release_url(
      index,
      source_path,
    )
    replacements[f"/static/yandex-download.html?p={encoded}"] = release_url(index, source_path)

  changed = 0
  for path in content_dir.rglob("*.md"):
    text = path.read_text()
    new_text = text
    for old, new in replacements.items():
      new_text = new_text.replace(old, new)
    if new_text != text:
      path.write_text(new_text)
      changed += 1
      print(f"rewrote {path}")
  return changed


def print_plan(files: list[dict]) -> None:
  names = [asset_name(file_info["path"]) for file_info in files]
  print(f"files: {len(files)}", flush=True)
  print(f"unique asset names: {len(set(names))}", flush=True)
  print(f"parts: {release_part(len(files) - 1)}", flush=True)
  print(
    f"total size: {sum(int(file_info.get('size') or 0) for file_info in files) / 1024 / 1024:.2f} MiB",
    flush=True,
  )
  if len(names) != len(set(names)):
    print("ERROR: asset name collision", file=sys.stderr)
    sys.exit(1)


def main() -> None:
  parser = argparse.ArgumentParser()
  parser.add_argument("--manifest", type=Path, default=Path("/tmp/orange5beta4-yandex-manifest.json"))
  parser.add_argument("--out-dir", type=Path, default=Path("/tmp/orange5beta4-release-assets"))
  parser.add_argument("--content-dir", type=Path, default=Path("content"))
  parser.add_argument("--workers", type=int, default=6)
  parser.add_argument("--batch-size", type=int, default=50)
  parser.add_argument("--download", action="store_true")
  parser.add_argument("--upload", action="store_true")
  parser.add_argument("--rewrite", action="store_true")
  args = parser.parse_args()

  files = load_files(args.manifest)
  print_plan(files)

  if args.download:
    download_assets(files, args.out_dir, args.workers)
  if args.upload:
    upload_assets(files, args.out_dir, args.batch_size)
  if args.rewrite:
    changed = rewrite_content_links(files, args.content_dir)
    print(f"changed markdown files: {changed}")


if __name__ == "__main__":
  main()
