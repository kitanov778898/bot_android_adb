"""
Основной скрипт автоматизации (Hill Climb / Racing Bot).
Версия: 1.1.3

ОГЛАВЛЕНИЕ:
[1] Импорты и настройки
[2] Инициализация и запуск игры
[3] Навигация по меню (UI) с отладкой
[4] Завершение этапа
"""

import time
from pathlib import Path
from adb_tools import (
    run_game, screenshot, draw_tap, 
    click_start_if_found, speak_text, pulse_gas, swipe
)

__version__ = "1.1.3"

# ==============================================================================
# [1] НАСТРОЙКИ И КОНСТАНТЫ
# ==============================================================================

# Определяем корень проекта автоматически (на уровень выше src/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Пути к папкам
ASSETS_DIR = PROJECT_ROOT / "assets"
UI_PATH = ASSETS_DIR / "search_ui_components"
SCREENSHOT_DIR = PROJECT_ROOT / "src" / "screenshot"

# Создаём папку для скриншотов, если её нет
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

# Координаты кнопок (под экран 1920x1200)
GAS_X, GAS_Y = 1670, 1000
BRAKE_X, BRAKE_Y = 250, 1000

# Пути к UI-шаблонам (теперь абсолютные!)
TEMPLATE_APPARAT = UI_PATH / "button_АППАРАТ.png"
TEMPLATE_TUNING = UI_PATH / "button_ТЮНИНГ.png"
TEMPLATE_STAGE = UI_PATH / "button_ЭТАП.png"
TEMPLATE_START_RACE = UI_PATH / "button_СТАРТ.png"

# Путь для отладочного скриншота
DEBUG_APPARAT_PATH = SCREENSHOT_DIR / "found_apparat.png"


# ==============================================================================
# [2] ИНИЦИАЛИЗАЦИЯ И ЗАПУСК
# ==============================================================================

print(f"\n————— 🤖 ЗАПУСК БОТА v{__version__} ———-")

run_game()
print("🚀 Игра запущена. Ожидание загрузки главного меню (5 сек)...")
time.sleep(5)


# ==============================================================================
# [3] НАВИГАЦИЯ И ОТЛАДКА
# ==============================================================================

print(f"\n🔍 Этап 1: Поиск кнопки 'АППАРАТ'...")

# Используем режим отладки: бот НЕ кликает, а только рисует рамку и сохраняет скрин
found_apparat = click_start_if_found(
    template_path=str(TEMPLATE_APPARAT),      # ← str() обязательно для OpenCV
    threshold=0.7,
    debug=True,                                # ← Режим отладки
    debug_path=str(DEBUG_APPARAT_PATH)         # ← Сохраняем сюда
)

if found_apparat:
    print("✅ Кнопка 'АППАРАТ' найдена!")
    print(f"📸 Проверьте файл: {DEBUG_APPARAT_PATH}")
else:
    print("⚠️ Кнопка 'АППАРАТ' не найдена. Проверьте:")
    print("   - Открыто ли нужное меню?")
    print("   - Правильный ли путь к шаблону?")
    print("   - Попробуйте снизить threshold до 0.6")


# ==============================================================================
# [4] ЗАВЕРШЕНИЕ ЭТАПА
# ==============================================================================

print("\n————— ✅ ЭТАП ЗАВЕРШЕН ———-")
print(f"📁 Папка скриншотов: {SCREENSHOT_DIR}")
print("Если рамка на месте — можно убирать debug=True и запускать реальный клик.\n")