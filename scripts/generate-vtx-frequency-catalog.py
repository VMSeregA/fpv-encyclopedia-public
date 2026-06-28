#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "vtx-frequency-tables.json"
DEFAULT_CONTENT_DIR = ROOT / "content" / "03_Видео_и_VRX" / "Частотные сетки VTX"
DEFAULT_STATIC_DIR = ROOT / "quartz" / "static" / "downloads" / "vtx-tables"
DOWNLOAD_BASE = "/static/downloads/vtx-tables"


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = value.replace("+", "plus")
    value = re.sub(r"[^a-z0-9а-яё-]+", "-", value, flags=re.IGNORECASE)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "table"


def page_name(value: str) -> str:
    return value.replace("/", " ").replace("\\", " ").strip()


def load_payload() -> dict[str, Any]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing data file: {DATA_PATH}")
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def validate_table(table: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    table_id = table.get("id", "<missing>")
    if not table.get("manufacturer"):
        errors.append(f"{table_id}: missing manufacturer")
    if not table.get("model"):
        errors.append(f"{table_id}: missing model")
    if not table.get("source_url"):
        errors.append(f"{table_id}: missing source_url")

    if table.get("range_only"):
        ranges = table.get("ranges_mhz") or []
        if not ranges:
            errors.append(f"{table_id}: range table has no ranges_mhz")
        for item in ranges:
            start = item.get("start")
            end = item.get("end")
            if not isinstance(start, int) or not isinstance(end, int) or start >= end:
                errors.append(f"{table_id}: invalid range {item}")
        return errors

    bands = table.get("bands") or []
    if not bands:
        errors.append(f"{table_id}: frequency table has no bands")
        return errors

    for band in bands:
        frequencies = band.get("frequencies") or []
        if not band.get("letter"):
            errors.append(f"{table_id}: band {band.get('name', '<unnamed>')} has no letter")
        if not frequencies:
            errors.append(f"{table_id}: band {band.get('letter', '<missing>')} has no frequencies")
        for frequency in frequencies:
            if not isinstance(frequency, int):
                errors.append(f"{table_id}: non-integer frequency {frequency!r}")
            elif frequency != 0 and not 1000 <= frequency <= 8000:
                errors.append(f"{table_id}: suspicious frequency {frequency}")
    return errors


def validate_payload(payload: dict[str, Any]) -> None:
    tables = payload.get("tables") or []
    ids = [table.get("id") for table in tables]
    errors: list[str] = []
    duplicate_ids = sorted({table_id for table_id in ids if ids.count(table_id) > 1})
    if duplicate_ids:
        errors.append(f"duplicate table ids: {', '.join(duplicate_ids)}")
    for table in tables:
        errors.extend(validate_table(table))
    if errors:
        raise ValueError("\n".join(errors))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def format_generated_files(paths: list[Path]) -> None:
    if not paths:
        return
    result = subprocess.run(
        ["npx", "prettier", "--write", *[str(path) for path in paths]],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr + result.stdout)


def write_table_csv(path: Path, table: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["band", "letter", "channel", "frequency_mhz"], lineterminator="\n")
        writer.writeheader()
        for band in table.get("bands", []):
            for index, frequency in enumerate(band.get("frequencies", []), start=1):
                writer.writerow(
                    {
                        "band": band.get("name", ""),
                        "letter": band.get("letter", ""),
                        "channel": index,
                        "frequency_mhz": frequency,
                    }
                )


def write_range_csv(path: Path, table: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["range", "start_mhz", "end_mhz", "note"], lineterminator="\n")
        writer.writeheader()
        for item in table.get("ranges_mhz", []):
            writer.writerow(
                {
                    "range": item.get("name", ""),
                    "start_mhz": item.get("start", ""),
                    "end_mhz": item.get("end", ""),
                    "note": item.get("note", ""),
                }
            )


def channel_table_markdown(table: dict[str, Any]) -> str:
    if table.get("range_only"):
        lines = ["| Диапазон | От, MHz | До, MHz | Примечание |", "| --- | ---: | ---: | --- |"]
        for item in table.get("ranges_mhz", []):
            lines.append(
                f"| {item.get('name', '')} | {item.get('start', '')} | {item.get('end', '')} | {item.get('note', '')} |"
            )
        return "\n".join(lines)

    max_channels = max(len(band.get("frequencies", [])) for band in table.get("bands", []))
    header = ["Сетка", "Буква"] + [f"CH{i}" for i in range(1, max_channels + 1)]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---", "---"] + ["---:"] * max_channels) + " |",
    ]
    for band in table.get("bands", []):
        freqs = [str(freq) if freq else "0" for freq in band.get("frequencies", [])]
        freqs += [""] * (max_channels - len(freqs))
        lines.append(f"| {band.get('name', '')} | {band.get('letter', '')} | " + " | ".join(freqs) + " |")
    return "\n".join(lines)


def table_summary_row(table: dict[str, Any]) -> str:
    table_id = table["id"]
    link = f"{DOWNLOAD_BASE}/json/{table_id}.json"
    csv_link = f"{DOWNLOAD_BASE}/csv/{table_id}.csv"
    variant = table.get("variant") or "-"
    status = table.get("status") or "-"
    family = table.get("band_family") or "-"
    return (
        f"| {table.get('model', '')} | {variant} | {family} | {status} | "
        f"[JSON]({link}) / [CSV]({csv_link}) |"
    )


def index_summary_row(manufacturer: str, table: dict[str, Any]) -> str:
    table_id = table["id"]
    link = f"{DOWNLOAD_BASE}/json/{table_id}.json"
    csv_link = f"{DOWNLOAD_BASE}/csv/{table_id}.csv"
    variant = table.get("variant") or "-"
    status = table.get("status") or "-"
    family = table.get("band_family") or "-"
    return (
        f"| {manufacturer} | {table.get('model', '')} | {variant} | {family} | {status} | "
        f"[JSON]({link}) / [CSV]({csv_link}) |"
    )


def render_index(payload: dict[str, Any], tables_by_manufacturer: dict[str, list[dict[str, Any]]]) -> str:
    updated = payload.get("updated", "")
    table_count = sum(len(items) for items in tables_by_manufacturer.values())
    lines = [
        "---",
        "title: Частотные сетки VTX",
        "status: справочник",
        "type: каталог",
        "topic: видео и VRX",
        "tags:",
        "  - fpv",
        "  - video",
        "  - vtx",
        "  - vrx",
        "  - частоты",
        f"updated: {updated}",
        "source: нормализованный публичный каталог",
        "---",
        "",
        "# Частотные сетки VTX",
        "",
        "> [!warning] Проверка перед применением",
        "> Частоты и мощность передатчиков зависят от региона, прошивки и разблокировки устройства. Перед записью в контроллер сверяйте сетку с маркировкой конкретного VTX и требованиями вашего диапазона.",
        "",
        f"В каталоге: **{table_count}** сеток и диапазонов. Скачать общий манифест: [manifest.json]({DOWNLOAD_BASE}/manifest.json).",
        "",
        "## Производители",
        "",
    ]
    for manufacturer in sorted(tables_by_manufacturer):
        count = len(tables_by_manufacturer[manufacturer])
        lines.append(f"- [[Производители/{page_name(manufacturer)}|{manufacturer}]] — {count}")

    lines.extend(
        [
            "",
            "## Полная таблица",
            "",
            "| Производитель | Модель | Вариант | Диапазон | Статус | Файлы |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for manufacturer in sorted(tables_by_manufacturer):
        for table in sorted(tables_by_manufacturer[manufacturer], key=lambda item: item["model"]):
            lines.append(index_summary_row(manufacturer, table))
    lines.extend(
        [
            "",
            "## Источники",
            "",
        ]
    )
    for source in payload.get("sources", []):
        lines.append(f"- [{source['title']}]({source['url']}) — {source.get('note', '')}")
    lines.append("")
    return "\n".join(lines)


def render_manufacturer_page(manufacturer: str, tables: list[dict[str, Any]], updated: str) -> str:
    lines = [
        "---",
        f"title: {manufacturer}",
        "status: справочник",
        "type: каталог",
        "topic: частотные сетки VTX",
        "tags:",
        "  - fpv",
        "  - vtx",
        f"updated: {updated}",
        "---",
        "",
        f"# {manufacturer}",
        "",
        f"Сеток в разделе: **{len(tables)}**.",
        "",
        "| Модель | Вариант | Диапазон | Статус | Файлы |",
        "| --- | --- | --- | --- | --- |",
    ]
    for table in sorted(tables, key=lambda item: item["model"]):
        lines.append(table_summary_row(table))

    for table in sorted(tables, key=lambda item: item["model"]):
        notes = table.get("notes") or []
        powers = ", ".join(level.get("label", "") for level in table.get("powerlevels", []) if level.get("label"))
        lines.extend(
            [
                "",
                f"## {table.get('model', '')}",
                "",
                f"- Вариант: **{table.get('variant') or '-'}**",
                f"- Диапазон: **{table.get('band_family') or '-'}**",
                f"- Статус: **{table.get('status') or '-'}**",
                f"- Протокол/формат: **{table.get('protocol') or '-'}**",
                f"- Источник: [{table.get('source_title') or table.get('source_url')}]({table.get('source_url')})",
            ]
        )
        if powers:
            lines.append(f"- Уровни мощности: {powers}")
        for note in notes:
            lines.append(f"- Примечание: {note}")
        lines.extend(["", channel_table_markdown(table)])
    lines.append("")
    return "\n".join(lines)


def write_outputs(content_dir: Path, static_dir: Path, payload: dict[str, Any]) -> None:
    validate_payload(payload)

    tables = payload["tables"]
    tables_by_manufacturer: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for table in tables:
        tables_by_manufacturer[table["manufacturer"]].append(table)

    static_dir.mkdir(parents=True, exist_ok=True)
    (static_dir / "json").mkdir(parents=True, exist_ok=True)
    (static_dir / "csv").mkdir(parents=True, exist_ok=True)

    manifest_tables = []
    generated_files: list[Path] = []
    for table in tables:
        table_id = table["id"]
        json_path = static_dir / "json" / f"{table_id}.json"
        write_json(json_path, table)
        generated_files.append(json_path)
        if table.get("range_only"):
            write_range_csv(static_dir / "csv" / f"{table_id}.csv", table)
        else:
            write_table_csv(static_dir / "csv" / f"{table_id}.csv", table)
        manifest_tables.append(
            {
                "id": table_id,
                "manufacturer": table["manufacturer"],
                "model": table["model"],
                "variant": table.get("variant"),
                "band_family": table.get("band_family"),
                "status": table.get("status"),
                "json": f"{DOWNLOAD_BASE}/json/{table_id}.json",
                "csv": f"{DOWNLOAD_BASE}/csv/{table_id}.csv",
                "source_url": table.get("source_url"),
            }
        )

    write_json(
        static_dir / "manifest.json",
        {
            "updated": payload.get("updated"),
            "table_count": len(tables),
            "manufacturers": sorted(tables_by_manufacturer),
            "tables": sorted(manifest_tables, key=lambda item: (item["manufacturer"], item["model"], item["id"])),
            "sources": payload.get("sources", []),
        },
    )
    generated_files.append(static_dir / "manifest.json")

    content_dir.mkdir(parents=True, exist_ok=True)
    (content_dir / "Производители").mkdir(parents=True, exist_ok=True)
    index_path = content_dir / "Частотные сетки VTX.md"
    index_path.write_text(render_index(payload, tables_by_manufacturer), encoding="utf-8")
    generated_files.append(index_path)
    for manufacturer, manufacturer_tables in tables_by_manufacturer.items():
        manufacturer_path = content_dir / "Производители" / f"{page_name(manufacturer)}.md"
        manufacturer_path.write_text(
            render_manufacturer_page(manufacturer, manufacturer_tables, payload.get("updated", "")),
            encoding="utf-8",
        )
        generated_files.append(manufacturer_path)
    format_generated_files(generated_files)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the public VTX frequency table catalog.")
    parser.add_argument("--content-dir", type=Path, default=DEFAULT_CONTENT_DIR)
    parser.add_argument("--static-dir", type=Path, default=DEFAULT_STATIC_DIR)
    parser.add_argument("--validate", action="store_true", help="Validate data only.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = load_payload()
    validate_payload(payload)
    if not args.validate:
        write_outputs(args.content_dir, args.static_dir, payload)
    print(f"validated {len(payload.get('tables', []))} VTX frequency tables")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
