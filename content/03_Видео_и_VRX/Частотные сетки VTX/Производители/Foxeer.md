---
title: Foxeer
status: справочник
type: каталог
topic: частотные сетки VTX
tags:
  - fpv
  - vtx
updated: 2026-06-28
---

# Foxeer

Сеток в разделе: **5**.

| Модель                                      | Вариант                           | Диапазон           | Статус                    | Файлы                                                                                                                                                                                                                                                                                            |
| ------------------------------------------- | --------------------------------- | ------------------ | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Reaper / Reaper Extreme 5.8G reference grid | A/B/E/F/R 40CH                    | 5.8 GHz analog     | требует проверки          | [JSON](/static/downloads/vtx-tables/json/foxeer-reaper-58ghz-reference.json) / [CSV](/static/downloads/vtx-tables/csv/foxeer-reaper-58ghz-reference.csv)                                                                                                                                         |
| Reaper Extreme 3W                           | Betaflight 64CH / A-B-E-F-R-H-O-U | 4.9-6.0 GHz analog | официальный источник      | [JSON](/static/downloads/vtx-tables/json/foxeer-reaper-extreme-3w-betaflight-64ch.json) / [CSV](/static/downloads/vtx-tables/csv/foxeer-reaper-extreme-3w-betaflight-64ch.csv) / [Изображение/мануал сетки](https://www.foxeer.com/foxeer-4-9-6g-reaper-extreme-3w-80ch-vtx-g-576)               |
| Reaper Extreme V3 2.5W                      | 80CH / A-B-E-F-R-H-L-U-O-X        | 4.9-6.0 GHz analog | мануал / требует проверки | [JSON](/static/downloads/vtx-tables/json/foxeer-reaper-extreme-v3-25w-80ch.json) / [CSV](/static/downloads/vtx-tables/csv/foxeer-reaper-extreme-v3-25w-80ch.csv) / [Изображение/мануал сетки](https://device.report/manuals/foxeer-reaper-extreme-v3-2-5w-80ch-vtx-manual-specs-frequency-table) |
| Reaper Infinity V2 5W                       | 80CH / A-B-E-F-R-H-L-U-O-X        | 4.9-6.0 GHz analog | официальный источник      | [JSON](/static/downloads/vtx-tables/json/foxeer-reaper-infinity-v2-5w-80ch.json) / [CSV](/static/downloads/vtx-tables/csv/foxeer-reaper-infinity-v2-5w-80ch.csv) / [Изображение/мануал сетки](https://www.foxeer.com/foxeer-4-9g-6g-reaper-infinity-v2-5w-80ch-vtx-g-588)                        |
| Reaper Nano V2 5.8G 350mW                   | visible 5-band table              | 5.8 GHz analog     | официальный источник      | [JSON](/static/downloads/vtx-tables/json/foxeer-reaper-nano-v2-58g-5band-reference.json) / [CSV](/static/downloads/vtx-tables/csv/foxeer-reaper-nano-v2-58g-5band-reference.csv) / [Изображение/мануал сетки](https://www.foxeer.com/foxeer-reaper-nano-v2-vtx-5-8g-72ch-350mw-tramp-g-583)      |

## Reaper / Reaper Extreme 5.8G reference grid

- Вариант: **A/B/E/F/R 40CH**
- Диапазон: **5.8 GHz analog**
- Статус: **требует проверки**
- Протокол/формат: **Analog FPV frequency grid**
- Источник: [Foxeer Reaper Extreme manual page](https://manuals.plus/foxeer/vtx-reaper-extreme-manual)
- Примечание: Добавлено как Foxeer-совместимая 5.8G сетка; сверять с наклейкой/мануалом конкретной версии перед прошивкой.

| Сетка    | Буква |  CH1 |  CH2 |  CH3 |  CH4 |  CH5 |  CH6 |  CH7 |  CH8 |
| -------- | ----- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BOSCAM_A | A     | 5865 | 5845 | 5825 | 5805 | 5785 | 5765 | 5745 | 5725 |
| BOSCAM_B | B     | 5733 | 5752 | 5771 | 5790 | 5809 | 5828 | 5847 | 5866 |
| BOSCAM_E | E     | 5705 | 5685 | 5665 | 5645 | 5885 | 5905 | 5925 | 5945 |
| FATSHARK | F     | 5740 | 5760 | 5780 | 5800 | 5820 | 5840 | 5860 | 5880 |
| RACEBAND | R     | 5658 | 5695 | 5732 | 5769 | 5806 | 5843 | 5880 | 5917 |

## Reaper Extreme 3W

- Вариант: **Betaflight 64CH / A-B-E-F-R-H-O-U**
- Диапазон: **4.9-6.0 GHz analog**
- Статус: **официальный источник**
- Протокол/формат: **IRC Tramp / Betaflight VTX table**
- Источник: [Foxeer Reaper Extreme 3W product page](https://www.foxeer.com/foxeer-4-9-6g-reaper-extreme-3w-80ch-vtx-g-576)
- Изображение/мануал сетки: [открыть источник](https://www.foxeer.com/foxeer-4-9-6g-reaper-extreme-3w-80ch-vtx-g-576)
- Уровни мощности: 25, 200, 500, 1.5W, 3W
- Примечание: Добавлено из публичной страницы/мануала Foxeer; перед записью сверять с конкретной ревизией VTX и региональными ограничениями.
- Примечание: Betaflight принимает максимум 64 канала, поэтому эта запись сохранена как 8-band вариант A/B/E/F/R/H/O/U из указания производителя.

| Сетка    | Буква |  CH1 |  CH2 |  CH3 |  CH4 |  CH5 |  CH6 |  CH7 |  CH8 |
| -------- | ----- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BOSCAM_A | A     | 5865 | 5845 | 5825 | 5805 | 5785 | 5765 | 5745 | 5725 |
| BOSCAM_B | B     | 5733 | 5752 | 5771 | 5790 | 5809 | 5828 | 5847 | 5866 |
| BOSCAM_E | E     | 5705 | 5685 | 5665 | 5645 | 5885 | 5905 | 5925 | 5945 |
| FATSHARK | F     | 5740 | 5760 | 5780 | 5800 | 5820 | 5840 | 5860 | 5880 |
| RACEBAND | R     | 5658 | 5695 | 5732 | 5769 | 5806 | 5843 | 5880 | 5917 |
| BAND_H   | H     | 5653 | 5693 | 5733 | 5773 | 5813 | 5853 | 5893 | 5933 |
| BAND_O   | O     | 5474 | 5492 | 5510 | 5528 | 5546 | 5564 | 5582 | 5600 |
| BAND_U   | U     | 5325 | 5348 | 5366 | 5384 | 5402 | 5420 | 5438 | 5456 |

## Reaper Extreme V3 2.5W

- Вариант: **80CH / A-B-E-F-R-H-L-U-O-X**
- Диапазон: **4.9-6.0 GHz analog**
- Статус: **мануал / требует проверки**
- Протокол/формат: **IRC Tramp / Betaflight VTX table**
- Источник: [Foxeer Reaper Extreme V3 2.5W 80CH manual page](https://device.report/manuals/foxeer-reaper-extreme-v3-2-5w-80ch-vtx-manual-specs-frequency-table)
- Изображение/мануал сетки: [открыть источник](https://device.report/manuals/foxeer-reaper-extreme-v3-2-5w-80ch-vtx-manual-specs-frequency-table)
- Уровни мощности: 25, 200, 500, 1.5W, 2.5W
- Примечание: Добавлено из публичной страницы/мануала Foxeer; перед записью сверять с конкретной ревизией VTX и региональными ограничениями.
- Примечание: Мануал указывает unlock частот и мощности; перед использованием high power проверить охлаждение и питание.

| Сетка    | Буква |  CH1 |  CH2 |  CH3 |  CH4 |  CH5 |  CH6 |  CH7 |  CH8 |
| -------- | ----- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BOSCAM_A | A     | 5865 | 5845 | 5825 | 5805 | 5785 | 5765 | 5745 | 5725 |
| BOSCAM_B | B     | 5733 | 5752 | 5771 | 5790 | 5809 | 5828 | 5847 | 5866 |
| BOSCAM_E | E     | 5705 | 5685 | 5665 | 5645 | 5885 | 5905 | 5925 | 5945 |
| FATSHARK | F     | 5740 | 5760 | 5780 | 5800 | 5820 | 5840 | 5860 | 5880 |
| RACEBAND | R     | 5658 | 5695 | 5732 | 5769 | 5806 | 5843 | 5880 | 5917 |
| BAND_H   | H     | 5653 | 5693 | 5733 | 5773 | 5813 | 5853 | 5893 | 5933 |
| BAND_L   | L     | 5333 | 5373 | 5413 | 5453 | 5493 | 5533 | 5573 | 5613 |
| BAND_U   | U     | 5325 | 5348 | 5366 | 5384 | 5402 | 5420 | 5438 | 5456 |
| BAND_O   | O     | 5474 | 5492 | 5510 | 5528 | 5546 | 5564 | 5582 | 5600 |
| BAND_X   | X     | 4990 | 5020 | 5050 | 5080 | 5110 | 5140 | 5170 | 5200 |

## Reaper Infinity V2 5W

- Вариант: **80CH / A-B-E-F-R-H-L-U-O-X**
- Диапазон: **4.9-6.0 GHz analog**
- Статус: **официальный источник**
- Протокол/формат: **IRC Tramp / Betaflight VTX table**
- Источник: [Foxeer Reaper Infinity V2 5W product page](https://www.foxeer.com/foxeer-4-9g-6g-reaper-infinity-v2-5w-80ch-vtx-g-588)
- Изображение/мануал сетки: [открыть источник](https://www.foxeer.com/foxeer-4-9g-6g-reaper-infinity-v2-5w-80ch-vtx-g-588)
- Уровни мощности: 1W, 2W, 3W, 4W, 5W
- Примечание: Добавлено из публичной страницы/мануала Foxeer; перед записью сверять с конкретной ревизией VTX и региональными ограничениями.
- Примечание: Это широкополосная 4.9-6.0G таблица; убедитесь, что VRX и региональные правила допускают выбранный диапазон.

| Сетка    | Буква |  CH1 |  CH2 |  CH3 |  CH4 |  CH5 |  CH6 |  CH7 |  CH8 |
| -------- | ----- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BOSCAM_A | A     | 5865 | 5845 | 5825 | 5805 | 5785 | 5765 | 5745 | 5725 |
| BOSCAM_B | B     | 5733 | 5752 | 5771 | 5790 | 5809 | 5828 | 5847 | 5866 |
| BOSCAM_E | E     | 5705 | 5685 | 5665 | 5645 | 5885 | 5905 | 5925 | 5945 |
| FATSHARK | F     | 5740 | 5760 | 5780 | 5800 | 5820 | 5840 | 5860 | 5880 |
| RACEBAND | R     | 5658 | 5695 | 5732 | 5769 | 5806 | 5843 | 5880 | 5917 |
| BAND_H   | H     | 5653 | 5693 | 5733 | 5773 | 5813 | 5853 | 5893 | 5933 |
| BAND_L   | L     | 5333 | 5373 | 5413 | 5453 | 5493 | 5533 | 5573 | 5613 |
| BAND_U   | U     | 5325 | 5348 | 5366 | 5384 | 5402 | 5420 | 5438 | 5456 |
| BAND_O   | O     | 5474 | 5492 | 5510 | 5528 | 5546 | 5564 | 5582 | 5600 |
| BAND_X   | X     | 4990 | 5020 | 5050 | 5080 | 5110 | 5140 | 5170 | 5200 |

## Reaper Nano V2 5.8G 350mW

- Вариант: **visible 5-band table**
- Диапазон: **5.8 GHz analog**
- Статус: **официальный источник**
- Протокол/формат: **IRC Tramp / Betaflight VTX table**
- Источник: [Foxeer Reaper Nano V2 product page](https://www.foxeer.com/foxeer-reaper-nano-v2-vtx-5-8g-72ch-350mw-tramp-g-583)
- Изображение/мануал сетки: [открыть источник](https://www.foxeer.com/foxeer-reaper-nano-v2-vtx-5-8g-72ch-350mw-tramp-g-583)
- Уровни мощности: 25, 100, 200, 350
- Примечание: Добавлено из публичной страницы/мануала Foxeer; перед записью сверять с конкретной ревизией VTX и региональными ограничениями.
- Примечание: Страница продукта указывает 72CH, но в видимой таблице источника сохранены A/B/E/F/R; дополнительные bands требуют сверки по файлу/мануалу конкретной ревизии.

| Сетка    | Буква |  CH1 |  CH2 |  CH3 |  CH4 |  CH5 |  CH6 |  CH7 |  CH8 |
| -------- | ----- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BOSCAM_A | A     | 5865 | 5845 | 5825 | 5805 | 5785 | 5765 | 5745 | 5725 |
| BOSCAM_B | B     | 5733 | 5752 | 5771 | 5790 | 5809 | 5828 | 5847 | 5866 |
| BOSCAM_E | E     | 5705 | 5685 | 5665 | 5645 | 5885 | 5905 | 5925 | 5945 |
| FATSHARK | F     | 5740 | 5760 | 5780 | 5800 | 5820 | 5840 | 5860 | 5880 |
| RACEBAND | R     | 5658 | 5695 | 5732 | 5769 | 5806 | 5843 | 5880 | 5917 |
