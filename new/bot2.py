import subprocess
import time
from time import sleep
from adb_tools import run_game, screenshot, draw_tap,click_start_if_found, speak_text, pulse_gas

# Координаты кнопок под твой экран 1920x1200
START_X, START_Y = 1550, 750
GAS_X, GAS_Y = 1670, 1000
BRAKE_X, BRAKE_Y = 250, 1000

def hold_button(x, y, duration_ms):
    """Зажимает экран в точке (x, y) на duration_ms миллисекунд"""
    subprocess.run(
        ["adb", "shell", "input", "swipe", str(x), str(y), str(x), str(y), str(duration_ms)],
        capture_output=True
    )

# 1. Запуск игры и вход в гонку
run_game()
sleep(2)

print(f"🚀 Нажимаем START...")
#hold_button(START_X, START_Y, 200) # Короткое нажатие старта
#sleep(5)  # Ждем пока загрузится трасса
click_start_if_found()

#speak_text("старт")

# 2. Начинаем ехать (Газ на 3 секунды)
print("🔥 Тестируем ГАЗ ...")
#hold_button(GAS_X, GAS_Y, 10000)
# Старт: очень короткие импульсы, машина еле ползёт
#pulse_gas(GAS_X, GAS_Y, duration_sec=3, hold_ms=50, pause_ms=400)

# Разгон: импульсы чуть длиннее, паузы короче
pulse_gas(GAS_X, GAS_Y, duration_sec=100, hold_ms=100, pause_ms=200)

# Рабочий режим: умеренный газ
pulse_gas(GAS_X, GAS_Y, duration_sec=100, hold_ms=150, pause_ms=175)


# Делаем скриншот ПОСЛЕ газа
screenshot("close.png")
#draw_tap("after_gas.png", "control_gas.png", GAS_X, GAS_Y, radius=30, color='red')

# 3. Торможение (Тормоз на 0.5 секунды для баланса)
#print("🛑 Жмём ТОРМОЗ на 0.5 секунды...")
#hold_button(BRAKE_X, BRAKE_Y, 500)

# Делаем скриншот ПОСЛЕ тормоза
#screenshot("after_brake.png")
#draw_tap("after_brake.png", "control_brake.png", BRAKE_X, BRAKE_Y, radius=30, color='red')

print("✅ Тест управления завершён!")

