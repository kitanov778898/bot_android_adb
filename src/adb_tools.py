"""
Модуль утилит для автоматизации Android через ADB и OpenCV.
Предназначен для работы в связке с Termux и ПК.

ОГЛАВЛЕНИЕ:
[1] Инициализация и запуск
    - run_game()
[2] Работа с экраном и медиа
    - screenshot(), grab_screen(), record_screen()
    - speak_text()
[3] Базовые действия ввода (Input)
    - tap(), swipe(), tap_hold(), pulse_gas()
[4] Анализ тачскрина (Touchscreen)
    - get_touch_coordinates(), record_touches_to_file(), parse_touch_log()
[5] Компьютерное зрение и автоматизация (OpenCV)
    - click_start_if_found(), find_template(), wait_for_template()
[6] Утилиты отладки
    - draw_tap(), draw_roi()
"""

import subprocess
import time
import select
import cv2
import numpy as np
from PIL import Image, ImageDraw

from config import (
    PACKAGE_NAME, ACTIVITY_NAME,
    SCREEN_W, SCREEN_H, RAW_MAX_X, RAW_MAX_Y,
    SCALE_X, SCALE_Y, TOUCH_DEVICE,
    CLICK_INTERVAL, MAX_CLICKS
)

__version__ = "1.0.2"  # Обновлена версия после рефакторинга


# ==============================================================================
# [1] ИНИЦИАЛИЗАЦИЯ И ЗАПУСК
# ==============================================================================

def run_game():
    """Запускает целевое приложение на Android устройстве."""
    result = subprocess.run(
        ["adb", "shell", "am", "start", "-f", "0x10020000", "-n", f"{PACKAGE_NAME}/{ACTIVITY_NAME}"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"✅ Игра {PACKAGE_NAME} запущена")
    else:
        print(f"❌ Ошибка запуска: {result.stderr}")


# ==============================================================================
# [2] РАБОТА С ЭКРАНОМ И МЕДИА
# ==============================================================================

def screenshot(filename="screen.png"):
    """Делает скриншот экрана и сохраняет его в файл."""
    result = subprocess.run(["adb", "exec-out", "screencap", "-p"], capture_output=True)
    with open(filename, "wb") as f:
        f.write(result.stdout)
    print(f"✅ Скриншот сохранен: {filename}")


def grab_screen():
    """Возвращает скриншот устройства как BGR numpy-массив (без сохранения на диск)."""
    result = subprocess.run(["adb", "exec-out", "screencap", "-p"], capture_output=True)
    if result.returncode != 0 or not result.stdout:
        return None
    raw = np.frombuffer(result.stdout, dtype=np.uint8)
    return cv2.imdecode(raw, cv2.IMREAD_COLOR)


def record_screen(filename="video.mp4", size="1728x1080", time_limit=10):
    """
    Записывает видео с экрана через adb shell screenrecord.
    
    Args:
        filename (str): имя файла на устройстве.
        size (str): разрешение в формате "ШxВ".
        time_limit (int): длительность записи в секундах.
    """
    result = subprocess.run(
        ["adb", "shell", "screenrecord", "--verbose", "--size", size, 
         "--time-limit", str(time_limit), f"/sdcard/{filename}"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"❌ Ошибка записи видео: {result.stderr}")
        return None
    return result.stdout


def speak_text(text):
    """
    Воспроизводит заданный текст через Termux TTS.
    Явно указывает движок Google для стабильности.
    """
    subprocess.run(["termux-tts-speak", "-e", "com.google.android.tts", "-l", "ru", text])


# ==============================================================================
# [3] БАЗОВЫЕ ДЕЙСТВИЯ ВВОДА (INPUT)
# ==============================================================================

def tap(x, y):
    """Делает одиночный клик по экрану."""
    subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)], capture_output=True, text=True)
    print(f"✅ Клик в точке ({x}, {y})")


def swipe(start_x, start_y, end_x, end_y, duration=500):
    """Делает свайп по экрану от одной точки к другой."""
    subprocess.run(
        ["adb", "shell", "input", "swipe", str(start_x), str(start_y), str(end_x), str(end_y), str(duration)],
        capture_output=True, text=True
    )
    print(f"↔️ Свайп из ({start_x}, {start_y}) в ({end_x}, {end_y}) за {duration}мс")


def tap_hold(x, y, hold_ms=300):
    """Нажимает и удерживает экран заданное время (эмуляция через swipe)."""
    subprocess.run(
        ["adb", "shell", "input", "swipe", str(x), str(y), str(x), str(y), str(hold_ms)],
        capture_output=True, text=True
    )


def pulse_gas(x, y, duration_sec=10, hold_ms=100, pause_ms=200):
    """
    Пульсирует нажатием: удержание и отпускание в цикле.
    
    Args:
        x, y: координаты кнопки.
        duration_sec: общая длительность пульсации в секундах.
        hold_ms: длительность удержания в мс.
        pause_ms: длительность паузы между нажатиями в мс.
    """
    start = time.time()
    while time.time() - start < duration_sec:
        tap_hold(x, y, hold_ms)
        time.sleep(pause_ms / 1000)
    print(f"⏱️ Пульсация {duration_sec}с завершена (удержание {hold_ms}мс, пауза {pause_ms}мс)")


# ==============================================================================
# [4] АНАЛИЗ ТАЧСКРИНА (TOUCHSCREEN)
# ==============================================================================

def get_touch_coordinates(timeout=10):
    """
    Читает лог касаний в реальном времени, переводит в экранные координаты и возвращает их.
    (Ранее называлась monitor_touches3)
    """
    print(f"⏳ Слушаю экран {timeout} секунд. Касайся экрана!")
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
                    print(f"📍 X = {last_x}")
                elif "ABS_MT_POSITION_Y" in line:
                    last_y = round(int(line.split()[-1], 16) / SCALE_Y)
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
    """Записывает сырой лог касаний (getevent) в текстовый файл."""
    print(f"⏳ Запись лога {timeout} сек. Файл: {filename}")
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
        print("\n✅ Запись остановлена вручную")
    finally:
        process.terminate()
    
    print(f"✅ Запись завершена! Строк: {lines_count}. Файл: {filename}")
    return filename


def parse_touch_log(filename="touchscreen_log.txt"):
    """
    Парсит записанный лог и извлекает усредненные координаты касаний.
    
    Returns:
        list: Список словарей с данными о каждом касании.
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Файл {filename} не найден")
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
    
    print(f"✅ Всего касаний: {len(results)}")
    return results


# ==============================================================================
# [5] КОМПЬЮТЕРНОЕ ЗРЕНИЕ И АВТОМАТИЗАЦИЯ (OPENCV)
# ==============================================================================

def click_start_if_found(template_path="button_start.png", threshold=0.8, 
                         debug=False, debug_path=None):
    """
    Находит шаблон на экране Android-устройства.
    
    Режимы работы:
        - debug=False (по умолчанию): находит и тапает по центру шаблона.
        - debug=True: НЕ тапает, а рисует рамку вокруг найденного 
          и сохраняет скриншот в debug_path (режим отладки).
    
    Args:
        template_path: путь к PNG-файлу шаблона.
        threshold: минимальная уверенность совпадения (0..1).
        debug: если True — режим отладки (без клика, с сохранением скрина).
        debug_path: путь для сохранения. Если None — сохраняется в 
                    screenshot/debug_<timestamp>.png автоматически.
    
    Returns:
        bool: True, если шаблон найден, иначе False.
    """
    import time
    from pathlib import Path
    
    # 1. Читаем шаблон
    template = cv2.imread(template_path)
    if template is None:
        print(f"❌ Не найден файл шаблона: {template_path}")
        return False

    # 2. Делаем скриншот через ADB
    raw_bytes = subprocess.run(
        ["adb", "exec-out", "screencap", "-p"],
        stdout=subprocess.PIPE, check=True
    ).stdout

    # 3. Декодируем в numpy-массив
    screen = cv2.imdecode(np.frombuffer(raw_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
    if screen is None:
        print(" Не удалось декодировать скриншот. Проверьте подключение.")
        return False

    # 4. Ищем шаблон
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    # 5. Если нашли — обрабатываем
    if max_val >= threshold:
        h, w = template.shape[:2]
        cx = max_loc[0] + w // 2
        cy = max_loc[1] + h // 2

        if debug:
            # 🛠️ РЕЖИМ ОТЛАДКИ: рисуем рамку и сохраняем
            x1, y1 = max_loc[0], max_loc[1]
            x2, y2 = max_loc[0] + w, max_loc[1] + h
            debug_img = screen.copy()
            cv2.rectangle(debug_img, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.putText(debug_img, f"OK: {max_val:.2f}", 
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.8, (0, 255, 0), 2)
            
            # Если путь не задан — формируем автоматически
            if debug_path is None:
                debug_dir = Path("screenshot")
                debug_dir.mkdir(exist_ok=True)
                debug_path = str(debug_dir / f"debug_{int(time.time())}.png")
            
            cv2.imwrite(debug_path, debug_img)
            print(f"🛠️ [DEBUG] Найдено! Уверенность: {max_val:.3f}")
            print(f"🛠️ [DEBUG] Центр: ({cx}, {cy})")
            print(f"🛠️ [DEBUG] Скрин с рамкой сохранён: {debug_path}")
        else:
            # 🎯 ОБЫЧНЫЙ РЕЖИМ: тапаем
            print(f"\n✅ НАЙДЕНО! Уверенность: {max_val:.3f}")
            subprocess.run(
                ["adb", "shell", "input", "tap", str(cx), str(cy)],
                stdout=subprocess.PIPE, check=True
            )
            print(f"👆 Тап в ({cx}, {cy})")
        return True
    else:
        print(f"\n❌ НЕ найдено (порог {threshold} > {max_val:.3f})")
        return False


def find_template(screen, template, threshold=0.85, roi=None):
    """
    Ищет шаблон на numpy-массиве экрана.
    
    Args:
        roi (tuple): (x1, y1, x2, y2) — область поиска. Если None, ищет по всему экрану.
    Returns:
        tuple: (cx, cy) центра шаблона или None.
    """
    h, w = template.shape[:2]
    x1, y1 = (0, 0) if roi is None else roi[:2]
    sub = screen[y1:roi[3], x1:roi[2]] if roi else screen

    if sub.shape[0] < h or sub.shape[1] < w:
        return None  # Шаблон больше области поиска

    result = cv2.matchTemplate(sub, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        return (max_loc[0] + w // 2 + x1, max_loc[1] + h // 2 + y1)
    return None


def wait_for_template(template, timeout=30, interval=1.0, threshold=0.85, roi=None):
    """Ждёт появления шаблона на экране с заданным таймаутом."""
    t0 = time.perf_counter()
    while True:
        screen = grab_screen()
        if screen is not None:
            pos = find_template(screen, template, threshold, roi)
            if pos is not None:
                return pos
        if time.perf_counter() - t0 > timeout:
            return None
        time.sleep(interval)


# ==============================================================================
# [6] УТИЛИТЫ ОТЛАДКИ
# ==============================================================================

def draw_tap(input_path, output_path, x, y, radius=25, color='red'):
    """Рисует закрашенный круг (точку тапа) на изображении через PIL."""
    img = Image.open(input_path)
    ImageDraw.Draw(img).ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    img.save(output_path)


def draw_roi(screen, roi, output_path="debug_roi.png"):
    """Рисует прямоугольник ROI на скриншоте (numpy) и сохраняет его."""
    if roi is None:
        print("⚠️ ROI не задан, нечего рисовать")
        return
    
    x1, y1, x2, y2 = roi
    debug_img = screen.copy()
    cv2.rectangle(debug_img, (x1, y1), (x2, y2), (0, 255, 0), 3)
    cv2.putText(debug_img, f"ROI: ({x1},{y1})-({x2},{y2})", 
                (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.imwrite(output_path, debug_img)
    print(f"✅ ROI нарисован и сохранен: {output_path}")


# ==============================================================================
# [7] ШПАРГАЛКА / ЗАГОТОВКИ (Не выполняется при импорте)
# ==============================================================================
if __name__ == "__main__":
    # Пример замера времени выполнения функции:
    # t0 = time.perf_counter()
    # grab_screen()
    # print(f"Выполнено за: {(time.perf_counter() - t0) * 1000:.0f} мс")
    
    print(f"Модуль adb_utils v{__version__} загружен. Запустите функции напрямую.")
