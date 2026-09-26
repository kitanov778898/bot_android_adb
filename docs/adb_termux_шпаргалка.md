Ниже — готовый документ, который можно скопировать целиком и вставить в файл adb_termux_шпаргалка.md. Он разделён на две части: ADB и Termux-звук, с оглавлением, таблицами, переменными и troubleshooting.

```markdown
# 📱 ADB + Termux: шпаргалка для проекта «Кликер»

Версия: 1.0  
Устройство: POCO M6 Pro (1080x2400)  
Планшет: Termux (Wi-Fi ADB)

---

## 📑 Оглавление

1. [Переменные](#переменные)
2. [ADB: подключение](#adb-подключение)
3. [ADB: управление приложениями](#adb-управление-приложениями)
4. [ADB: ввод и касания](#adb-ввод-и-касания)
5. [ADB: скриншоты и запись экрана](#adb-скриншоты-и-запись-экрана)
6. [ADB: getevent — чтение касаний](#adb-getevent--чтение-касаний)
7. [ADB: системные команды](#adb-системные-команды)
8. [ADB: troubleshooting](#adb-troubleshooting)
9. [Типовой цикл работы](#типовой-цикл-работы)
10. [Python-скрипт для ADB](#python-скрипт-для-adb)
11. [Termux: звук](#termux-звук)
12. [Termux: установка](#termux-установка)
13. [Termux: TTS (синтез речи)](#termux-tts-синтез-речи)
14. [Termux: воспроизведение](#termux-воспроизведение)
15. [Termux: запись с микрофона](#termux-запись-с-микрофона)
16. [Termux: громкость](#termux-громкость)
17. [Termux: генерация звука (ffmpeg)](#termux-генерация-звука-ffmpeg)
18. [Termux: Python-обёртка](#termux-python-обёртка)
19. [Termux: частые проблемы](#termux-частые-проблемы)

---

## Переменные

Перед работой задай переменные, чтобы не повторять IP и package name:

```bash
DEVICE=192.168.10.185:45107
APP=com.fingersoft.hillclimb
APP2=com.ea.game.starwarscapital_row
```

---

ADB: подключение

Команда Назначение
adb devices Список подключённых устройств
adb connect $DEVICE Подключиться к POCO по Wi-Fi
adb disconnect $DEVICE Отключиться
adb kill-server Убить сервер ADB
adb start-server Запустить сервер ADB

---

ADB: управление приложениями

Команда Назначение
adb shell am start -n $APP/com.fingersoft.game.MainActivity Запуск через Activity
adb shell am start -f 0x00020000 -n $APP/com.fingersoft.game.MainActivity Поднять уже запущенный экземпляр наверх (FLAG_ACTIVITY_REORDER_TO_FRONT)
adb shell monkey -p $APP 1 Запуск Hill Climb
adb shell monkey -p $APP2 1 Запуск Star Wars
adb shell am force-stop $APP Принудительно закрыть Hill Climb
adb shell pm list packages -3 Список сторонних приложений
adb shell pm list packages -3 \| grep -i "hill\|star\|war" Поиск приложений по ключевым словам
adb shell dumpsys activity recents \| grep $APP Проверить приложение в недавних
adb shell dumpsys window \| grep mCurrentFocus Показать активное окно

---

ADB: ввод и касания

Команда Назначение
adb shell input tap 540 1200 Клик в X=540 Y=1200
adb shell input swipe 100 500 100 100 Свайп от (100,500) до (100,100)
adb shell input text "hello" Ввести текст
adb shell input keyevent 4 Назад
adb shell input keyevent 3 Домой
adb shell input keyevent 26 Блокировка / разблокировка

⚠️ POCO M6 Pro: через Wi-Fi ADB команды input дают
java.lang.SecurityException: INJECT_EVENTS permission denied.
✅ Работают только через USB с ПК.
✅ getevent работает и по Wi-Fi, и по USB.

---

ADB: скриншоты и запись экрана

Команда Назначение
adb exec-out screencap -p > screen.png Скриншот сразу на планшет
adb shell screencap -p /sdcard/screen.png Скриншот на телефон
adb shell screenrecord /sdcard/video.mp4 Запись экрана (Ctrl+C — стоп)
Content area is 1728x1080

adb shell screenrecord --verbose --size 1728x1080 /sdcard/video.mp4

adb exec-out screencap > screen.raw

код для Пайтон ————————-
import subprocess

raw = subprocess.run(
    ["adb", "exec-out", "screencap"],
    stdout=subprocess.PIPE,
    check=True,
).stdout

# raw — это bytes, всё содержимое в памяти

---

ADB: getevent — чтение касаний

Команда Назначение
adb shell getevent -lp /dev/input/event3 Параметры тачскрина (min/max X, Y)
adb shell getevent -lt /dev/input/event3 Касания в реальном времени
adb shell getevent -lt /dev/input/event3 > touch_log.txt Записать касания в файл

Для POCO: ABS_MT_POSITION_X max = 17280, ABS_MT_POSITION_Y max = 38400.

---

ADB: системные команды

Команда Назначение
adb shell wm size Разрешение экрана (POCO: 1080x2400)
adb shell settings put system show_touches 1 Включить белые кружки нажатий
adb shell settings put system show_touches 0 Выключить кружки
adb shell dumpsys battery Информация о батарее
adb shell dumpsys cpuinfo Загрузка CPU

---

ADB: troubleshooting

Проблема Решение
unauthorized Подтверди отладку на телефоне
offline adb kill-server && adb start-server, переподключись
connection refused Проверь IP и порт в «Беспроводная отладка»
INJECT_EVENTS permission denied Используй USB ADB для input
Порт Wi-Fi сменился Смотри актуальный порт в настройках телефона

---

Типовой цикл работы

```bash
# 1. Подключиться
adb connect $DEVICE

# 2. Проверить
adb devices

# 3. Запустить игру
adb shell monkey -p $APP 1

# 4. Скриншот
adb exec-out screencap -p > menu.png

# 5. Записать касания
adb shell getevent -lt /dev/input/event3 > touch.txt
# Тыкаешь пальцем в START, затем Ctrl+C

# 6. Разобрать координаты (parse_touch.py)
```

---

Python-скрипт для ADB

```python
import os
import time

DEVICE = "192.168.10.185:45107"
APP = "com.fingersoft.hillclimb"

def run(cmd):
    print(f">>> {cmd}")
    os.system(cmd)

run(f"adb connect {DEVICE}")
time.sleep(1)
run(f"adb shell monkey -p {APP} 1")
time.sleep(5)
run("adb exec-out screencap -p > menu.png")
print("Готово! Скриншот сохранён как menu.png")
```

---

Termux: звук

Termux: установка

```bash
pkg update && pkg upgrade
pkg install termux-api python ffmpeg play-audio
termux-setup-storage
```

Требуется:

· приложение Termux:API (из F-Droid)
· TTS-движок (например, Speech Services by Google)

---

Termux: TTS (синтез речи)

Команда Назначение
termux-tts-speak "Привет, это тест" Простой тест
termux-tts-speak -l ru -r 0.9 -p 1.0 "Медленная фраза" Язык, скорость, тон
termux-tts-speak -e com.google.android.tts -l ru "Текст" Явно указать движок
termux-tts-engines Список доступных движков
termux-tts-speak "тест"; echo "rc=$?" Проверка кода возврата

termux-tts-speak -e com.google.android.tts -l ru -p 0.3 -r 0.7 "Я твой отец" 


---

Termux: воспроизведение

Команда Назначение
termux-media-player play ~/storage/shared/Music/song.mp3 Воспроизведение
termux-media-player pause Пауза
termux-media-player stop Стоп
play-audio ~/storage/shared/Music/beep.wav Короткий звук
play-audio ~/storage/shared/Music/beep.wav & Фоном

---

Termux: запись с микрофона

Команда Назначение
termux-microphone-record -f ~/storage/shared/Music/rec.wav -e wav -l 5 Запись 5 секунд в WAV
termux-microphone-record -f ~/storage/shared/Music/rec.wav -e wav Запись без лимита
termux-microphone-record -q Остановить запись
termux-microphone-record -f ~/storage/shared/Music/rec.aac -e aac -l 10 Запись 10 секунд в AAC

---

Termux: громкость

Команда Назначение
termux-volume Показать текущие уровни
termux-volume music 15 Установить громкость музыки
termux-volume ring 10 Установить громкость звонка

---

Termux: генерация звука (ffmpeg)

Команда Назначение
ffmpeg -f lavfi -i "sine=frequency=1000:duration=2" -ar 44100 $TMPDIR/beep.wav Тон 1000 Гц, 2 сек
ffmpeg -f lavfi -i "sine=frequency=440:duration=3" -ar 44100 $TMPDIR/a.wav Нота Ля, 3 сек
ffmpeg -i input.mp3 -ar 44100 output.wav MP3 → WAV
ffmpeg -i input.wav -b:a 128k output.mp3 WAV → MP3
ffmpeg -i in.mp3 -ss 00:00:02 -to 00:00:05 -c copy out.mp3 Обрезать с 2 по 5 сек

Пути:

· $TMPDIR — временные файлы Termux
· ~/storage/shared/Music — общая папка Music
· ~/storage/shared/ — корень внешней памяти

---

Termux: Python-обёртка

```python
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
    subprocess.run(["termux-microphone-record",
                    "-f", path, "-e", "wav", "-l", str(sec)])
    return path

def stop_all():
    subprocess.run(["termux-microphone-record", "-q"], capture_output=True)
    subprocess.run(["termux-media-player", "stop"], capture_output=True)
    subprocess.run(["pkill", "-f", "play-audio"], capture_output=True)

if __name__ == "__main__":
    say("Начинаю запись")
    rec = record("test.wav", 3)
    say("Запись завершена")
    play("test.wav")
```

---

Termux: частые проблемы

Проблема Решение
termux-tts-speak молчит, rc=0 Нет TTS-движка. Установи Speech Services by Google и активируй
/tmp/beep.wav: No such file В Termux нет /tmp. Используй $TMPDIR
termux-* молчат Нет приложения Termux:API. Установи из F-Droid
Нет звука, но всё работает Низкая громкость «Медиа». termux-volume music 15
play-audio не найден pkg install play-audio

---

Быстрый тест «всё работает»

```bash
termux-battery-status
ffmpeg -f lavfi -i "sine=frequency=1000:duration=2" -ar 44100 $TMPDIR/beep.wav
termux-media-player play $TMPDIR/beep.wav
termux-tts-speak "тест"
```

---

🎉 Удачного дебага!

```

