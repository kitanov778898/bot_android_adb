import cv2

# ——— настройки –———————————————————————————————————————
SCREEN = "screen.png"
TEMPLATE = "button_start.png"
THRESHOLD = 0.8
PREVIEW = "screen_found.png"
# ———————————————————————————————————————————————————————

screen = cv2.imread(SCREEN)
template = cv2.imread(TEMPLATE)

if screen is None:
    print(f"❌ Не найден: {SCREEN}")
    exit(1)
if template is None:
    print(f"❌ Не найден: {TEMPLATE}")
    exit(1)

print(f"📐 Экран:   {screen.shape[1]}x{screen.shape[0]}")
print(f"📐 Шаблон:  {template.shape[1]}x{template.shape[0]}")

# Поиск шаблона
result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

print(f"\n🎯 Уверенность: {max_val:.3f}")
print(f"📍 Верхний левый угол: {max_loc}")

if max_val >= THRESHOLD:
    h, w = template.shape[:2]
    cx = max_loc[0] + w // 2
    cy = max_loc[1] + h // 2
    print(f"\n✅ НАЙДЕНО!")
    print(f"   Центр: ({cx}, {cy})")
    print(f"   Команда: adb shell input tap {cx} {cy}")

    # Рисуем рамку на превью
    cv2.rectangle(screen, max_loc,
                  (max_loc[0] + w, max_loc[1] + h),
                  (0, 0, 255), 3)
    cv2.circle(screen, (cx, cy), 8, (0, 255, 0), -1)
    cv2.imwrite(PREVIEW, screen)
    print(f"\n🖼️  Превью сохранено: {PREVIEW}")
else:
    print(f"\n❌ НЕ найдено (порог {THRESHOLD})")
    print(f"   Лучшее совпадение всего {max_val:.3f}")
    print("   Попробуй снизить THRESHOLD до 0.7 или пересоздать шаблон")