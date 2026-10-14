import subprocess
import time
from time import sleep
from adb_tools import run_game, screenshot, draw_tap,click_start_if_found, speak_text, pulse_gas, swipe

__version__ = "1.1.1"


# Координаты кнопок под твой экран 1920x1200
START_X, START_Y = 1550, 750
GAS_X, GAS_Y = 1670, 1000
BRAKE_X, BRAKE_Y = 250, 1000
#start_x, start_y, end_x, end_y, duration = 1000,1000, 1050,1000, 500
print(f"————— start ———-")

# 1. Запуск игры и вход в гонку

run_game()
#speak_text("старт")

print(f"🚀 Нажимаем START...")

sleep(5)  # Ждем пока загрузится трасса
#click_start_if_found()
# попадаем в главное окно меню ищем  АППАРАТ

click_start_if_found(template_path="search_ui_components/"+"button_АППАРАТ.png", threshold=0.7)

# прокручиваем экран спайп
# adb shell input swipe <startX> <startY> <endX> <endY> [duration]
#swipe(start_x, start_y, end_x, end_y, duration=500)

#click_start_if_found(template_path="search_ui_components/"+"button_ТЮНИНГ.png", threshold=0.8)

#click_start_if_found(template_path="search_ui_components/"+"button_ТЮНИНГ.png", threshold=0.8)

#click_start_if_found(template_path="search_ui_components/"+"button_ЭТАП.png", threshold=0.8)

#click_start_if_found(template_path="search_ui_components/"+"button_СТАРТ.png", threshold=0.8)


#speak_text("старт")


# Делаем скриншот ПОСЛЕ газа
screenshot("screenshot/test.png")
#draw_tap("after_gas.png", "control_gas.png", GAS_X, GAS_Y, radius=30, color='red')


# Делаем скриншот 
#screenshot("after_brake.png")
#draw_tap("after_brake.png", "control_brake.png", BRAKE_X, BRAKE_Y, radius=30, color='red')

print(f"————— end ———-")
#speak_text("отработал")

