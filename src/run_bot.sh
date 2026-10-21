#!/bin/bash
script="bot2.py"
read -p "Сколько раз запустить? " count
brightness=$(adb shell settings get system screen_brightness)
adb shell settings put system screen_brightness 1

echo " Запускаю $count циклов..."
for ((i=1; i<=count; i++)); do
    echo "--- Запуск $i ---"
    python "$script"
done
adb shell settings put system screen_brightness "$brightness"
echo " Готово!"
