"""
Основной скрипт автоматизации (Hill Climb / Racing Bot).
Версия: 1.2.7
"""

import time
import subprocess
from pathlib import Path
from adb_tools import (
    run_game, screenshot,
    click_start_if_found, swipe,
    check_and_unlock_screen, wait_for_template
)

__version__ = "1.2.7"

# ==============================================================================
# [1] НАСТРОЙКИ
# ==============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
UI_PATH = PROJECT_ROOT / "assets" / "search_ui_components"
SCREENSHOT_DIR = PROJECT_ROOT / "src" / "screenshot"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

TEMPLATE_APPARAT = UI_PATH / "button_АППАРАТ.png"
TEMPLATE_GARAGE = UI_PATH / "button_ГАРАЖ.png"
TEMPLATE_DONE = UI_PATH / "button_ГОТОВО.png"
TEMPLATE_DONE_2 = UI_PATH / "button_ГОТОВО_2.png"


# ==============================================================================
# [2] ЗАПУСК
# ==============================================================================

print(f"\n————— 🤖 ЗАПУСК БОТА v{__version__} ———-")

if not check_and_unlock_screen(pin="seal"):
    print("⚠️ Экран не разблокирован, продолжаю...")

run_game()
print("🚀 Жду появления кнопки 'АППАРАТ' (макс. 20 сек)...")


# ==============================================================================
# [3] ЭТАП 1: АППАРАТ
# ==============================================================================

pos = wait_for_template(
    template=str(TEMPLATE_APPARAT),
    timeout=20, interval=1.0, threshold=0.85
)

if not pos:
    print("❌ АППАРАТ не найден. Выход.")
    exit(1)

print(f"✅ АППАРАТ найден: {pos}")
subprocess.run(
    ["adb", "shell", "input", "tap", str(pos[0]), str(pos[1])],
    capture_output=True
)
time.sleep(2)


# ==============================================================================
# [4] ЭТАП 2: ГАРАЖ (с прокруткой)
# ==============================================================================

print("\n🔍 Этап 2: Ищу ГАРАЖ...")
found = False
for i in range(15):
    found = click_start_if_found(
        template_path=str(TEMPLATE_GARAGE),
        threshold=0.80,
        debug=True,
        debug_path=str(SCREENSHOT_DIR / f"garage_{i+1}.png")
    )
    if found:
        print(f"✅ ГАРАЖ найден на свайпе {i+1}")
        break
    swipe(1300, 600, 900, 600, 600)
    time.sleep(1.5)

if not found:
    print("❌ ГАРАЖ не найден. Выход.")
    exit(1)


# ==============================================================================
# [5] ЭТАП 3: ГОТОВО
# ==============================================================================

print("\n🔍 Этап 3: Жду ГОТОВО...")
pos = wait_for_template(
    template=str(TEMPLATE_DONE),
    timeout=15, interval=1.0, threshold=0.80
)

if pos:
    print(f"✅ ГОТОВО найдено: {pos}")
    subprocess.run(
        ["adb", "shell", "input", "tap", str(pos[0]), str(pos[1])],
        capture_output=True
    )
    time.sleep(3)
else:
    print("⚠️ ГОТОВО не найдено. Пропускаю.")


# ==============================================================================
# [6] ЭТАП 4: ГОТОВО_2
# ==============================================================================

print("\n🔍 Этап 4: Жду ГОТОВО_2...")
pos = wait_for_template(
    template=str(TEMPLATE_DONE_2),
    timeout=15, interval=1.0, threshold=0.80
)

if pos:
    print(f"✅ ГОТОВО_2 найдено: {pos}")
    subprocess.run(
        ["adb", "shell", "input", "tap", str(pos[0]), str(pos[1])],
        capture_output=True
    )
    time.sleep(2)
else:
    print("⚠️ ГОТОВО_2 не найдено за 15 секунд.")
    print("📸 Делаю скриншот для анализа...")
    screenshot(str(SCREENSHOT_DIR / "after_done_no_garage2.png"))
    print(f"📁 Скриншот: {SCREENSHOT_DIR / 'after_done_no_garage2.png'}")


# ==============================================================================
# [7] ЗАВЕРШЕНИЕ
# ==============================================================================

print("\n————— ✅ ВСЕ ЭТАПЫ ЗАВЕРШЕНЫ ———-")
print(f"📁 Папка скриншотов: {SCREENSHOT_DIR}\n")