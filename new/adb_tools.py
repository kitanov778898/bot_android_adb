import subprocess
import re
import time
import cv2
import numpy as np
import select
from config import (
    PACKAGE_NAME, ACTIVITY_NAME,
    SCREEN_W, SCREEN_H, RAW_MAX_X, RAW_MAX_Y,
    SCALE_X, SCALE_Y, TOUCH_DEVICE,
    CLICK_INTERVAL, MAX_CLICKS
)
from PIL import Image, ImageDraw


def run_game():
    """Запускает игру"""
    result = subprocess.run(
        ["adb", "shell", "am", "start", "-f", "0x10020000", "-n", f"{PACKAGE_NAME}/{ACTIVITY_NAME}"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(f"✅ Игра {PACKAGE_NAME} запущена")
    else:
        print(f"❌ Ошибка: {result.stderr}")


def screenshot(filename="screen.png"):
    """Делает скриншот экрана"""
    result = subprocess.run(
        ["adb", "exec-out", "screencap", "-p"],
        capture_output=True
    )
    with open(filename, "wb") as f:
        f.write(result.stdout)
    print(f"✅ Скриншот сохранен: {filename}")


def tap(x, y):
    """Делает клик по экрану"""
    subprocess.run(
        ["adb", "shell", "input", "tap", str(x), str(y)],
        capture_output=True,
        text=True
    )
    print(f"✅ Клик в точке ({x}, {y})")


def monitor_touches3(timeout=10):
    """Читает лог касаний, переводит в экранные координаты и возвращает их"""
    print(f"⏳ Слушаю экран {timeout} секунд. Касайся экрана!")
    process = subprocess.Popen(
        ["adb", "shell", "getevent", "-l", TOUCH_DEVICE],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        universal_newlines=True
    )
    start_time = time.time()
    last_x = None
    last_y = None
    try:
        while time.time() - start_time < timeout:
            ready, _, _ = select.select([process.stdout], [], [], 0.1)
            if ready:
                line = process.stdout.readline()
                if "ABS_MT_POSITION_X" in line:
                    hex_val = line.split()[-1]
                    raw_x = int(hex_val, 16)
                    last_x = round(raw_x / SCALE_X)
                    print(f"📍 X = {last_x}")
                elif "ABS_MT_POSITION_Y" in line:
                    hex_val = line.split()[-1]
                    raw_y = int(hex_val, 16)
                    last_y = round(raw_y / SCALE_Y)
                    print(f"📍 Y = {last_y}")
    except KeyboardInterrupt:
        print("\n✅ Остановлено вручную")
    finally:
        process.terminate()
        print("⏰ Время вышло!")
    
    if last_x is not None and last_y is not None:
        print(f"✅ Готовые координаты для клика: ({last_x}, {last_y})")
        return last_x, last_y
    return None, None


def record_touches_to_file(timeout=5, filename="touchscreen_log.txt"):
    """
    Записывает сырой лог касаний в текстовый файл.
    Слушает только тачскрин (/dev/input/event2).
    
    Args:
        timeout: длительность записи в секундах
        filename: имя выходного файла
    
    Returns:
        Путь к сохранённому файлу
    """
    print(f"⏳ Запись лога {timeout} секунд. Касайся экрана!")
    print(f"📁 Файл: {filename}")
    
    process = subprocess.Popen(
        ["adb", "shell", "getevent", "-l", "-t", TOUCH_DEVICE],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        universal_newlines=True
    )
    
    start_time = time.time()
    lines_count = 0
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            while time.time() - start_time < timeout:
                ready, _, _ = select.select([process.stdout], [], [], 0.1)
                if ready:
                    line = process.stdout.readline()
                    if not line:
                        break
                    f.write(line)
                    lines_count += 1
    except KeyboardInterrupt:
        print("\n✅ Запись остановлена вручную")
    finally:
        process.terminate()
    
    print(f"⏰ Запись завершена!")
    print(f"✅ Строк записано: {lines_count}")
    print(f"📁 Файл сохранён: {filename}")
    return filename


def parse_touch_log(filename="touchscreen_log.txt"):
    """
    Парсит записанный лог и извлекает координаты касаний.
    Возвращает список касаний с усреднёнными координатами.
    
    Returns:
        Список словарей: [{"raw_x": ..., "raw_y": ..., "pixel_x": ..., "pixel_y": ...}, ...]
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Файл {filename} не найден")
        return []
    
    # Разделяем по маркеру конца касания
    touches_raw = content.split("ABS_MT_TRACKING_ID   ffffffff")
    
    results = []
    for i, touch in enumerate(touches_raw[:-1]):
        x_values = []
        y_values = []
        
        for line in touch.split("\n"):
            if "ABS_MT_POSITION_X" in line:
                hex_val = line.split()[-1]
                x_values.append(int(hex_val, 16))
            elif "ABS_MT_POSITION_Y" in line:
                hex_val = line.split()[-1]
                y_values.append(int(hex_val, 16))
        
        if x_values and y_values:
            avg_raw_x = sum(x_values) / len(x_values)
            avg_raw_y = sum(y_values) / len(y_values)
            
            pixel_x = round(avg_raw_x / SCALE_X)
            pixel_y = round(avg_raw_y / SCALE_Y)
            
            touch_data = {
                "raw_x": avg_raw_x,
                "raw_y": avg_raw_y,
                "pixel_x": pixel_x,
                "pixel_y": pixel_y,
                "points_count": len(x_values)
            }
            results.append(touch_data)
            
            print(f"Касание {i+1}:")
            print(f"  Сырые: X={avg_raw_x:.1f}, Y={avg_raw_y:.1f}")
            print(f"  Пиксели: X={pixel_x}, Y={pixel_y}")
            print(f"  Точек: {len(x_values)}")
            print(f"  Команда: adb shell input tap {pixel_x} {pixel_y}\n")
    
    print(f"✅ Всего касаний: {len(results)}")
    return results

def draw_tap(input_path, output_path, x, y, radius=25, color='red'):
    """
    Открывает изображение, рисует закрашенный круг (tap) в заданной точке,
    сохраняет результат в новый файл.

    Параметры:
        input_path (str): путь к исходному изображению.
        output_path (str): путь для сохранения результата.
        x, y (int): координаты центра круга.
        radius (int): радиус круга (по умолчанию 25).
        color (str или tuple): цвет заливки (по умолчанию 'red').
    """
    img = Image.open(input_path)
    draw = ImageDraw.Draw(img)
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    img.save(output_path)

def speak_text(text):
    """
    Воспроизводит заданный текст через Termux TTS.

    Параметры:
        text (str): текст, который нужно озвучить.
    """
    subprocess.run(["termux-tts-speak","-e", "com.google.android.tts","-l","ru", text])
#termux-tts-speak -e com.google.android.tts -l ru "Текст" Явно указать движок

def record_screen(filename="video.mp4", size="1728x1080", time_limit=10):
    """
    Записывает видео с экрана через adb shell screenrecord.

    Параметры:
        filename (str): имя файла на устройстве (по умолчанию "video.mp4")
        size (str): разрешение в формате "ШxВ" (по умолчанию "1728x1080")
        time_limit (int): длительность записи в секундах (по умолчанию 10)

    Возвращает:
        str: вывод команды или None при ошибке
    """
    result = subprocess.run(
        ["adb", "shell", "screenrecord", "--verbose",
         "--size", size, "--time-limit", str(time_limit),
         f"/sdcard/{filename}"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"❌ Ошибка: {result.stderr}")
        return None
    return result.stdout


def click_start_if_found(template_path="button_start.png", threshold=0.8):
    """Находит шаблон на экране Android-устройства и тапает по его центру.

    Args:
        template_path: путь к PNG-файлу шаблона.
        threshold: минимальная уверенность совпадения (0..1).
    """
    # 1. Читаем шаблон
    template = cv2.imread(template_path)
    if template is None:
        print(f"❌ Не найден шаблон: {template_path}")
        exit(1)  # ошибка — шаблон не найден

    # 2. Делаем скриншот через adb (-p = формат PNG)
    raw_bytes = subprocess.run(
        ["adb", "exec-out", "screencap", "-p"],
        stdout=subprocess.PIPE,
        check=True,
    ).stdout

    # 3. Преобразуем байты в NumPy-массив
    image_array = np.frombuffer(raw_bytes, dtype=np.uint8)

    # 4. Декодируем массив в картинку OpenCV
    screen = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if screen is None:
        print("❌ Не удалось декодировать скриншот от ADB. Проверьте подключение устройства.")
        exit(1)  # ошибка — скриншот битый

    # 5. Ищем шаблон на скриншоте
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    # 6. Если нашли — считаем центр и тапаем
    if max_val >= threshold:
        print("\n✅ НАЙДЕНО!")
        print(f"\n🎯 Уверенность: {max_val:.3f}")

        h, w = template.shape[:2]
        cx = max_loc[0] + w // 2
        cy = max_loc[1] + h // 2

        subprocess.run(
            ["adb", "shell", "input", "tap", str(cx), str(cy)],
            stdout=subprocess.PIPE,
            check=True,
        )
        print(f"👆 Тап в ({cx}, {cy})")
    else:
        print(f"\n❌ НЕ найдено (порог {threshold} > {max_val:.3f})")


def tap_hold(x, y, hold_ms=300):
    """Нажимает и держит hold_ms миллисекунд."""
    subprocess.run(
        ["adb", "shell", "input", "swipe",
         str(x), str(y), str(x), str(y), str(hold_ms)],
        stdout=subprocess.PIPE,
        check=True,
    )


def pulse_gas(x, y, duration_sec=10, hold_ms=100, pause_ms=200):
    """Пульсирует газом: держим hold_ms, пауза pause_ms.

    Args:
        x, y: координаты кнопки газа.
        duration_sec: сколько всего секунд пульсировать.
        hold_ms: длительность удержания.
        pause_ms: длительность паузы.
    """
    start = time.time()
    cycle = (hold_ms + pause_ms) / 1000  # длительность одного цикла в секундах

    while time.time() - start < duration_sec:
        tap_hold(x, y, hold_ms)
        time.sleep(pause_ms / 1000)

    print(f"⏱️ Пульсация {duration_sec}с завершена "
          f"(удержание {hold_ms}мс, пауза {pause_ms}мс)")


def grab_screen():
    """Скриншот устройства -> BGR numpy-массив (без файла на диске)."""
    result = subprocess.run(
        ["adb", "exec-out", "screencap", "-p"],
        capture_output=True
    )
    if result.returncode != 0 or not result.stdout:
        return None

    raw = np.frombuffer(result.stdout, dtype=np.uint8)
    screen = cv2.imdecode(raw, cv2.IMREAD_COLOR)
    return screen

def find_template(screen, template, threshold=0.85, roi=None):
    """Ищет шаблон на экране. Возвращает (cx, cy) или None.

    Args:
        screen: BGR numpy-массив (скриншот).
        template: BGR numpy-массив (шаблон).
        threshold: порог уверенности (0..1).
        roi: (x1, y1, x2, y2) — область поиска.
             Если None — ищем по всему экрану.

    Returns:
        (cx, cy) — центр шаблона в координатах экрана.
        None — если не найдено или шаблон больше области.
    """
    h, w = template.shape[:2]

    # Если задан ROI — вырезаем подэкран, иначе берём весь
    if roi is not None:
        x1, y1, x2, y2 = roi
        sub = screen[y1:y2, x1:x2]
    else:
        sub = screen
        x1, y1 = 0, 0

    # Защита: шаблон не должен быть больше области поиска
    if sub.shape[0] < h or sub.shape[1] < w:
        return None

    result = cv2.matchTemplate(sub, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        # max_loc — в координатах sub, добавляем смещение ROI
        cx = max_loc[0] + w // 2 + x1
        cy = max_loc[1] + h // 2 + y1
        return (cx, cy)

    return None

def wait_for_template(template, timeout=30, interval=1.0, threshold=0.85, roi=None):
    """Ждёт появления шаблона на экране. Возвращает (cx, cy) или None."""
    t0 = time.perf_counter()
    while True:
        screen = grab_screen()
        if screen is None:
            return None

        pos = find_template(screen, template, threshold, roi)
        if pos is not None:
            return pos

        if time.perf_counter() - t0 > timeout:
            return None

        time.sleep(interval)

# ———- шаблон для новой функции –—————————————————————————-

def function_name(param1, param2="default"):
    """
    Краткое описание что делает функция.

    Параметры:
        param1 (str): описание
        param2 (str): описание (по умолчанию "default")

    Возвращает:
        str: результат команды
    """
    result = subprocess.run(
        ["команда", "-флаг", param1],
        capture_output=True,
        text=True
    )
    return result.stdout




# ———- .замер функции сколько выполняются ——————————————————-
#t0 = time.perf_counter()   # ЗАСЕЧКА ДО
#... делаем что-то ...
#t1 = time.perf_counter()   # ЗАСЕЧКА ПОСЛЕ
#print(t1 - t0)             # сколько заняло

#print(f"{(t1 - t0) * 1000:.0f} мс")



