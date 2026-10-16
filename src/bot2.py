"""
Скрипт для теста запуска и поиска кнопки СТАРТ.
Версия: 1.1.2

ШАБЛОНЫ (лежат в assets/search_ui_components/):
- button_СТАРТ.png       — первая кнопка СТАРТ в меню
- button_СТАРТ_2.png     — вторая кнопка СТАРТ (после первого клика)
- button_pause.png       — кнопка паузы (индикатор начала гонки)
- button_close_2.png     — крестик во время гонки (реклама/окно)
- button_car_outline.png — контур машины (заготовка)
"""

import subprocess
import time
from pathlib import Path
from adb_tools import (
    run_game, screenshot,
    pulse_gas,
    check_and_unlock_screen, wait_for_template
)

__version__ = "1.1.2"

# ==============================================================================
# [1] НАСТРОЙКИ
# ==============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
UI_PATH = PROJECT_ROOT / "assets" / "search_ui_components"
SCREENSHOT_DIR = PROJECT_ROOT / "src" / "screenshot"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

# Шаблоны
TEMPLATE_START = UI_PATH / "button_СТАРТ.png"
TEMPLATE_START_2 = UI_PATH / "button_СТАРТ_2.png"
TEMPLATE_PAUSE = UI_PATH / "button_pause.png"
TEMPLATE_CLOSE_2 = UI_PATH / "button_close_2.png"  # ← Новый шаблон
TEMPLATE_CAR = UI_PATH / "button_car_outline.png"

# Координаты
GAS_X, GAS_Y = 1670, 1000

# Параметры газа (увеличены на 50% от предыдущих 120мс)
GAS_HOLD_MS = 180      # Было 120мс, стало 180мс (+50%)
GAS_PAUSE_MS = 200     # Пауза между нажатиями
GAS_BLOCK_SEC = 20     # Длительность одного блока газа
MAX_GAS_BLOCKS = 50     # Сколько блоков газа сделать (итого 50 сек)


# ==============================================================================
# [2] ФУНКЦИЯ: ОЖИДАНИЕ НАЧАЛА ГОНКИ
# ==============================================================================

def wait_for_race_start(timeout=15, interval=1.0, threshold=0.75):
    """Ждёт появления кнопки паузы — индикатор начала гонки."""
    print(f"   Ожидаю появления кнопки паузы (макс. {timeout} сек)...")
    
    pos = wait_for_template(
        template=str(TEMPLATE_PAUSE),
        timeout=timeout,
        interval=interval,
        threshold=threshold
    )
    
    if pos:
        print(f"   ✅ Кнопка паузы найдена: {pos} — гонка началась!")
        return True
    else:
        print(f"   ⚠️ Кнопка паузы не найдена за {timeout} сек.")
        return False


# ==============================================================================
# [3] ФУНКЦИЯ: ПОИСК КРЕСТИКА ВО ВРЕМЯ ГОНКИ
# ==============================================================================

def check_for_close_button(timeout=5, interval=0.5, threshold=0.70):
    """
    Ищет крестик button_close_2.png на экране.
    
    Returns:
        (cx, cy) — координаты крестика, или None если не найден
    """
    pos = wait_for_template(
        template=str(TEMPLATE_CLOSE_2),
        timeout=timeout,
        interval=interval,
        threshold=threshold
    )
    return pos


# ==============================================================================
# [4] ФУНКЦИЯ-ЗАГЛУШКА: ПОИСК КОНТУРА МАШИНЫ
# ==============================================================================

def find_car_outline(timeout=15, interval=1.0, threshold=0.75):
    """
    Ищет контур машины на экране.
    TODO: Реализовать поиск через wait_for_template(template=TEMPLATE_CAR)
    """
    pass


# ==============================================================================
# [5] ЗАПУСК И РАЗБЛОКИРОВКА
# ==============================================================================

print(f"\n—————  ЗАПУСК БОТА v{__version__} ———-")

if not check_and_unlock_screen(pin="seal"):
    print("⚠️ Экран не разблокирован, продолжаю...")


# ==============================================================================
# [6] ЭТАП 1: ЗАПУСК ИГРЫ И ПЕРВЫЙ СТАРТ
# ==============================================================================

run_game()
print("🚀 Игра запущена. Жду появления кнопки 'СТАРТ' (макс. 20 сек)...")

pos = wait_for_template(
    template=str(TEMPLATE_START),
    timeout=20, interval=1.0, threshold=0.80
)

if pos:
    print(f"✅ Кнопка 'СТАРТ' найдена: {pos}")
    subprocess.run(
        ["adb", "shell", "input", "tap", str(pos[0]), str(pos[1])],
        capture_output=True
    )
    print("👆 Тап по СТАРТ выполнен.")
    time.sleep(1)
else:
    print("❌ Кнопка 'СТАРТ' не найдена за 20 секунд.")
    exit(1)


# ==============================================================================
# [7] ЭТАП 2: ВТОРОЙ СТАРТ
# ==============================================================================

print("\n🔍 Этап 2: Жду появления кнопки 'СТАРТ_2' (макс. 20 сек)...")

pos_2 = wait_for_template(
    template=str(TEMPLATE_START_2),
    timeout=20, interval=1.0, threshold=0.80
)

if pos_2:
    print(f"✅ Кнопка 'СТАРТ_2' найдена: {pos_2}")
    subprocess.run(
        ["adb", "shell", "input", "tap", str(pos_2[0]), str(pos_2[1])],
        capture_output=True
    )
    print("👆 Тап по СТАРТ_2 выполнен.")
else:
    print("❌ Кнопка 'СТАРТ_2' не найдена за 20 секунд.")
    exit(1)


# ==============================================================================
# [8] ЭТАП 3: ОЖИДАНИЕ НАЧАЛА ГОНКИ
# ==============================================================================

print("\n Этап 3: Ожидаю начала гонки...")

if not wait_for_race_start(timeout=15, interval=1.0, threshold=0.75):
    print("⚠️ Гонка не началась. Продолжаю через 3 секунды...")
    time.sleep(3)


# ==============================================================================
# [9] ЭТАП 4: СКРИНШОТ ДЛЯ КОНТУРА МАШИНЫ
# ==============================================================================

print("\n📸 Этап 4: Скриншот для контура машины...")

car_screenshot = str(SCREENSHOT_DIR / "bot2_car_outline.png")
screenshot(car_screenshot)
print(f"📸 Скриншот сохранён: {car_screenshot}")


# ==============================================================================
# [10] ЭТАП 5: ЦИКЛИЧЕСКИЙ ГАЗ С ПОИСКОМ КРЕСТИКА
# ==============================================================================

print(f"\n🔥 Этап 5: Циклический газ ({MAX_GAS_BLOCKS} блоков по {GAS_BLOCK_SEC} сек)")
print(f"   Параметры: hold={GAS_HOLD_MS}мс, pause={GAS_PAUSE_MS}мс")
print(f"   Поиск крестика button_close_2.png каждые {GAS_BLOCK_SEC} сек\n")

for block_num in range(1, MAX_GAS_BLOCKS + 1):
    print(f"--- Блок газа {block_num}/{MAX_GAS_BLOCKS} ---")
    
    # 1. Давим газ
    pulse_gas(GAS_X, GAS_Y, duration_sec=GAS_BLOCK_SEC, 
              hold_ms=GAS_HOLD_MS, pause_ms=GAS_PAUSE_MS)
    
    # 2. Ищем крестик
    print(f"   🔍 Ищу крестик (button_close_2.png)...")
    close_pos = check_for_close_button(timeout=3, interval=0.5, threshold=0.70)
    
    if close_pos:
        print(f"   ✅ Крестик найден: {close_pos}")
        
        # Скриншот с крестиком
        close_screenshot = str(SCREENSHOT_DIR / f"bot2_close_found_block{block_num}.png")
        screenshot(close_screenshot)
        print(f"    Скриншот сохранён: {close_screenshot}")
        
        # Кликаем по крестику
        subprocess.run(
            ["adb", "shell", "input", "tap", str(close_pos[0]), str(close_pos[1])],
            capture_output=True
        )
        print(f"   👆 Тап по крестику выполнен.")
        time.sleep(2)  # Ждём закрытия окна
    else:
        print(f"   ⚪ Крестик не найден. Продолжаю газ.")
    
    print()  # Пустая строка для читаемости


# ==============================================================================
# [11] ЭТАП 6: ФИНАЛЬНЫЙ СКРИНШОТ
# ==============================================================================

final_screenshot = str(SCREENSHOT_DIR / "bot2_after_gas.png")
screenshot(final_screenshot)
print(f"📸 Финальный скриншот: {final_screenshot}")

print("\n————— ✅ ТЕСТ ЗАВЕРШЕН ———-")