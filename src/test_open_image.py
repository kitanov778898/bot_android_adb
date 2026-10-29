from adb_tools import speak_text

__version__ = "1.4.0"

import matplotlib

# Указываем интерактивный бэкенд (TkAgg или Qt5Agg)
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import time
import os
import cv2
import subprocess
import numpy as np
from PIL import Image
from pathlib import Path
from adb_tools import measure_time,grab_screen, grab_screen_gray

PUT = Path(
    "/data/data/com.termux/files/home/storage/downloads/bot_android_adb/src/screenshot/zzzz1.png"
)
BASE_DIR = Path(__file__).parent  # полуим путь как обет откуда открыли файл скрипта
F = Path("zzzz1.png")  # Объект Path (pathlib.Path)


@measure_time
def test_function():
    time.sleep(0.5)  # Имитация работы


def test_1():
    # --- путь к текушей папке ---
    print(f"Путь :  {BASE_DIR}")

    if (PUT).exists():
        print("Файл существует.")
        with Image.open(PUT) as img:
            print(f"Размер: {img.size}")
            print(f"Режим: {img.mode}")
            print(f"Формат: {img.format}")
            # Показываем изображение

            # Показываем изображение через matplotlib (надёжно работает через SSH X11)
            plt.figure(figsize=(8, 6))  # Задаём размер окна на компьютере
            plt.imshow(img)
            plt.axis("off")  # Убираем оси координат
            plt.title("Изображение с планшета через SSH X11")

            print("🖼️ Открываю окно ... (закрой его крестиком, чтобы продолжить)")
            plt.show(
                block=True
            )  # <--- ВАЖНО: block=True по умолчанию. Ждёт закрытия окна
            plt.close()  # Освобождаем память

            # ЭТАП 2: ПРЕОБРАЗОВАНИЯ (после того, как ты закрыл окно)
            box = (
                10,
                10,
                640,
                340,
            )  # лево, верх, право, низ - Вырезаем кусочек изображения
            # new_img = img.crop(box)
            # Квантуем до 8 цветов
            img_8 = img.quantize(colors=10)
            new_img = img_8.convert("1")  # Сделать чёрно-белым

            # Здесь можно добавить другие преобразования, например:
            # new_img = new_img.rotate(45)                    # Повернуть на 45°
            # new_img = new_img.convert('L')                  # Сделать чёрно-белым оттенки серого
            # new_img = new_img.convert('1')                  # Сделать чёрно-белым
            # new_img = new_img.resize((320, 170))            # Изменить размер
            # new_img = new_img.filter(ImageFilter.BLUR)      # Размыть

            # ЭТАП 3: СОХРАНЯЕМ РЕЗУЛЬТАТ
            # save_path = PUT.parent / "my_test.png"
            # new_img.save(save_path)

            # ЭТАП 4: ПОКАЗЫВАЕМ РЕЗУЛЬТАТ
            plt.figure(figsize=(8, 6))
            # plt.figure(figsize=(16, 9), dpi='figure')  # dpi подстроится под экран
            # Для TkAgg бэкенда:
            # fig.canvas.manager.full_screen()  # Развернуть на весь экран
            plt.imshow(new_img)
            plt.title("РЕЗУЛЬТАТ преобразований")
            plt.show()  # Ждём закрытия
            plt.close()  # Освобождаем память

    else:
        print("Файла нет.")


def show_demo():
    with Image.open(PUT) as img:
        # 1. Оттенки серого (256 цветов)
        img_gray = img.convert("L")

        # 2. Строго ч/б (2 цвета, без серого)
        img_bw = img_gray.point(lambda p: 255 if p > 128 else 0)

        # 3. Квантование до 8 цветов
        img_8 = img.quantize(colors=8).convert("RGB")

        # Показываем все 3
        show_comparison(
            images=[img, img_gray, img_bw, img_8],
            titles=["Оригинал", "Серый (L)", "Ч/Б (1)", "8 цветов"],
            layout="horizontal",
        )


def show_comparison(images, titles=None, layout="horizontal"):
    """
    Показывает несколько картинок для сравнения.
    Автоматически определяет cmap для ч/б изображений.
    """
    n = len(images)

    if layout == "horizontal":
        fig = plt.figure(figsize=(5 * n, 5), dpi=100)
        for i, img in enumerate(images, 1):
            plt.subplot(1, n, i)

            # 🔥 МАГИЯ: проверяем режим картинки
            if img.mode in ("L", "1"):  # Ч/Б или оттенки серого
                plt.imshow(img, cmap="gray")  # ← Используем серый cmap
            else:  # Цветная (RGB, RGBA)
                plt.imshow(img)  # ← Обычный показ

            plt.title(titles[i - 1] if titles else f"#{i}")
            plt.axis("off")
    else:  # vertical
        fig = plt.figure(figsize=(5, 5 * n), dpi=100)
        for i, img in enumerate(images, 1):
            plt.subplot(n, 1, i)

            # 🔥 Та же проверка
            if img.mode in ("L", "1"):
                plt.imshow(img, cmap="gray")
            else:
                plt.imshow(img)

            plt.title(titles[i - 1] if titles else f"#{i}")
            plt.axis("off")

    plt.tight_layout()
    plt.show()
    plt.close()


@measure_time
def main():
    """Главная функция — точка входа в программу"""
    print("--- старт ---")
    if PUT.exists():
        with Image.open(PUT) as img:
            print(f"Размер: {img.size}")
            print(f"Режим: {img.mode}")
            print(f"Формат: {img.format}")
            img.show()  # открыть в новом окне
            # --- пробуем вырезать кусочек изображения ---
            box = (10, 10, 640, 340)  # лево, верх, право, низ
            new_img = img.crop(box)
            new_img.show()
            new_img.save("screenshot/my_test.png")
    else:
        print("Файла нет.")
    print("--- конец ---")


if __name__ == "__main__":
    # Этот код выполнится, только если запустить скрипт напрямую

    # main()

    # 1. путь к исходному файлу

    IN_F = Path(
        "/data/data/com.termux/files/home/storage/downloads/bot_android_adb/src/screenshot/zzzz1.png"
    )

    SEARCH = Path(
        "/data/data/com.termux/files/home/storage/downloads/bot_android_adb/assets/search_ui_components/button_СТАРТ.png"
    )
    # 2. проверка наличия (True/False)
    file_exists_1 = os.path.exists(IN_F)
    file_exists_2 = os.path.exists(SEARCH)

    # 3. изображение в памяти  cv2
    img_1 = cv2.imread(IN_F)
    img_2 = cv2.imread(SEARCH)
    #


    # Вызов функции (декоратор уже сработает внутри, при вызове)
    img_scr_1 = grab_screen()
    img_scr_2 = grab_screen_gray()


