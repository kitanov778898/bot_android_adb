from PIL import Image, ImageDraw

def draw_tap(input_path, output_path, x, y, radius=25, color='red'):
    """
    Открывает изображение, рисует закрашенный круг (tap) в заданной точке,
    сохраняет результат в новый файл.

    Параметры:
        input_path (str): путь к исходному изображению.
        output_path (str): путь для сохранения результата.
        x, y (int): координаты центра круга.
        radius (int): радиус круга (по умолчанию 25).
        color (str или tuple): цвет заливки (по умолчанию 'red').
    """
    img = Image.open(input_path)
    draw = ImageDraw.Draw(img)
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    img.save(output_path)

# Нарисовать красный круг радиусом 25 в точке (270, 250)
draw_tap('screen.png', 'out.png', 270, 250)

# Сменить цвет на синий и увеличить радиус
draw_tap('screen.png', 'out_blue.png', 100, 150, radius=40, color='blue')


