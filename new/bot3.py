from time import sleep
from adb_tools import run_game, screenshot, tap, draw_tap,speak_text
#———(1) запуск игры ——-
speak_text("запуск игры")
run_game()

#———(2) проверка что окно меню загрузилось ——-

import time

# ——— скриншоты каждые 5 сек в течение 60 сек (for) –—————————

for i in range(1, 31 // 2 + 1):
    filename = f"screen_{i:02d}.png"
    screenshot(filename)
    time.sleep(2)

print(f"✅ Готово. Скриншотов: {60 // 5}")
#———(3) клик в меню по кнопке старт ——-

#sleep(5)

#speak_text("Старт записи скриншотов")

# # Вместо старых кликов попробуй нажать на кнопку START
# Она находится примерно в правом нижнем углу

# Клик по кнопке START (примерные координаты для экрана 1024x640)
#tap(850, 540) 
#screenshot("do_1.png")
#sleep(1)
#draw_tap(input_path="do_1.png", output_path="fo_1.png", x=850, y=540, radius=25, color='red')

speak_text("скрипт завершил работу можно переключаться")


