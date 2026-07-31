#!/usr/bin/env python3

import argparse
import hashlib
import shutil
import zipfile
from collections import defaultdict
from pathlib import Path, PurePosixPath
from urllib.parse import quote


DOWNLOAD_BASE_URL = "https://app.gorizontvverh.ru/downloads/RED5"
SERVER_PATH = "/var/www/uav-downloads/RED5"
WIKI_BASE = "06_Прошивки_и_настройки/Прошивки ELRS/RED5"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the RED5 firmware catalog")
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--updated", required=True)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def human_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.2f} {unit}"
        value /= 1024
    raise AssertionError("unreachable")


def file_count_text(count: int) -> str:
    remainder = count % 100
    if 11 <= remainder <= 14:
        word = "файлов"
    elif count % 10 == 1:
        word = "файл"
    elif 2 <= count % 10 <= 4:
        word = "файла"
    else:
        word = "файлов"
    return f"{count} {word}"


def markdown_text(value: str) -> str:
    return value.replace("|", "\\|")


def encoded_url(path: PurePosixPath) -> str:
    suffix = "/".join(quote(part, safe="") for part in path.parts)
    return f"{DOWNLOAD_BASE_URL}/{suffix}" if suffix else f"{DOWNLOAD_BASE_URL}/"


def wiki_link(path: PurePosixPath, label: str) -> str:
    suffix = "/".join(path.parts)
    target = f"{WIKI_BASE}/{suffix}/Индекс" if suffix else f"{WIKI_BASE}/Индекс"
    return f"[[{target}|{label}]]"


def frontmatter(title: str, updated: str, archive_sha256: str, source_path: str | None = None) -> str:
    source_line = f'\nsource_path: "{source_path}"' if source_path is not None else ""
    return f'''---
title: "{title}"
status: черновик
type: каталог
topic: RED5
tags:
  - fpv
  - elrs
  - expresslrs
  - прошивки
  - red5
verified: файлы загружены на Timeweb и проверены прямыми HTTPS-ссылками
updated: {updated}
source: "локальный архив RED5.zip"
server_path: "{SERVER_PATH}"
download_base: "{DOWNLOAD_BASE_URL}/"
source_sha256: "{archive_sha256}"{source_line}
---
'''


def load_files(archive: Path) -> list[tuple[PurePosixPath, int]]:
    with zipfile.ZipFile(archive) as zip_file:
        entries = [info for info in zip_file.infolist() if not info.is_dir()]

    files: list[tuple[PurePosixPath, int]] = []
    for entry in entries:
        path = PurePosixPath(entry.filename)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"Unsafe archive path: {entry.filename}")
        if path.parts and path.parts[0] == "RED5":
            path = PurePosixPath(*path.parts[1:])
        if not path.parts:
            continue
        files.append((path, entry.file_size))

    return sorted(files, key=lambda item: tuple(part.casefold() for part in item[0].parts))


def directory_paths(files: list[tuple[PurePosixPath, int]]) -> list[PurePosixPath]:
    directories = {PurePosixPath()}
    for path, _ in files:
        parent = path.parent
        while parent != PurePosixPath("."):
            directories.add(parent)
            parent = parent.parent
    return sorted(directories, key=lambda path: (len(path.parts), tuple(part.casefold() for part in path.parts)))


def descendants(files: list[tuple[PurePosixPath, int]], directory: PurePosixPath) -> list[tuple[PurePosixPath, int]]:
    prefix = directory.parts
    return [item for item in files if item[0].parts[: len(prefix)] == prefix]


def direct_files(files: list[tuple[PurePosixPath, int]], directory: PurePosixPath) -> list[tuple[PurePosixPath, int]]:
    return [item for item in files if item[0].parent == (directory if directory.parts else PurePosixPath("."))]


def direct_directories(directories: list[PurePosixPath], directory: PurePosixPath) -> list[PurePosixPath]:
    expected_depth = len(directory.parts) + 1
    return [path for path in directories if len(path.parts) == expected_depth and path.parent == (directory if directory.parts else PurePosixPath("."))]


def write_directory_index(
    output: Path,
    directory: PurePosixPath,
    directories: list[PurePosixPath],
    files: list[tuple[PurePosixPath, int]],
    updated: str,
    archive_sha256: str,
) -> None:
    title = "RED5" if not directory.parts else directory.name
    page_dir = output.joinpath(*directory.parts)
    page_dir.mkdir(parents=True, exist_ok=True)
    source_path = "/" if not directory.parts else f"/{directory.as_posix()}"
    lines = [
        frontmatter(f"Индекс: {title}", updated, archive_sha256, source_path),
        f"# Индекс: {title}\n",
        f"Источник: `{source_path}` в локальном архиве `RED5.zip`. Сервер: [{encoded_url(directory)}]({encoded_url(directory)})\n",
        "> [!warning] Не прошивка\n> Эта заметка является индексом. Имена файлов ниже ведут напрямую на сервер Timeweb. Перед прошивкой проверь target, диапазон и ветку RC5/RC6.\n",
        f"Главная страница: [[{WIKI_BASE}/RED5|RED5]]\n",
        f"Полный список: [[{WIKI_BASE}/Манифест файлов|Манифест файлов RED5]]\n",
    ]

    if directory.parts:
        parent = PurePosixPath(*directory.parts[:-1])
        parent_label = "RED5" if not parent.parts else parent.name
        lines.append(f"Родительская папка: {wiki_link(parent, parent_label)}\n")

    child_directories = direct_directories(directories, directory)
    if child_directories:
        lines.append("## Папки\n")
        for child in child_directories:
            child_files = descendants(files, child)
            child_size = sum(size for _, size in child_files)
            lines.append(
                f"- {wiki_link(child, child.name)} - {file_count_text(len(child_files))}, {human_size(child_size)};"
            )
        lines.append("")

    local_files = direct_files(files, directory)
    lines.append("## Файлы\n")
    if not local_files:
        lines.append("В этой папке нет файлов на верхнем уровне. Открой вложенную папку выше.\n")
    else:
        lines.extend(["| Файл | Размер | Путь |", "| --- | ---: | --- |"])
        for path, size in local_files:
            lines.append(
                f"| [{markdown_text(path.name)}]({encoded_url(path)}) | {human_size(size)} | `{markdown_text(path.as_posix())}` |"
            )
        lines.append("")

    (page_dir / "Индекс.md").write_text("\n".join(lines), encoding="utf-8")


def write_manifest(
    output: Path,
    files: list[tuple[PurePosixPath, int]],
    updated: str,
    archive_sha256: str,
) -> None:
    lines = [
        frontmatter("Манифест файлов RED5", updated, archive_sha256),
        "# Манифест файлов RED5\n",
        "Источник: локальный архив `RED5.zip`.\n",
        f"Главная страница: [[{WIKI_BASE}/RED5|RED5]]\n",
        f"Индекс архива: [[{WIKI_BASE}/Индекс|Индекс RED5]]\n",
        "> [!tip] Прямое скачивание\n> Каждый путь кликабелен и ведет напрямую на соответствующий файл в `/downloads/RED5/` на сервере Timeweb.\n",
        "| № | Файл | Размер |",
        "| ---: | --- | ---: |",
    ]
    for index, (path, size) in enumerate(files, start=1):
        lines.append(
            f"| {index} | [`/{markdown_text(path.as_posix())}`]({encoded_url(path)}) | {human_size(size)} |"
        )
    lines.append("")
    (output / "Манифест файлов.md").write_text("\n".join(lines), encoding="utf-8")


def write_main_page(
    output: Path,
    archive: Path,
    files: list[tuple[PurePosixPath, int]],
    directories: list[PurePosixPath],
    updated: str,
    archive_sha256: str,
) -> None:
    total_size = sum(size for _, size in files)
    top_level_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for path, size in files:
        top_level_counts[path.parts[0]][0] += 1
        top_level_counts[path.parts[0]][1] += size

    lines = [
        frontmatter("RED5", updated, archive_sha256),
        "# RED5\n",
        "> [!info] Что это\n> Архив прошивок RED5 для ELRS-совместимых TX/RX targets. Внутри находятся отдельные наборы RC5 и RC6.\n",
        "> [!warning] Важно\n> Не прошивай файл только по похожему названию. Проверь точный target, тип радиочипа, частотный диапазон и нужную ветку RC5/RC6. Ошибка target может потребовать восстановления через UART.\n",
        "> [!tip] Скачивание\n> Можно скачать исходный ZIP целиком либо открыть индексы и скачать отдельный конечный файл напрямую с Timeweb.\n",
        "## Скачать архив\n",
        f"[Скачать RED5.zip ({human_size(archive.stat().st_size)})]({DOWNLOAD_BASE_URL}/RED5.zip)\n",
        "## Сводка\n",
        f"- файлов в архиве: {file_count_text(len(files))};",
        f"- папок: {len(directories) - 1};",
        f"- размер файлов после распаковки: {human_size(total_size)};",
        f"- размер исходного ZIP: {human_size(archive.stat().st_size)};",
        f"- серверный каталог: `{SERVER_PATH}`;",
        f"- SHA-256 исходного архива: `{archive_sha256}`.\n",
        "## Разделы\n",
        "| Раздел | Файлов | Размер |",
        "| --- | ---: | ---: |",
    ]
    for name in sorted(top_level_counts, key=str.casefold):
        count, size = top_level_counts[name]
        if PurePosixPath(name) in directories:
            label = f"[{markdown_text(name)}](./{quote(name, safe='')}/Индекс.md)"
        else:
            path = next(path for path, _ in files if path.parts[0] == name)
            label = f"[{markdown_text(name)}]({encoded_url(path)})"
        lines.append(f"| {label} | {count} | {human_size(size)} |")

    lines.extend(
        [
            "",
            "## Навигация\n",
            f"- [[{WIKI_BASE}/Индекс|Индекс архива RED5]];",
            f"- [[{WIKI_BASE}/Манифест файлов|Полный манифест файлов RED5]];",
            "- [[06_Прошивки_и_настройки/Прошивки ELRS/Прошивки ELRS|Прошивки ELRS]].\n",
            "## Как пользоваться\n",
            "- выбери ветку `RC5` или `RC6`;",
            "- затем выбери тип устройства: `RX`, `RXasTX` или `TX`;",
            "- открой папку радиочипа и нажми на точное имя target;",
            "- перед прошивкой ещё раз сверь устройство, диапазон и имя файла.",
            "",
        ]
    )
    (output / "RED5.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    archive = args.archive.resolve()
    output = args.output.resolve()
    archive_sha256 = sha256_file(archive)
    files = load_files(archive)
    directories = directory_paths(files)

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    for directory in directories:
        write_directory_index(
            output, directory, directories, files, args.updated, archive_sha256
        )
    write_manifest(output, files, args.updated, archive_sha256)
    write_main_page(
        output,
        archive,
        files,
        directories,
        args.updated,
        archive_sha256,
    )
    print(
        f"Создан каталог RED5: {file_count_text(len(files))}, "
        f"{len(directories) - 1} папок"
    )


if __name__ == "__main__":
    main()
