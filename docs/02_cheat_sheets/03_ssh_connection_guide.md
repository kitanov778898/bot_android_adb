# 🔐 SSH: Подключение и настройка

## 1. Архитектура подключения "Матрешка"

### Слой 1: ПК (Windows CMD) → Планшет (Termux)
\`\`\`cmd
:: Проброс порта через ADB
adb forward tcp:8022 tcp:8022

:: Подключение по SSH
ssh localhost -p 8022
\`\`\`

### Слой 2: Планшет (Termux) → POCO (по WiFi)
\`\`\`bash
# На планшете подключаемся к POCO по WiFi
adb connect 192.168.10.185:45107

# Проверка подключения
adb devices
\`\`\`

## 2. Проверка активной сессии

После подключения по SSH проверь, что ты в правильной консоли:
\`\`\`bash
ps
\`\`\`

**Ожидаемый вывод:**
\`\`\`
  PID TTY          TIME CMD
30208 pts/1    00:00:00 /data/data/com.termux/files/usr/bin/bash
26913 pts/1    00:00:00 ps
\`\`\`

## 3. Различение консолей

### 💻 Windows CMD (Внешняя)
- **Где:** На ПК
- **Как выглядит:** `C:\Users\79100\Downloads\111>`
- **Для чего:** Управление подключением (`adb forward`, `ssh localhost`)

### 📱 Termux Bash через SSH (Внутренняя)
- **Где:** Внутри планшета, отображается на экране ПК
- **Как выглядит:** `~/.../bot_android_adb $`
- **Для чего:** Управление файлами, Python-скрипты, `dumpsys`, запуск `adb connect` к POCO

## 4. Работа с tmux (опционально)

Если ты используешь tmux для управления сессиями:
\`\`\`bash
# Создать новую сессию
tmux new -s main

# Список активных сессий
tmux ls

# Подключиться к сессии
tmux attach -t main

# Отправить команду в другую сессию (если нужно)
echo "tmux attach -t main" > /dev/pts/0
\`\`\`

## 5. Troubleshooting

### Проблема: `Connection refused`
**Решение:**
1. Убедись, что SSH-сервер запущен в Termux: `sshd`
2. Проверь порт: `netstat -tlnp | grep 8022`
3. Перезапусти ADB-сервер на ПК: `adb kill-server && adb start-server`

### Проблема: `Permission denied (publickey)`
**Решение:**
1. Сгенерируй ключ (если еще нет): `ssh-keygen -t rsa`
2. Скопируй публичный ключ: `cat ~/.ssh/id_rsa.pub`
3. Добавь его в `~/.ssh/authorized_keys` на целевом устройстве

### Проблема: SSH-сессия обрывается
**Решение:**
- Используй `tmux` или `screen` для сохранения сессии
- Настрой KeepAlive в SSH-конфиге

## 6. Передача файлов через SCP

Через проброшенный порт 8022:
\`\`\`bash
# С планшета на ПК (выполнять в Windows CMD)
scp -P 8022 u0_a239@localhost:/data/data/com.termux/files/home/file.txt ./local_file.txt

# С ПК на планшет (выполнять в Windows CMD)
scp -P 8022 ./local_file.txt u0_a239@localhost:/data/data/com.termux/files/home/file.txt

# Рекурсивное копирование папки
scp -r -P 8022 u0_a239@localhost:/path/to/folder/ ./local_folder/
\`\`\`
