#!/usr/bin/env bash
set -euo pipefail

SOURCE_VAULT="/Users/sergejsavcuk/Desktop/I.P.D"
TARGET_CONTENT="/Users/sergejsavcuk/Documents/fpv-encyclopedia-public/content"

if [[ ! -d "$SOURCE_VAULT" ]]; then
  echo "Source vault not found: $SOURCE_VAULT" >&2
  exit 1
fi

if [[ "$TARGET_CONTENT" != "/Users/sergejsavcuk/Documents/fpv-encyclopedia-public/content" ]]; then
  echo "Refusing to sync to unexpected target: $TARGET_CONTENT" >&2
  exit 1
fi

mkdir -p "$TARGET_CONTENT"
find "$TARGET_CONTENT" -mindepth 1 -maxdepth 1 -exec rm -rf {} +

rsync -a "$SOURCE_VAULT/00_Главная" "$TARGET_CONTENT/"
rsync -a "$SOURCE_VAULT/01_База_знаний" "$TARGET_CONTENT/"
rsync -a "$SOURCE_VAULT/02_Радиоканал" "$TARGET_CONTENT/"
rsync -a "$SOURCE_VAULT/03_Видео_и_VRX" "$TARGET_CONTENT/"
rsync -a "$SOURCE_VAULT/04_Антенны" "$TARGET_CONTENT/"
rsync -a "$SOURCE_VAULT/05_Полетный_контроллер_ESC_моторы" "$TARGET_CONTENT/"
rsync -a "$SOURCE_VAULT/06_Прошивки_и_настройки" "$TARGET_CONTENT/"
rsync -a "$SOURCE_VAULT/07_Питание" "$TARGET_CONTENT/"
rsync -a "$SOURCE_VAULT/08_Сборка_и_пайка" "$TARGET_CONTENT/"
rsync -a "$SOURCE_VAULT/09_Диагностика_и_ремонт" "$TARGET_CONTENT/"
rsync -a "$SOURCE_VAULT/10_Полевой_опыт" "$TARGET_CONTENT/"
rsync -a "$SOURCE_VAULT/11_Каталоги" "$TARGET_CONTENT/"
rsync -a "$SOURCE_VAULT/12_Глоссарий" "$TARGET_CONTENT/"
rsync -a "$SOURCE_VAULT/90_Шаблоны" "$TARGET_CONTENT/"

mkdir -p "$TARGET_CONTENT/99_Материалы"
rsync -a "$SOURCE_VAULT/99_Материалы/README.md" "$TARGET_CONTENT/99_Материалы/README.md"
rsync -a "$SOURCE_VAULT/00_Главная/FPV Энциклопедия.md" "$TARGET_CONTENT/index.md"

python3 - <<'PY'
from pathlib import Path

root = Path("/Users/sergejsavcuk/Documents/fpv-encyclopedia-public/content")

for path in root.rglob("*.md"):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    title = None
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break
    if not title:
        title = path.stem

    if lines[:1] == ["---"]:
        try:
            end = lines[1:].index("---") + 1
        except ValueError:
            continue
        frontmatter = lines[1:end]
        if not any(line.startswith("title:") for line in frontmatter):
            lines.insert(1, f"title: {title}")
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        path.write_text(f"---\ntitle: {title}\n---\n\n{text}", encoding="utf-8")
PY

npx prettier "$TARGET_CONTENT" --write >/dev/null

echo "Public content synced to $TARGET_CONTENT"
