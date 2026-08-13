# FPV Энциклопедия

Публичная версия FPV-базы знаний из Obsidian, собранная через Quartz.

## Что публикуется

В сайт попадает только публичный слой из vault `I.P.D`:

- `00_Главная`
- `01_База_знаний`
- `02_Радиоканал`
- `03_Видео_и_VRX`
- `04_Антенны`
- `05_Полетный_контроллер_ESC_моторы`
- `06_Прошивки_и_настройки`
- `07_Питание`
- `08_Сборка_и_пайка`
- `09_Диагностика_и_ремонт`
- `10_Полевой_опыт`
- `11_Каталоги`
- `12_Глоссарий`
- `90_Шаблоны`
- `99_Материалы/README.md`

Папка `!FPV`, исходные PDF, видео, прошивки, `.obsidian`, `.copilot` и личные материалы не копируются автоматически.

## Локальная работа

```bash
npm i
npm run sync-content
npx quartz build
npx quartz build --serve
```

Локальный сайт после `--serve` обычно открывается на `http://localhost:8080`.

## Тесты и проверки

Каталоги (Maimun-архив, частотные таблицы VTX) покрыты Python-тестами:

```bash
python3 -m unittest discover -s tests
```

Проверка типов и форматирования:

```bash
npm run check
```

## Публикация на GitHub Pages

1. Создать пустой публичный GitHub-репозиторий `VMSeregA/fpv-encyclopedia-public`.
2. В настройках репозитория открыть `Settings` -> `Pages`.
3. В `Build and deployment` выбрать `Source: GitHub Actions`.
4. Добавить remote:

```bash
git remote add origin git@github.com:VMSeregA/fpv-encyclopedia-public.git
```

5. Отправить ветку:

```bash
git push -u origin v5
```

После успешного GitHub Actions workflow сайт будет доступен по адресу:

```text
https://VMSeregA.github.io/fpv-encyclopedia-public
```
