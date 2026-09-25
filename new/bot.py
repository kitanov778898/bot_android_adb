from time import sleep
from adb_tools import run_game, screenshot, tap, monitor_touches3, record_touches_to_file

# Сценарий работы бота
run_game()
sleep(2)
#screenshot()
#record_touches_to_file()
tap(414, 1572)

# Когда нужно будет найти координаты, просто раскомментируй строку ниже:
#monitor_touches3()