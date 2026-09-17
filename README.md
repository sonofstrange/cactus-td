# Cactus Tower Defense

Tower Defense игра на Python/Pygame с поддержкой Windows и Android.

## Скачать
Готовые сборки (.exe и .apk) доступны во вкладке [Releases](https://github.com/sonofstrange/cactus-td/releases).

## Запуск из исходников
Требуется Python 3.10+ и библиотеки:
`ash
pip install pygame-ce numpy
python main.py
`

## Сборка
- **Windows (exe)**:
  `ash
  pyinstaller CactusTD_Remastered.spec
  `
- **Android (apk)**:
  `ash
  buildozer android debug
  `

## Управление
- **Мышь / Тачскрин** — выбор и установка башен, навигация по меню.
- **Цифры 1–6** — быстрый выбор башни в бою.
- **Пробел** — переключение скорости (1x–5x).
- **U** — режим улучшения башен.
- **Esc** — пауза и бестиарий.
