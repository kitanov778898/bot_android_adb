from time import sleep
import subprocess
from adb_tools import run_game, screenshot, tap, monitor_touches3, record_touches_to_file

__version__ = "1.0.1"

"""Это docstring. 1)организуем проверку статуса экрана. 2) разблокируем экран вводим пароль 3)запускаем приложение"""

# Сценарий работы бота

# 1)организуем проверку статуса экрана.
#используем команду
#adb shell dumpsys display | findstr mScreenState

#run_game()
#sleep(2)

def display_status() -> int:
    """Проверяет статус экрана Android устройства.

    Выполняет команду dumpsys display и определяет, включен ли экран.

    Returns:
        int: 1 если экран включен, 0 если выключен или в спящем режиме.

    Example:
        >>> status = display_status()
        >>> print(f"Экран: {'включен' if status else 'выключен'}")
    """
    result = subprocess.run(
        ["adb", "shell", "dumpsys", "display"],
        capture_output=True,
        text=True
.    как дополнение обязательно проверить есть ли подключение по ADB иначе не правильный статус выдастся
    )
    
    # Ищем строку с mScreenState
    for line in result.stdout.split('\n'):
        if 'mScreenState=' in line:
            state = line.split('=')[1].strip()
            return 1 if state == 'ON' else 0
    
    return 0

#———————————————————————- end ———————————————————————-

def display_password() -> int:
   pass

def main():
    print('--------*** START ***--------')
    status = display_status()
    print(f"статус : {status}")
    if status == False: # если выключен то
       print("выкл.")
       pass
    print('--------*** END ***-------')
    pass

if __name__ == "__main__":
    main()
