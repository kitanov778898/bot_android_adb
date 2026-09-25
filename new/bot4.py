import cv2
import time
from config import START_ROI
from adb_tools import grab_screen, find_template, tap, run_game

def main():
    # 1. Загружаем шаблон ОДИН раз при старте
    template = cv2.imread("button_start.png", cv2.IMREAD_COLOR)
    if template is None:
        print("❌ Ошибка: нет файла button_start.png в папке!")
        return
    print(f"✅ Шаблон загружен, размер: {template.shape}")

    # 2. Запускаем игру
    print("🚀 Запускаем игру...")
    run_game()
    
    # 3. Даём время на загрузку (сплеш-скрины, логотипы, загрузочный экран)
    # Для Hill Climb Racing обычно нужно 5-10 секунд
    print("⏳ Ждём первоначальную загрузку игры (10 секунд)...")
    time.sleep(10)

    # 4. Ждём появления кнопки START
    print("🔍 Ищем кнопку START (таймаут 30 сек)...")
    start_time = time.perf_counter()
    timeout = 30
    interval = 1.0  # проверяем раз в секунду
    
    found = False
    while True:
        elapsed = time.perf_counter() - start_time
        if elapsed > timeout:
            print("⏰ Таймаут: кнопка START не появилась за 30 секунд.")
            
            # 🔥 КЛЮЧЕВАЯ ДИАГНОСТИКА: сохраняем последний кадр
            last_screen = grab_screen()
            if last_screen is not None:
                cv2.imwrite("debug_last_screen.png", last_screen)
                print("💡 Сохранил последний экран в debug_last_screen.png")
                print("   👉 ОТКРОЙ ЭТОТ ФАЙЛ! Там ты увидишь, что именно видел бот.")
            break

        screen = grab_screen()
        if screen is None:
            print("⚠️ Не удалось получить экран, пробую снова...")
            time.sleep(interval)
            continue

        # Ищем с учётом ROI (если ROI задан в config.py)
        pos = find_template(screen, template, threshold=0.85, roi=START_ROI)
        
        if pos is not None:
            cx, cy = pos
            print(f"✅ Нашёл START на координатах ({cx}, {cy})!")
            print("👆 Делаем тап...")
            tap(cx, cy)
            found = True
            break

        # Для спокойствия выводим прогресс каждые 5 секунд
        if int(elapsed) % 5 == 0 and int(elapsed) > 0:
            print(f"⏳ Прошло {int(elapsed)} сек, пока не вижу START...")
            
        time.sleep(interval)

    if found:
        print("🎉 Бот успешно нажал START! Миссия выполнена.")
    else:
        print("❌ Бот не смог нажать START. Смотри debug_last_screen.png и проверяй ROI.")

if __name__ == "__main__":
    main()
