# 1. Запусти X11 сервер
termux-x11 :0 -ac &

# 2. Подожди немного, пока сервер запустится
sleep 2

# 3. Установи переменную окружения
export DISPLAY=:0

# 4. Проверь, что сервер работает
xdpyinfo | head -20

# 5. Запусти свой скрипт
am start --user 0 -n com.termux.x11/.MainActivity >/dev/null 2>&1

