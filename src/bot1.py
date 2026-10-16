"""
Основной скрипт автоматизации (Hill Climb / Racing Bot).
Версия: 1.1.4

ОГЛАВЛЕНИЕ:
[0] Проверка и разблокировка экрана
[1] Импорты и настройки
[2] Инициализация и запуск игры
[3] Навигация по меню (UI)
[4] Завершение этапа
"""

import time
import subprocess
from pathlib import Path
from adb_tools import (
    run_game, screenshot, draw_tap, 
    click_start_if_found, speak_text, pulse_gas, swipe
)

__version__ = "1.1.4"

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


# ==============================================================================
# [0] ПРОВЕРКА И РАЗБЛОКИРОВКА ЭКРАНА
# ==============================================================================

def check_and_unlock_screen():
    """
    Проверяет состояние экрана устройства.
    Если экран выключен или заблокирован — выполняет разблокировку.
    """
    print("\n🔒 Проверка состояния экрана...")
    
    # Получаем состояние питания устройства
    result = subprocess.run(
        ["adb", "shell", "dumpsys", "power"],
        capture_output=True, text=True
    )
    
    is_screen_on = "mWakefulness=Awake" in result.stdout
    is_locked = "mDreamingLockscreen=true" in result.stdout
    
    if is_screen_on and not is_locked:
        print("✅ Экран включён и разблокирован")
        return True
    
    print("⚠️ Экран выключен или заблокирован. Выполняю разблокировку...")
    
    # Команда разблокировки: включить экран → свайп → ввести PIN → Enter
    unlock_cmd = (
        "input keyevent 224 && "           # Включить экран (WAKEUP)
        "input swipe 540 1500 540 500 500 && "  # Свайп вверх для снятия блокировки
        "input text seal && "              # Ввод PIN-кода
        "input keyevent 66"                # Нажатие Enter
    )
    subprocess.run(["adb", "shell", unlock_cmd], capture_output=True, text=True)
    
    # Ждём, пока система обработает разблокировку
    time.sleep(2)
    
    # Проверяем результат
    result = subprocess.run(
        ["adb", "shell", "dumpsys", "power"],
        capture_output=True, text=True
    )
    
    if "mWakefulness=Awake" in result.stdout:
        print("✅ Экран успешно разблокирован")
        return True
    else:
        print("❌ Не удалось разблокировать экран. Проверьте PIN-код.")
        return False


# ==============================================================================
# [2] ИНИЦИАЛИЗАЦИЯ И ЗАПУСК
# ==============================================================================

print(f"\n————— 🤖 ЗАПУСК БОТА v{__version__} ———-")

# Сначала проверяем и разблокируем экран
if not check_and_unlock_screen():
    print("⚠️ Продолжаю работу, но экран может быть заблокирован...")

run_game()
print("🚀 Игра запущена. Ожидание загрузки главного меню (5 сек)...")
time.sleep(5)


# ==============================================================================
# [3] НАВИГАЦИЯ ПО МЕНЮ
# ==============================================================================

print(f"\n🔍 Этап 1: Поиск кнопки 'АППАРАТ'...")

found_apparat = click_start_if_found(
    template_path=str(TEMPLATE_APPARAT), 
    threshold=0.85,
    debug=True
)

if found_apparat:
    print("✅ Кнопка 'АППАРАТ' найдена и нажата!")
else:
    print("️ Кнопка 'АППАРАТ' не найдена. Проверьте:")
    print("   - Открыто ли нужное меню?")
    print("   - Правильный ли путь к шаблону?")
    print("   - Попробуйте снизить threshold до 0.7")


# ==============================================================================
# [4] ЗАВЕРШЕНИЕ ЭТАПА
# ==============================================================================

print("\n————— ✅ ЭТАП ЗАВЕРШЕН ———-")
print(f"📁 Папка скриншотов: {SCREENSHOT_DIR}\n")