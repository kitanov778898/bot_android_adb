#!/bin/bash

# Информация о скрипте
VERSION="1.2.0"
AUTHOR="Китанов Виктор"

adb start-server

echo "=== ШАГ 1: Включаем отладку в настройках ==="
echo "Сейчас откроются настройки. Найди пункт 'Отладка по WLAN' и включи его."
echo ""

# Открываем меню разработчика Android
adb shell am start -a android.settings.APPLICATION_DEVELOPMENT_SETTINGS > /dev/null 2>&1

read -p "Как включишь отладку, возвращайся сюда и жми Enter..."

echo ""
echo "=== ШАГ 2: Ищем порт отладки ==="
echo "Сканируем порты, подожди 2-3 секунды..."

# Ищем порт в диапазоне 30000-45000, где Android всегда включает WLAN-отладку
PORT=$(nmap -sT -p 30000-45000 localhost | grep "open" | head -n 1 | cut -d'/' -f1)

# Проверяем, удалось ли найти порт автоматически
if [ -z "$PORT" ]; then
    echo "⚠️ Не удалось найти порт автоматически (возможно, отладка не включена)."
    echo "Пожалуйста, посмотри на экран телефона в настройки 'Отладка по WLAN'."
    echo "Введи пятизначный порт вручную (цифры после localhost:) и нажми Enter:"
    read PORT
fi

# Если порт пустой и после ручного ввода, останавливаем скрипт
if [ -z "$PORT" ]; then
    echo "❌ Порт не введен. Выход."
    exit 1
fi

echo "🎯 Найден порт отладки: $PORT"
echo ""
echo "=== ШАГ 3: Подключение к ADB ==="

# Подключаемся к локальному порту
adb connect localhost:$PORT

echo ""
echo "=== ШАГ 4: Проверка списка устройств ==="
adb devices

echo ""
echo "=== ШАГ 5: Защита SSH-сессий от падения ==="
echo "Настраиваем лимит фоновых процессов, чтобы Android не убивал бота..."

# 📝 ЗАМЕТКА ДЛЯ СЕБЯ НА БУДУЩЕЕ:
# Периодически наблюдался внезапный обрыв фоновой SSH-сессии при сворачивании Termux.
# Анализ системного лога (adb logcat) показал ошибку: "Process PhantomProcessRecord ... died".
# Причина: Android по умолчанию жестко убивает скрытые (фантомные) дочерние процессы, 
# если их лимит превышает 32 на всё устройство.
# Чтобы сессии не отваливались, увеличиваем этот лимит в 4 раза — с 32 до 128.

# Меняем настройки «инспектора» Android
adb shell device_config put activity_manager max_phantom_processes 128
adb shell settings put global settings_enable_monitor_phantom_procs true

# Проверяем, сколько процессов сейчас запущено для контроля
echo "Проверка: сейчас в фоне работает фантомных процессов:"
adb shell dumpsys activity processes | grep "PhantomProcessRecord" | wc -l

echo ""
echo "🎉 Готово! Если в Шаге 4 написано 'device', то кликер и фоновый SSH готовы к работе."
