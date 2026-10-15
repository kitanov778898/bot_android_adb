# 📱 ADB: Полное руководство

## 1. Переменные окружения
Задай переменные, чтобы не повторять IP и package name:
\`\`\`bash
DEVICE="192.168.10.185:45107" # Замени на актуальный IP:порт из "Беспроводная отладка"
APP="com.fingersoft.hillclimb"
\`\`\`

## 2. Подключение
\`\`\`bash
adb devices                  # Список устройств
adb connect \$DEVICE          # Подключиться по WiFi
adb disconnect \$DEVICE       # Отключиться
adb kill-server && adb start-server # Перезапуск сервера при глюках
\`\`\`

## 3. Управление приложениями
\`\`\`bash
# Запуск с поднятием существующего экземпляра (без перезапуска жизненного цикла)
adb shell am start -f 0x00020000 -n \$APP/com.fingersoft.game.MainActivity

# Альтернативный запуск (monkey)
adb shell monkey -p \$APP 1

# Принудительная остановка
adb shell am force-stop \$APP

# Проверка активного окна
adb shell dumpsys window | grep mCurrentFocus
\`\`\`

## 4. Касания и ввод (INPUT)
⚠️ **КРИТИЧЕСКОЕ ОГРАНИЧЕНИЕ**: На POCO/Xiaomi через WiFi ADB команды \`input tap/swipe\` выдают \`java.lang.SecurityException: INJECT_EVENTS permission denied\`. Они работают **ТОЛЬКО** по USB с ПК.
\`\`\`bash
adb shell input tap 540 1200          # Клик по координатам X Y
adb shell input swipe 100 500 100 100 # Свайп
adb shell input text "hello"          # Ввод текста
adb shell input keyevent 4            # Назад (3 = Домой, 26 = Блокировка)
\`\`\`

## 5. Скриншоты и Видео
\`\`\`bash
# Надежный скриншот (сохраняется на устройстве, откуда выполняется команда)
adb exec-out screencap -p > screen.png

# Запись экрана (⚠️ ЛИМИТ: максимум 1728x1080, на 1920x1200 будет err=-38)
adb shell screenrecord --size 1728x1080 /sdcard/video.mp4
\`\`\`

## 6. Чтение касаний (GETEVENT)
✅ Работает и по WiFi, и по USB (в отличие от input tap).
\`\`\`bash
# Параметры тачскрина (ищи ABS_MT_POSITION_X/Y min/max)
adb shell getevent -lp /dev/input/event3

# Чтение касаний в реальном времени (Ctrl+C для остановки)
adb shell getevent -lt /dev/input/event3

# Запись касаний в файл для последующего парсинга
adb shell getevent -lt /dev/input/event3 > touch_log.txt
\`\`\`

## 7. Troubleshooting
- \`unauthorized\`: Подтверди отладку по USB/WiFi на экране устройства.
- \`connection refused\`: Проверь актуальный порт в настройках "Беспроводная отладка".
- \`INJECT_EVENTS denied\`: Используй USB-кабель для эмуляции касаний, либо переходи на чтение \`getevent\`.
