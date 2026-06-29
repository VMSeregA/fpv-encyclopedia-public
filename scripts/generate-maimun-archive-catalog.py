#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = Path("/Users/sergejsavcuk/Desktop/I.P.D/!FPV")
DEFAULT_CONTENT_DIR = ROOT / "content" / "13_База_данных_Маймуна"
ARCHIVE_NAME = "База данных Маймуна"


def human_size(size: int) -> str:
    value = float(size)
    for unit in ["Б", "КБ", "МБ", "ГБ", "ТБ"]:
        if value < 1024 or unit == "ТБ":
            return f"{value:.1f} {unit}" if unit != "Б" else f"{int(value)} {unit}"
        value /= 1024
    return f"{size} Б"


def file_kind(path: Path) -> str:
    suffix = path.suffix.lower().lstrip(".")
    if not suffix:
        return "без расширения"
    return suffix


def slug_page_name(relative_dir: Path) -> str:
    if str(relative_dir) == ".":
        return ARCHIVE_NAME
    return " - ".join(relative_dir.parts)


def frontmatter(title: str, source: str) -> list[str]:
    return [
        "---",
        f"title: {title}",
        "status: каталог",
        "type: база данных",
        "topic: FPV архив",
        "tags:",
        "  - fpv",
        "  - база-данных",
        "  - маймун",
        f"updated: {date.today().isoformat()}",
        f"source: {source}",
        "---",
        "",
    ]


def table_escape(value: str) -> str:
    return value.replace("|", "\\|")


def markdown_escape(value: str) -> str:
    escaped = value.replace("\\", "\\\\")
    for char in ["[", "]", "*", "_", "`", "|"]:
        escaped = escaped.replace(char, f"\\{char}")
    return escaped


def local_file_uri(path: Path) -> str:
    return "file://" + str(path.resolve())


def file_link(path: Path) -> str:
    return f"[{markdown_escape(path.name)}](<{local_file_uri(path)}>)"


def write_page(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_catalog(source: Path, content_dir: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Source archive not found: {source}")
    if not source.is_dir():
        raise NotADirectoryError(f"Source archive is not a directory: {source}")

    files = sorted(path for path in source.rglob("*") if path.is_file())
    dirs = sorted(path for path in source.rglob("*") if path.is_dir())
    total_size = sum(path.stat().st_size for path in files)
    ext_counts = Counter(file_kind(path) for path in files)
    top_counts: dict[str, int] = defaultdict(int)
    top_sizes: dict[str, int] = defaultdict(int)

    for path in files:
        rel = path.relative_to(source)
        top = rel.parts[0] if rel.parts else "корень"
        top_counts[top] += 1
        top_sizes[top] += path.stat().st_size

    index_lines = frontmatter(ARCHIVE_NAME, str(source))
    index_lines.extend(
        [
            f"# {ARCHIVE_NAME}",
            "",
            "> [!warning] Публичная граница",
            "> Это индекс сырого архива `!FPV`, а не публикация всех исходных файлов. PDF, видео, прошивки, STL и архивы остаются в локальном хранилище, пока конкретный материал не отобран и не проверен для публичной энциклопедии.",
            "> Локальные ссылки `file://` открываются на этом Mac и в Obsidian. На публичном сайте браузер может блокировать такие ссылки из-за правил безопасности.",
            "",
            f"Файлов в исходной папке: **{len(files)}**.",
            f"Папок в исходной папке: **{len(dirs) + 1}**.",
            f"Общий размер исходной папки: **{human_size(total_size)}**.",
            "",
            "## Разделы",
            "",
            "| Раздел | Файлов | Размер | Страница |",
            "| --- | ---: | ---: | --- |",
        ]
    )
    for top in sorted(top_counts):
        page = slug_page_name(Path(top))
        index_lines.append(f"| {table_escape(top)} | {top_counts[top]} | {human_size(top_sizes[top])} | [[{page}|Открыть]] |")

    index_lines.extend(["", "## Типы файлов", "", "| Тип | Количество |", "| --- | ---: |"])
    for ext, count in sorted(ext_counts.items(), key=lambda item: (-item[1], item[0])):
        index_lines.append(f"| `{table_escape(ext)}` | {count} |")

    index_lines.extend(
        [
            "",
            "## Полный список файлов",
            "",
            "| Файл | Путь в `!FPV` | Тип | Размер |",
            "| --- | --- | --- | ---: |",
        ]
    )
    for path in files:
        rel = path.relative_to(source)
        parent = str(rel.parent) if str(rel.parent) != "." else "корень"
        index_lines.append(
            f"| {file_link(path)} | `{table_escape(parent)}` | `{file_kind(path)}` | {human_size(path.stat().st_size)} |"
        )

    write_page(content_dir / f"{ARCHIVE_NAME}.md", index_lines)

    by_top: dict[str, list[Path]] = defaultdict(list)
    for path in files:
        rel = path.relative_to(source)
        top = rel.parts[0] if rel.parts else "корень"
        by_top[top].append(path)

    for top, paths in sorted(by_top.items()):
        title = slug_page_name(Path(top))
        lines = frontmatter(title, str(source / top))
        lines.extend(
            [
                f"# {title}",
                "",
                f"Назад: [[{ARCHIVE_NAME}|{ARCHIVE_NAME}]]",
                "",
                f"Файлов: **{len(paths)}**.",
                f"Размер: **{human_size(sum(path.stat().st_size for path in paths))}**.",
                "",
                "## Файлы",
                "",
                "| Файл | Путь внутри раздела | Тип | Размер |",
                "| --- | --- | --- | ---: |",
            ]
        )
        for path in paths:
            rel = path.relative_to(source / top)
            parent = str(rel.parent) if str(rel.parent) != "." else "корень"
            lines.append(f"| {file_link(path)} | `{table_escape(parent)}` | `{file_kind(path)}` | {human_size(path.stat().st_size)} |")
        write_page(content_dir / f"{title}.md", lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate public index pages for the local !FPV archive.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--content-dir", type=Path, default=DEFAULT_CONTENT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_catalog(args.source, args.content_dir)
    print(f"indexed {args.source} into {args.content_dir}")


if __name__ == "__main__":
    main()
