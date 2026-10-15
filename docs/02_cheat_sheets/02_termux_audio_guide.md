# 🔊 Termux: Работа со звуком

## 1. Установка и подготовка
\`\`\`bash
pkg update && pkg upgrade
pkg install termux-api python ffmpeg play-audio
termux-setup-storage
\`\`\`
**Требования:** 
- Установленное приложение **Termux:API** (из F-Droid).
- Активный TTS-движок в системе Android (например, *Speech Services by Google*).

## 2. Синтез речи (TTS)
\`\`\`bash
# Простой тест
termux-tts-speak "Привет, это тест"

# С указанием языка, скорости и тона
termux-tts-speak -l ru -r 0.9 -p 1.0 "Медленная фраза"

# Явное указание движка
termux-tts-speak -e com.google.android.tts -l ru "Текст"

# Проверка доступных движков
termux-tts-engines

# Проверка кода возврата (должен быть 0)
termux-tts-speak "тест"; echo "rc=$?"
\`\`\`

## 3. Воспроизведение аудио
\`\`\`bash
# Через Android-медиаплеер (поддерживает паузу/стоп)
termux-media-player play ~/storage/shared/Music/song.mp3
termux-media-player pause
termux-media-player stop

# Через play-audio (лёгкий, для коротких звуков)
play-audio ~/storage/shared/Music/beep.wav

# Запуск в фоне (не блокирует скрипт)
play-audio ~/storage/shared/Music/beep.wav &
\`\`\`

## 4. Запись с микрофона
\`\`\`bash
# Запись 5 секунд в WAV
termux-microphone-record -f ~/storage/shared/Music/rec.wav -e wav -l 5

# Запись без лимита (остановить вручную)
termux-microphone-record -f ~/storage/shared/Music/rec.wav -e wav
termux-microphone-record -q  # Остановка записи

# Запись в AAC (компактнее)
termux-microphone-record -f ~/storage/shared/Music/rec.aac -e aac -l 10
\`\`\`

## 5. Управление громкостью
\`\`\`bash
# Показать текущие уровни по потокам
termux-volume

# Установить громкость (значение из вывода выше, например, 15)
termux-volume music 15
termux-volume ring 10
\`\`\`

## 6. Генерация звука (FFmpeg)
\`\`\`bash
# Тон 1000 Гц, 2 секунды, WAV (используем $TMPDIR, а не /tmp)
ffmpeg -f lavfi -i "sine=frequency=1000:duration=2" -ar 44100 \$TMPDIR/beep.wav

# Тон 440 Гц (нота Ля), 3 секунды
ffmpeg -f lavfi -i "sine=frequency=440:duration=3" -ar 44100 \$TMPDIR/a.wav

# Конвертация MP3 -> WAV
ffmpeg -i input.mp3 -ar 44100 output.wav
\`\`\`

## 7. Python-обёртка для автоматизации
\`\`\`python
import subprocess
import os

AUDIO = os.path.expanduser("~/storage/shared/Music")

def say(text, lang="ru"):
    subprocess.run(["termux-tts-speak", "-l", lang, text])

def play(filename):
    path = os.path.join(AUDIO, filename)
    subprocess.Popen(["termux-media-player", "play", path],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def record(name="rec.wav", sec=5):
    path = os.path.join(AUDIO, name)
    subprocess.run(["termux-microphone-record", "-f", path, "-e", "wav", "-l", str(sec)])
    return path

def stop_all():
    subprocess.run(["termux-microphone-record", "-q"], capture_output=True)
    subprocess.run(["termux-media-player", "stop"], capture_output=True)
    subprocess.run(["pkill", "-f", "play-audio"], capture_output=True)
\`\`\`

## 8. Troubleshooting
- **termux-tts-speak молчит, rc=0**: Нет TTS-движка. Установи *Speech Services by Google* и активируй его в настройках Android.
- **/tmp/beep.wav: No such file**: В Termux нет `/tmp`. Всегда используй переменную `\$TMPDIR`.
- **Команды termux-* молчат**: Не установлено приложение Termux:API. Установи его из F-Droid.
- **Нет звука, но всё работает**: Низкая громкость потока "Медиа". Выполни `termux-volume music 15`.
- **play-audio: command not found**: Выполни `pkg install play-audio`.
