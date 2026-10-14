import os
import time
import uiautomator2 as u2

def main():
    # 1. Сначала жестко закрываем настройки, чтобы сбросить положение экрана
    print("[*] Закрываем старое окно настроек...")
    os.system("am force-stop com.android.settings")
    time.sleep(1)

    # 2. Открываем настройки разработчика с самого начала
    print("[*] Открываем настройки «с нуля»...")
    os.system("am start -a android.settings.APPLICATION_DEVELOPMENT_SETTINGS")
    time.sleep(3) # Даем время на чистую загрузку страницы

    d = u2.connect()
    target = "Отладка по WLAN"

    # 3. Проверяем, виден ли пункт. Если нет — запускаем автоскролл
    if not d(text=target).exists:
        print(f"[*] Пункт '{target}' скрыт. Запускаем автоматическую прокрутку...")
        
        # Находим любой скроллируемый контейнер на экране и крутим его до текста
        if d(scrollable=True).exists:
            # Метод scroll.to сам будет крутить страницу вниз, пока не упрется в текст
            d(scrollable=True).scroll.to(text=target)
            print("[+] Скролл завершен, элемент найден!")
        else:
            print("[-] Квадрат скролла не найден. Пробуем свайпнуть вручную...")
            # Если автоскролл не сработал, делаем жест свайпа снизу вверх
            d.swipe(500, 1000, 500, 300, steps=10)
            time.sleep(1)

    # 4. Проверяем итоговое положение элемента после прокрутки
    if d(text=target).exists:
        print(f"\n[🎉] ЭЛЕМЕНТ УСПЕШНО НАЙДЕН ПОСЛЕ ПЕРЕОТКРЫТИЯ!")
        print(f"Новые координаты bounds: {d(text=target).info['bounds']}")
    else:
        print(f"[-] Ошибка: Не удалось найти пункт '{target}' на чистом экране.")

if __name__ == "__main__":
    main()
