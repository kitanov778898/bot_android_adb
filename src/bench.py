"""
Замер скорости разных способов получить экран и найти шаблон.
Запуск: python bench.py
Требует: устройство подключено, есть button_start.png в папке.
"""
import subprocess
import time
import cv2
import numpy as np
from config import SCREEN_W, SCREEN_H


N = 10  # сколько прогонов на каждый режим


# ---------- Способы получить экран ----------

def screen_png_file(filename="_bench.png"):
    """Старый способ: PNG -> файл на диске."""
    subprocess.run(
        ["adb", "exec-out", "screencap", "-p"],
        stdout=open(filename, "wb"),
    )


def screen_png_memory():
    """PNG -> imdecode в памяти, без файла."""
    result = subprocess.run(
        ["adb", "exec-out", "screencap", "-p"],
        capture_output=True,
    )
    if result.returncode != 0 or not result.stdout:
        return None
    raw = np.frombuffer(result.stdout, dtype=np.uint8)
    return cv2.imdecode(raw, cv2.IMREAD_COLOR)


def screen_raw_memory():
    """Raw screencap -> reshape -> BGR. Заголовок вычисляется."""
    result = subprocess.run(
        ["adb", "exec-out", "screencap"],
        capture_output=True,
    )
    if result.returncode != 0 or not result.stdout:
        return None
    raw = np.frombuffer(result.stdout, dtype=np.uint8)
    pixels = SCREEN_W * SCREEN_H * 4
    header = len(raw) - pixels
    if header < 0:
        return None
    img = raw[header:].reshape((SCREEN_H, SCREEN_W, 4))
    return cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)


# ---------- Замер ----------

def bench(name, fn, n=N):
    """Прогоняет fn n раз, возвращает (среднее_мс, минимум_мс)."""
    times = []
    for _ in range(n):
        t0 = time.perf_counter()
        fn()
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)
    avg = sum(times) / len(times)
    mn = min(times)
    mx = max(times)
    print(f"{name:<28} avg={avg:>7.1f}  min={mn:>7.1f}  max={mx:>7.1f}  (мс)")
    return avg


# ---------- Режимы поиска шаблона ----------

def load_template():
    t = cv2.imread("button_start.png", cv2.IMREAD_COLOR)
    if t is None:
        print("❌ Нет button_start.png — вырезать сначала")
        raise SystemExit(1)
    return t


def find_full_color(screen, template):
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    return max_val


def find_roi_color(screen, template, roi):
    x1, y1, x2, y2 = roi
    sub = screen[y1:y2, x1:x2]
    result = cv2.matchTemplate(sub, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    return max_val


def find_full_gray(screen, template):
    gs = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    gt = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(gs, gt, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    return max_val


# ---------- Основной прогон ----------

def main():
    print(f"Замер: {N} прогонов на каждый режим\n")

    print("=== Получение экрана ===")
    bench("PNG -> файл",         screen_png_file)
    bench("PNG -> imdecode",     screen_png_memory)
    bench("Raw -> reshape",      screen_raw_memory)

    # готовые картинки для тестов поиска
    print("\nГотовлю образцы...")
    screen_raw = screen_raw_memory()
    if screen_raw is None:
        print("❌ Не получили raw — дальше не идём")
        return
    template = load_template()
    print(f"screen: {screen_raw.shape}, template: {template.shape}\n")

    print("=== Поиск шаблона (по готовому screen) ===")
    bench("full color",
          lambda: find_full_color(screen_raw, template))
    bench("full gray",
          lambda: find_full_gray(screen_raw, template))
    # ROI — верхний правый угол, подгони под свой экран
    roi = (1400, 50, 1900, 350)
    bench(f"ROI color {roi}",
          lambda: find_roi_color(screen_raw, template, roi))

    print("\nГотово.")


if __name__ == "__main__":
    main()