"""
Скрипт автоматизации игры v1.4.0
Разблокировка → запуск → поиск кнопок → поиск машины.
"""
import csv
import cv2  # <-- ДОБАВИТЬ ЭТО В НАЧАЛО ФАЙЛА (рядом с другими импортами)
import time
import numpy as np
from pathlib import Path
from adb_tools import (
    run_game,
    tap,
    screenshot,
    wait_for_template,
    find_template,
    check_and_unlock_screen,
    grab_screen,
    grab_screen_gray,
    measure_time,
)

__version__ = "1.4.0"

# Пути
PROJECT_ROOT = Path(__file__).resolve().parent.parent
UI_PATH = PROJECT_ROOT / "assets" / "search_ui_components"
SCREENSHOT_DIR = PROJECT_ROOT / "src" / "screenshot"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

# Шаблоны (внимательно: только латиница в именах!)
TEMPLATE_START = UI_PATH / "button_СТАРТ.png"
TEMPLATE_START_2 = UI_PATH / "button_СТАРТ_2.png"
TEMPLATE_END = UI_PATH / "button_end.png"
TEMPLATE_CAR = UI_PATH / "car_truck.png"  

# Координаты
TARGET_X, TARGET_Y = 1670, 1000
ROI_CAR = ( 140, 300, 860, 1200 )


# ==============================================================================
# ЭТАП 1: РАЗБЛОКИРОВКА + ЗАПУСК ИГРЫ
# ==============================================================================

@measure_time
def step_1() -> int:
    """Разблокировка экрана + запуск игры.
    Проверяет, что экран меняется после каждого действия.
    Возвращает 0 — успех, 1 — ошибка.
    """
    check_and_unlock_screen()
    #buf_screen = grab_screen()
    # тут нужна проверка что игра запущена функция 
    run_game()
    time.sleep(5)
    #buf_screen_new = grab_screen()
    #if np.array_equal(buf_screen_new, buf_screen):
    #    print("❌ Экран не изменился после запуска игры")
    #    return 1
    print("🚀 Игра успешно запущена")
    return 0

@measure_time
def step_2() -> int:
    """Ищем шаблон машины и провереям мщем сасый быстрый пооиск шаблона.
    Возвращает 0 — успех, 1 — ошибка.
    """
    pass
    screen = grab_screen()
    car_pos = find_template(screen, str(TEMPLATE_CAR), threshold=0.65, roi=ROI_CAR)
    if car_pos:
        print(f"✅ Машина найдена: {car_pos}")
        return 0
    else:
        print("❌ Машина не найдена")
        return 1

@measure_time
def step_3() -> int:
    """Создаёт сетку 25x25, сохраняет данные о яркости и картинку с сеткой."""
    screen = grab_screen()
    if screen is None:
        print("❌ Не удалось получить скриншот")
        return 1
    
    h, w = screen.shape[:2]
    step = 25
    
    # Если изображение черно-белое (2D-массив), конвертируем в цветное для рисования зеленых линий
    if len(screen.shape) == 2:
        vis_screen = cv2.cvtColor(screen, cv2.COLOR_GRAY2BGR)
    else:
        vis_screen = screen.copy()
    
    grid_file = SCREENSHOT_DIR / "grid_25x25.csv"
    grid_img_file = SCREENSHOT_DIR / "grid_visualization.png"
    
    with open(grid_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["x_center", "y_center", "avg_brightness"])
        
        for y in range(0, h, step):
            # Рисуем горизонтальную линию
            cv2.line(vis_screen, (0, y), (w, y), (0, 255, 0), 1)
            
            for x in range(0, w, step):
                # Рисуем вертикальную линию
                if y == 0:  # Чтобы не рисовать вертикальные линии повторно на каждом шаге Y
                    cv2.line(vis_screen, (x, 0), (x, h), (0, 255, 0), 1)
                
                cell = screen[y:y+step, x:x+step]
                avg = int(cell.mean())
                cx = x + step // 2
                cy = y + step // 2
                writer.writerow([cx, cy, avg])
    
    # Сохраняем изображение с нарисованной сеткой
    cv2.imwrite(str(grid_img_file), vis_screen)
    
    print(f"✅ Сетка 25x25 сохранена: {grid_file}")
    print(f"🖼️ Картинка с сеткой сохранена: {grid_img_file}")
    print(f"📊 Ячеек: {(w // step) * (h // step)}")
    return 0
       

# ==============================================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ==============================================================================

def main() -> int:
    """Главная точка входа. Возвращает 0 — успех, 1 — ошибка."""
    print("🚀 Начало работы скрипта")

    # Этап 1: разблокировка + запуск
    if step_1() != 0:
        return 1

    # Этап 2: первая кнопка СТАРТ
    buf_screen = grab_screen()
    pos = wait_for_template(str(TEMPLATE_START), timeout=20, threshold=0.80)
    if not pos:
        print("❌ Кнопка СТАРТ не найдена")
        return 1
    tap(*pos)

    buf_screen_new = grab_screen()
    if not np.array_equal(buf_screen_new, buf_screen):
        print("✅ Экран изменился после СТАРТ")
    else:
        print("❌ Экран не изменился после СТАРТ")
        return 1

    # Этап 3: вторая кнопка СТАРТ
    buf_screen = buf_screen_new
    pos = wait_for_template(str(TEMPLATE_START_2), timeout=20, threshold=0.80)
    if not pos:
        print("❌ Кнопка СТАРТ_2 не найдена")
        return 1
    tap(*pos)

    buf_screen_new = grab_screen()
    if not np.array_equal(buf_screen_new, buf_screen):
        print("✅ Экран изменился после СТАРТ_2")
    else:
        print("❌ Экран не изменился после СТАРТ_2")
        return 1

    # Этап 4: поиск машины
    step_2()
    time.sleep(2)
    
    # Этап 4: сетка 25x25
    if step_3() != 0:
        return 1
    
    
    # Финальный скриншот
    #screenshot(str(SCREENSHOT_DIR / "final_1.png"))
    print("✅ Готово")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())