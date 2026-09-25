import cv2
from adb_tools import grab_screen, find_template
from config import START_ROI

def main():
    # 1. Читаем шаблон
    template = cv2.imread("button_start.png", cv2.IMREAD_COLOR)
    if template is None:
        print("❌ Нет button_start.png")
        return
    print(f"Шаблон: {template.shape}")

    # 2. Делаем скриншот
    screen = grab_screen()
    if screen is None:
        print("❌ Не получили экран")
        return
    print(f"Экран: {screen.shape}")

    # 3. Проверяем ROI
    x1, y1, x2, y2 = START_ROI
    print(f"ROI: ({x1},{y1}) -> ({x2},{y2}), размер={x2-x1}x{y2-y1}")

    h, w = screen.shape[:2]
    if x1 < 0 or y1 < 0 or x2 > w or y2 > h:
        print(f"⚠️ ROI выходит за экран ({w}x{h})!")

    # 4. Сохраняем ROI в файл — смотрим глазами
    roi_img = screen[y1:y2, x1:x2]
    cv2.imwrite("debug_roi.png", roi_img)
    print("✅ Сохранил ROI в debug_roi.png — откройте и посмотрите")

    # 5. Ищем по всему экрану (без ROI)
    pos_full = find_template(screen, template, threshold=0.85)
    print(f"\nПоиск по всему экрану: {pos_full}")

    # 6. Ищем по ROI
    pos_roi = find_template(screen, template, threshold=0.85, roi=START_ROI)
    print(f"Поиск по ROI: {pos_roi}")

    # 7. Анализ
    if pos_full is not None and pos_roi is None:
        cx, cy = pos_full
        if not (x1 <= cx <= x2 and y1 <= cy <= y2):
            print(f"\n⚠️ Кнопка на ({cx},{cy}) — ВНЕ ROI!")
            print("   Нужно расширить ROI или подогнать координаты.")
    elif pos_full is None:
        print("\n⚠️ Кнопка не найдена даже по всему экрану.")
        print("   Возможные причины:")
        print("   - button_start.png вырезан из другого экрана/версии игры")
        print("   - кнопка ещё не появилась (игра не загрузилась)")
        print("   - попробуйте threshold=0.7")

if __name__ == "__main__":
    main()