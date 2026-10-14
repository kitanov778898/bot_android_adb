from PIL import Image, ImageDraw
import os

__version__ = "1.2.3"

#МАГАЗИН ✅	(245, 788, 490, 832)	245×44
#ЭТАП	(590, 786, 735, 834)	145×48
#АППАРАТ	(835, 764, 1080, 812)	245×48
#ТЮНИНГ	(1140, 786, 1355, 834)	215×48
#СТАРТ	(1465, 786, 1635, 834)	170×48
name="АППАРАТ"
# ——— настройки –———————————————————————————————————————
INPUT = "test1.png"           # исходный скриншот
OUTPUT = "button_"+name+".png"    # куда сохранить шаблон
PREVIEW = "screen_boxed.png"   # проверочный скрин с рамкой

# Координаты кнопки: (left, top, right, bottom)
BOX = (835, 764, 1080, 812)

#кнопка старт область резерв
#BOX = (1400, 710, 1710, 900)
# ———————————————————————————————————————————————————————

img = Image.open(INPUT).convert("RGB")
print(f"📐 Размер экрана: {img.size}")

crop = img.crop(BOX)
crop.save(OUTPUT)
print(f"✅ Шаблон сохранён: {OUTPUT}")
print(f"📐 Размер шаблона: {crop.size}")

# Проверочный скрин с рамкой
preview = img.copy()
draw = ImageDraw.Draw(preview)
draw.rectangle(BOX, outline="red", width=4)
draw.text((BOX[0], max(BOX[1] - 20, 0)), "START", fill="red")
preview.save(PREVIEW)
print(f"✅ Проверочный скрин: {PREVIEW}")
print(f"✅ коардинаты: {BOX}")




# ... после сохранения ...

#os.system(f'termux-open {PREVIEW}')
# или
#os.system(f'xdg-open {PREVIEW}')