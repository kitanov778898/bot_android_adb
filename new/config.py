# config.py
# Настройки игры
PACKAGE_NAME = "com.fingersoft.hillclimb"
ACTIVITY_NAME = "com.fingersoft.game.MainActivity"

# Параметры экрана и тачскрина
#SCREEN_W = 1200
#SCREEN_H = 1920
#RAW_MAX_X = 11999
#RAW_MAX_Y = 19199

# Меняем ширину и высоту местами для горизонтального режима
SCREEN_W = 1920
SCREEN_H = 1200
RAW_MAX_X = 19199
RAW_MAX_Y = 11999


# Коэффициенты масштабирования
SCALE_X = RAW_MAX_X / SCREEN_W
SCALE_Y = RAW_MAX_Y / SCREEN_H

# Путь к устройству тачскрина
TOUCH_DEVICE = "/dev/input/event2"

# Координаты кнопок управления (для экрана 1920x1200)
START_X = 1550
START_Y = 750

GAS_X = 1670
GAS_Y = 1000

BRAKE_X = 250
BRAKE_Y = 1000


# Настройки бота
CLICK_INTERVAL = 0.5  # Интервал между кликами
MAX_CLICKS = 100      # Количество кликов

# ROI для кнопок (x1, y1, x2, y2)
# Формат: левый-верхний угол, правый-нижний угол
# Подгоняется под конкретный экран и ориентацию

START_ROI = (1400, 50, 1900, 350)   # кнопка START — верхний правый угол
CRASH_ROI = None                     # крестик аварии — пока ищем везде