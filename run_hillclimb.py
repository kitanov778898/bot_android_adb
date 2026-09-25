import subprocess
import time
import os # Подключаем модуль для работы с путями и папками

PACKAGE = "com.fingersoft.hillclimb"

# 1. Создаём переменную для папки
OUTPUT_DIR = "hillclimb_dumps2" 

# 2. Создаём папку, если она ещё не существует (exist_ok=True предотвратит ошибку, если папка уже есть)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Запускаем игру через monkey (надёжнее, чем am start, для этого пакета)
subprocess.run(["adb", "shell", "monkey", "-p", PACKAGE, "1"])

# Ждём 25 секунд, пока загрузится
time.sleep(25)

# 3. Скриншот на компьютер (используем os.path.join для формирования пути)
screenshot_path = os.path.join(OUTPUT_DIR, "screenshot.png")
with open(screenshot_path, "wb") as f:
    subprocess.run(["adb", "exec-out", "screencap", "-p"], stdout=f)

time.sleep(5)
# adb shell input tap 1620 720
subprocess.run(["adb", "shell", "uiautomator", "input", "tap" ,"1620 720"])

# 4. XML-дамп экрана на устройстве
subprocess.run(["adb", "shell", "uiautomator", "dump", "/sdcard/page.xml"])

# 5. Копируем XML на компьютер в нашу папку и чистим за собой
xml_path = os.path.join(OUTPUT_DIR, "page.xml")
subprocess.run(["adb", "pull", "/sdcard/page.xml", xml_path])
subprocess.run(["adb", "shell", "rm", "/sdcard/page.xml"])

# 6. Дамп активности в файл в нашей папке
activity_path = os.path.join(OUTPUT_DIR, "activity_dump.txt")
with open(activity_path, "w", encoding="utf-8") as f:
    subprocess.run(["adb", "shell", "dumpsys", "activity"], stdout=f, text=True)

# 7. Закрываем игру
subprocess.run(["adb", "shell", "am", "force-stop", PACKAGE])

print(f"Готово! Все данные сохранены в папку '{OUTPUT_DIR}'.")
