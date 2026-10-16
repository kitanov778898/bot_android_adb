"""
Бенчмарк скорости поиска шаблона (с диска).
Сравнивает поиск в цвете (BGR) и в чёрно-белом (Grayscale).
Версия: 1.0.0
"""

import cv2
import time
import numpy as np
from pathlib import Path

# ==============================================================================
# [1] НАСТРОЙКИ
# ==============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
UI_PATH = PROJECT_ROOT / "assets" / "search_ui_components"
SCREENSHOT_DIR = PROJECT_ROOT / "src" / "screenshot"

# Имя файла скриншота (должен лежать в папке src/screenshot/)
SCREENSHOT_NAME = "in.png"
SCREEN_PATH = SCREENSHOT_DIR / SCREENSHOT_NAME

# Имя шаблона (должен лежать в assets/search_ui_components/)
TEMPLATE_NAME = "button_СТАРТ.png"
TEMPLATE_PATH = UI_PATH / TEMPLATE_NAME

ITERATIONS = 50  # Количество повторений для точности

# ==============================================================================
# [2] ЗАГРУЗКА ИЗОБРАЖЕНИЙ
# ==============================================================================

print(f"\n  БЕНЧМАРК v1.0.0 -")
print(f"Скриншот: {SCREENSHOT_NAME}")
print(f"Шаблон:   {TEMPLATE_NAME}")
print(f"Итераций: {ITERATIONS}\n")

# Загружаем скриншот
img_bgr = cv2.imread(str(SCREEN_PATH))
if img_bgr is None:
    print(f" ОШИБКА: Не удалось загрузить скриншот '{SCREEN_PATH}'")
    print(f"   Убедись, что файл 'in.png' существует в папке src/screenshot/")
    exit(1)

# Загружаем шаблон
tpl_bgr = cv2.imread(str(TEMPLATE_PATH))
if tpl_bgr is None:
    print(f" ОШИБКА: Не удалось загрузить шаблон '{TEMPLATE_PATH}'")
    exit(1)

print(f" Изображения загружены.")
print(f"   Размер экрана: {img_bgr.shape[1]}x{img_bgr.shape[0]}")
print(f"   Размер шаблона: {tpl_bgr.shape[1]}x{tpl_bgr.shape[0]}\n")

# Конвертируем в Ч/Б ОДИН РАЗ перед циклом (чтобы замерять только поиск)
img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
tpl_gray = cv2.cvtColor(tpl_bgr, cv2.COLOR_BGR2GRAY)


# ==============================================================================
# [3] ЗАМЕРЫ СКОРОСТИ
# ==============================================================================

print(f" Замер в ЦВЕТЕ (BGR)...")
times_bgr = []
for _ in range(ITERATIONS):
    t0 = time.perf_counter()
    # Сам поиск шаблона
    cv2.matchTemplate(img_bgr, tpl_bgr, cv2.TM_CCOEFF_NORMED)
    t1 = time.perf_counter()
    times_bgr.append((t1 - t0) * 1000)  # Переводим в миллисекунды

print(f" Замер в Ч/Б (Grayscale)...")
times_gray = []
for _ in range(ITERATIONS):
    t0 = time.perf_counter()
    # Сам поиск шаблона
    cv2.matchTemplate(img_gray, tpl_gray, cv2.TM_CCOEFF_NORMED)
    t1 = time.perf_counter()
    times_gray.append((t1 - t0) * 1000)


# ==============================================================================
# [4] ОБРАБОТКА РЕЗУЛЬТАТОВ
# ==============================================================================

avg_bgr = np.mean(times_bgr)
avg_gray = np.mean(times_gray)
min_bgr = np.min(times_bgr)
min_gray = np.min(times_gray)
max_bgr = np.max(times_bgr)
max_gray = np.max(times_gray)

# Расчёт ускорения
speedup = avg_bgr / avg_gray if avg_gray > 0 else 0
percent_faster = ((avg_bgr - avg_gray) / avg_bgr * 100) if avg_bgr > 0 else 0


# ==============================================================================
# [5] ВЫВОД
# ==============================================================================

print(f"\n{'='*55}")
print(f" РЕЗУЛЬТАТЫ ({ITERATIONS} итераций)")
print(f"{'='*55}")
print(f"{'Метрика':<18} {'ЦВЕТ (BGR) мс':<18} {'Ч/Б (Gray) мс':<18}")
print(f"{'-'*55}")
print(f"{'Среднее (Avg)':<18} {avg_bgr:<18.3f} {avg_gray:<18.3f}")
print(f"{'Минимум (Min)':<18} {min_bgr:<18.3f} {min_gray:<18.3f}")
print(f"{'Максимум (Max)':<18} {max_bgr:<18.3f} {max_gray:<18.3f}")
print(f"{'='*55}")

print(f"\n Grayscale быстрее в {speedup:.2f}x раз")
print(f" Экономия времени на одном поиске: {percent_faster:.1f}%")

if percent_faster > 20:
    print(f"\n РЕКОМЕНДАЦИЯ: Однозначно переходить на Grayscale в основном коде!")
else:
    print(f"\n Разница незначительная. Можно оставить цвет или искать другие оптимизации (например, ROI).")

print(f"\n  БЕНЧМАРК ЗАВЕРШЁН -\n")
