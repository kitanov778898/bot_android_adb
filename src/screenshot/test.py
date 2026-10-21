from PIL import Image
import os

# 1. Имена файлов
input_file = "zzzz2.png"
output_file = "zzzz2.jpg"

try:
    # 2. Открываем исходную картинку
    img = Image.open(input_file)
    
    # 3. ВАЖНО: Конвертируем в RGB. 
    # PNG часто имеет прозрачность (Alpha-канал), а JPG её не поддерживает.
    # Если этого не сделать, Pillow выдаст ошибку при сохранении.
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
        print("✅ Прозрачность убрана, готовим JPG...")
    
    # 4. Сохраняем как JPG
    img.save(output_file, "JPEG", quality=90)
    print(f"✅ Успешно сохранено как: {output_file}")
    
    # 5. Пытаемся открыть через системный просмотрщик Android
    print("🚀 Открываем файл...")
    os.system(f"termux-open {output_file}")
    
except FileNotFoundError:
    print(f"❌ Ошибка: Файл '{input_file}' не найден. Проверь имя командой 'ls'")
except Exception as e:
    print(f"❌ Что-то пошло не так: {e}")
