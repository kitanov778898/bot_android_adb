"""
Модуль утилит для автоматизации Android через ADB и OpenCV.

=== НАВИГАЦИЯ ПО ФУНКЦИЯМ ===

1. Управление устройством и приложением
   1.1. run_game()                - Запуск указанного приложения/игры через ADB.
   1.2. get_screen_status()       - Проверка текущего состояния экрана (включен/выключен).
   1.3. check_and_unlock_screen() - Проверка состояния экрана и его разблокировка с помощью PIN-кода.

2. Захват и работа с изображением экрана
   2.1. screenshot()              - Создание скриншота и сохранение его в файл.
   2.2. grab_screen_gray()        - Получение скриншота в оттенках серого (NumPy array) для быстрой обработки.
   2.3. grab_screen()             - Получение цветного скриншота (NumPy array, BGR) для дальнейшей обработки.
   2.4. record_screen()           - Запись видео с экрана устройства в файл.

3. Эмуляция пользовательского ввода
   3.1. tap()                     - Эмуляция одиночного нажатия (тапа) по заданным координатам.
   3.2. swipe()                   - Эмуляция свайпа (проведения) между двумя точками.
   3.3. tap_hold()                - Эмуляция удержания нажатия в заданной точке.
   3.4. pulse_gas()               - Циклическое нажатие с удержанием (например, имитация педали газа).

4. Анализ и логирование касаний
   4.1. get_touch_coordinates()   - Интерактивный сбор и вывод координат касаний в реальном времени.
   4.2. record_touches_to_file()  - Запись сырых данных событий касания (getevent) в текстовый файл.
   4.3. parse_touch_log()         - Парсинг лог-файла касаний для вычисления усредненных координат.

5. Компьютерное зрение и поиск шаблонов
   5.1. find_template()           - Поиск шаблона на изображении (с поддержкой области интереса ROI).
   5.2. wait_for_template()       - Ожидание появления шаблона на экране в течение заданного времени.
   5.3. click_start_if_found()    - Поиск шаблона на экране и автоматический клик по нему при обнаружении.

6. Визуализация и отладка
   6.1. draw_tap()                - Визуализация точки нажатия (круга) на изображении с помощью PIL.
   6.2. draw_roi()                - Визуализация области интереса (ROI) на изображении с помощью OpenCV.

7. Прочие утилиты
   7.1. speak_text()              - Озвучивание текста через системный TTS (termux-tts-speak).
"""

import subprocess
import time
import select
import cv2
import numpy as np
from PIL import Image, ImageDraw
from functools import wraps

from config import (
    PACKAGE_NAME, ACTIVITY_NAME,
    SCREEN_W, SCREEN_H, RAW_MAX_X, RAW_MAX_Y,
    SCALE_X, SCALE_Y, TOUCH_DEVICE,
    CLICK_INTERVAL, MAX_CLICKS
)

__version__ = "1.3.1"  # Обновил версию, так как добавлена новая функциональность


def measure_time(func):
    """Декоратор для замера времени выполнения функции.

    Оборачивает функцию и при каждом вызове выводит в консоль
    время её выполнения в миллисекундах с использованием
    высокоточного счётчика ``time.perf_counter``.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        t1 = time.perf_counter()
        elapsed_ms = (t1 - t0) * 1000
        print(f"⏱ Функция '{func.__name__}' выполнялась: {elapsed_ms:.2f} мс")
        return result
    return wrapper


# ==============================================================================
# 1. Управление устройством и приложением
# ==============================================================================

def run_game():
    result = subprocess.run(
        ["adb", "shell", "am", "start", "-f", "0x10020000", "-n", f"{PACKAGE_NAME}/{ACTIVITY_NAME}"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f" Игра {PACKAGE_NAME} запущена")
    else:
        print(f" Ошибка запуска: {result.stderr}")

def get_screen_status():
    result = subprocess.run(
        ["adb", "shell", "dumpsys", "display"],
        capture_output=True, text=True
    )
    for line in result.stdout.splitlines():
        if "mScreenState=" in line:
            return line.split("=")[-1].strip()
    return "UNKNOWN"

def check_and_unlock_screen(pin="seal"):
    print("\n Проверка состояния экрана...")
    status = get_screen_status()
    print(f"   Текущий статус: {status}")
    if status == "ON":
        print(" Экран включён")
        return True
    print(" Экран выключен. Выполняю разблокировку...")
    unlock_cmd = (
        "input keyevent 224 && "
        "sleep 1 && "
        "input swipe 540 1500 540 500 500 && "
        "sleep 0.5 && "
        f"input text {pin} && "
        "sleep 0.5 && "
        "input keyevent 66"
    )
    subprocess.run(["adb", "shell", unlock_cmd], capture_output=True, text=True)
    time.sleep(2)
    status = get_screen_status()
    if status == "ON":
        print(" Экран успешно разблокирован")
        return True
    else:
        print(" Не удалось разблокировать экран. Проверьте PIN-код.")
        return False


# ==============================================================================
# 2. Захват и работа с изображением экрана
# ==============================================================================

def screenshot(filename="screen.png"):
    result = subprocess.run(["adb", "exec-out", "screencap", "-p"], capture_output=True)
    with open(filename, "wb") as f:
        f.write(result.stdout)
    print(f" Скриншот сохранен: {filename}")

def grab_screen_gray():
    """
    Захватывает скриншот экрана Android через ADB в оттенках серого.
    
    Выполняет команду `adb exec-out screencap -p` для получения PNG-скриншота
    напрямую в память (без сохранения на диск), декодирует его в numpy array
    в режиме grayscale.
    
    Returns:
        numpy.ndarray | None: Изображение в оттенках серого (1 канал) 
        в формате numpy array, или None, если произошла ошибка.
    """
    result = subprocess.run(
        ["adb", "exec-out", "screencap", "-p"], 
        capture_output=True
    )
    if result.returncode != 0 or not result.stdout:
        return None
    
    raw = np.frombuffer(result.stdout, dtype=np.uint8)
    return cv2.imdecode(raw, cv2.IMREAD_GRAYSCALE)

def grab_screen():
    """
    Захватывает скриншот экрана Android через ADB в цвете (BGR).
    
    Выполняет команду `adb exec-out screencap -p` для получения PNG-скриншота
    напрямую в память (без сохранения на диск), декодирует его в numpy array
    в цветном режиме BGR. Альфа-канал (прозрачность) игнорируется.
    
    Returns:
        numpy.ndarray | None: Цветное изображение в формате BGR (3 канала) 
        в виде numpy array, или None, если произошла ошибка.
    """
    result = subprocess.run(
        ["adb", "exec-out", "screencap", "-p"], 
        capture_output=True
    )
    if result.returncode != 0 or not result.stdout:
        return None
    
    raw = np.frombuffer(result.stdout, dtype=np.uint8)
    return cv2.imdecode(raw, cv2.IMREAD_COLOR)

def record_screen(filename="video.mp4", size="1728x1080", time_limit=10):
    result = subprocess.run(
        ["adb", "shell", "screenrecord", "--verbose", "--size", size, 
         "--time-limit", str(time_limit), f"/sdcard/{filename}"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f" Ошибка записи видео: {result.stderr}")
        return None
    return result.stdout


# ==============================================================================
# 3. Эмуляция пользовательского ввода
# ==============================================================================

def tap(x, y):
    subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)], capture_output=True, text=True)
    print(f" Клик в точке ({x}, {y})")

def swipe(start_x, start_y, end_x, end_y, duration=500):
    subprocess.run(
        ["adb", "shell", "input", "swipe", str(start_x), str(start_y), str(end_x), str(end_y), str(duration)],
        capture_output=True, text=True
    )
    print(f" Свайп из ({start_x}, {start_y}) в ({end_x}, {end_y}) за {duration}мс")

def tap_hold(x, y, hold_ms=300):
    subprocess.run(
        ["adb", "shell", "input", "swipe", str(x), str(y), str(x), str(y), str(hold_ms)],
        capture_output=True, text=True
    )

def pulse_gas(x, y, duration_sec=10, hold_ms=100, pause_ms=200):
    start = time.time()
    while time.time() - start < duration_sec:
        tap_hold(x, y, hold_ms)
        time.sleep(pause_ms / 1000)
    print(f" Пульсация {duration_sec}с завершена (удержание {hold_ms}мс, пауза {pause_ms}мс)")


# ==============================================================================
# 4. Анализ и логирование касаний
# ==============================================================================

def get_touch_coordinates(timeout=10):
    print(f" Слушаю экран {timeout} секунд. Касайся экрана!")
    process = subprocess.Popen(
        ["adb", "shell", "getevent", "-l", TOUCH_DEVICE],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        bufsize=1, universal_newlines=True
    )
    start_time = time.time()
    last_x, last_y = None, None
    try:
        while time.time() - start_time < timeout:
            ready, _, _ = select.select([process.stdout], [], [], 0.1)
            if ready:
                line = process.stdout.readline()
                if "ABS_MT_POSITION_X" in line:
                    last_x = round(int(line.split()[-1], 16) / SCALE_X)
                    print(f" X = {last_x}")
                elif "ABS_MT_POSITION_Y" in line:
                    last_y = round(int(line.split()[-1], 16) / SCALE_Y)
                    print(f" Y = {last_y}")
    except KeyboardInterrupt:
        print("\n Остановлено вручную")
    finally:
        process.terminate()
        print(" Время вышло!")
    if last_x is not None and last_y is not None:
        print(f" Готовые координаты для клика: ({last_x}, {last_y})")
        return last_x, last_y
    return None, None

def record_touches_to_file(timeout=5, filename="touchscreen_log.txt"):
    print(f" Запись лога {timeout} сек. Файл: {filename}")
    process = subprocess.Popen(
        ["adb", "shell", "getevent", "-l", "-t", TOUCH_DEVICE],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        bufsize=1, universal_newlines=True
    )
    start_time = time.time()
    lines_count = 0
    try:
        with open(filename, "w", encoding="utf-8") as f:
            while time.time() - start_time < timeout:
                ready, _, _ = select.select([process.stdout], [], [], 0.1)
                if ready:
                    line = process.stdout.readline()
                    if not line: break
                    f.write(line)
                    lines_count += 1
    except KeyboardInterrupt:
        print("\n Запись остановлена вручную")
    finally:
        process.terminate()
    print(f" Запись завершена! Строк: {lines_count}. Файл: {filename}")
    return filename

def parse_touch_log(filename="touchscreen_log.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f" Файл {filename} не найден")
        return []
    touches_raw = content.split("ABS_MT_TRACKING_ID   ffffffff")
    results = []
    for i, touch in enumerate(touches_raw[:-1]):
        x_values, y_values = [], []
        for line in touch.split("\n"):
            if "ABS_MT_POSITION_X" in line:
                x_values.append(int(line.split()[-1], 16))
            elif "ABS_MT_POSITION_Y" in line:
                y_values.append(int(line.split()[-1], 16))
        if x_values and y_values:
            avg_raw_x = sum(x_values) / len(x_values)
            avg_raw_y = sum(y_values) / len(y_values)
            pixel_x = round(avg_raw_x / SCALE_X)
            pixel_y = round(avg_raw_y / SCALE_Y)
            results.append({
                "raw_x": avg_raw_x, "raw_y": avg_raw_y,
                "pixel_x": pixel_x, "pixel_y": pixel_y,
                "points_count": len(x_values)
            })
            print(f"Касание {i+1}: Сырые=({avg_raw_x:.1f}, {avg_raw_y:.1f}) | "
                  f"Пиксели=({pixel_x}, {pixel_y}) | Точек={len(x_values)}")
            print(f"  Команда: adb shell input tap {pixel_x} {pixel_y}\n")
    print(f" Всего касаний: {len(results)}")
    return results


# ==============================================================================
# 5. Компьютерное зрение и поиск шаблонов
# ==============================================================================

def find_template(screen, template, threshold=0.85, roi=None):
    if isinstance(template, str):
        template = cv2.imread(template)
        if template is None:
            print(f" Не удалось загрузить шаблон: {template}")
            return None
    screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    h, w = template_gray.shape[:2]
    if roi is not None:
        x1, y1, x2, y2 = roi
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(screen_gray.shape[1], x2), min(screen_gray.shape[0], y2)
        sub = screen_gray[y1:y2, x1:x2]
        offset_x, offset_y = x1, y1
    else:
        sub = screen_gray
        offset_x, offset_y = 0, 0
    if sub.shape[0] < h or sub.shape[1] < w:
        return None
    result = cv2.matchTemplate(sub, template_gray, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val >= threshold:
        return (max_loc[0] + w // 2 + offset_x, max_loc[1] + h // 2 + offset_y)
    return None

def wait_for_template(template, timeout=30, interval=1.0, threshold=0.85, roi=None):
    if isinstance(template, str):
        template_img = cv2.imread(template)
        if template_img is None:
            print(f" Не удалось загрузить шаблон: {template}")
            return None
    else:
        template_img = template
    t0 = time.perf_counter()
    while True:
        screen = grab_screen()
        if screen is not None:
            pos = find_template(screen, template_img, threshold, roi)
            if pos is not None:
                return pos
        if time.perf_counter() - t0 > timeout:
            return None
        time.sleep(interval)

def click_start_if_found(template_path="button_start.png", threshold=0.8, debug=False, debug_path=None):
    template = cv2.imread(template_path)
    if template is None:
        print(f" Не найден шаблон: {template_path}")
        return False
    
    # 💡 ОПТИМИЗАЦИЯ: Используем нашу новую функцию grab_screen() вместо дублирования кода!
    screen = grab_screen()
    if screen is None:
        print(" Не удалось получить скриншот")
        return False
        
    screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    
    if max_val >= threshold:
        h, w = template_gray.shape[:2]
        cx = max_loc[0] + w // 2
        cy = max_loc[1] + h // 2
        if debug:
            x1, y1 = max_loc[0], max_loc[1]
            x2, y2 = max_loc[0] + w, max_loc[1] + h
            debug_img = screen.copy()
            cv2.rectangle(debug_img, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.putText(debug_img, f"OK: {max_val:.2f}", 
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.8, (0, 255, 0), 2)
            if debug_path is None:
                debug_path = "debug.png"
            cv2.imwrite(debug_path, debug_img)
            print(f" [DEBUG] Найдено! Уверенность: {max_val:.3f}")
            print(f" [DEBUG] Скрин сохранён: {debug_path}")
        else:
            print(f"\n НАЙДЕНО! Уверенность: {max_val:.3f}")
            subprocess.run(
                ["adb", "shell", "input", "tap", str(cx), str(cy)],
                stdout=subprocess.PIPE, check=True
            )
            print(f" Тап в ({cx}, {cy})")
        return True
    else:
        print(f"\n НЕ найдено (порог {threshold} > {max_val:.3f})")
        return False


# ==============================================================================
# 6. Визуализация и отладка
# ==============================================================================

def draw_tap(input_path, output_path, x, y, radius=25, color='red'):
    img = Image.open(input_path)
    ImageDraw.Draw(img).ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    img.save(output_path)

def draw_roi(screen, roi, output_path="debug_roi.png"):
    if roi is None:
        print(" ROI не задан, нечего рисовать")
        return
    x1, y1, x2, y2 = roi
    debug_img = screen.copy()
    cv2.rectangle(debug_img, (x1, y1), (x2, y2), (0, 255, 0), 3)
    cv2.putText(debug_img, f"ROI: ({x1},{y1})-({x2},{y2})", 
                (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.imwrite(output_path, debug_img)
    print(f" ROI нарисован и сохранен: {output_path}")


# ==============================================================================
# 7. Прочие утилиты
# ==============================================================================

def speak_text(text):
    subprocess.run(["termux-tts-speak", "-e", "com.google.android.tts", "-l", "ru", text])


if __name__ == "__main__":
    print(f" Модуль adb_tools v{__version__} загружен корректно.")