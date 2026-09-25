from PIL import Image, ImageDraw

# ——— настройки –———————————————————————————————————————
INPUT = "screen.png"           # исходный скриншот
OUTPUT = "button_start.png"    # куда сохранить шаблон
PREVIEW = "screen_boxed.png"   # проверочный скрин с рамкой

# Координаты кнопки: (left, top, right, bottom)
BOX = (1400, 710, 1710, 900)
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