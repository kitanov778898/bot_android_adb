from time import sleep
from adb_tools import run_game, screenshot, tap, draw_tap,speak_text

__version__ = "1.2.1"

name = "screenshot_готово"
dir = "/data/data/com.termux/files/home/storage/downloads/bot_android_adb/new/screenshot/"

val=dir + name + ".png"


#———(1) запуск игры ——-
#speak_text("запуск игры")
run_game()

sleep(10)
#speak_text("Старт записи скриншотов")

print(f"✅ {val}")
screenshot(val)

#draw_tap(input_path="do_1.png", output_path="fo_1.png", #x=850, y=540, radius=25, color='red')

#speak_text("скрипт завершил работу можно переключаться")


