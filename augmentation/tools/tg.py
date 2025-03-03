from PIL import Image
import math

def cylindrical_distortion(image, boxes, distortion_factor=0.15):
    """
    Применяет цилиндрическую деформацию к изображению и преобразует bounding boxes
    :param image: Исходное изображение (PIL Image)
    :param boxes: Список боксов в формате [class, x_center, y_center, width, height]
    :param distortion_factor: Сила деформации (0.0-0.5)
    :return: Деформированное изображение и преобразованные боксы
    """
    width, height = image.size
    new_image = Image.new("RGB", (width, height))
    pixels = new_image.load()
    
    # Коэффициент цилиндрической проекции
    k = distortion_factor * width
    
    # Создаем преобразование координат
    for y in range(height):
        theta = (y - height/2) * math.pi / height
        shift = int(k * math.sin(theta))
        
        for x in range(width):
            src_x = x - shift
            if 0 <= src_x < width:
                pixels[x, y] = image.getpixel((src_x, y))
    
    # Преобразуем координаты боксов
    new_boxes = []
    for box in boxes:
        cls, x_center, y_center, w, h = box
        
        # Рассчитываем смещение для центра бокса
        theta_center = (y_center*height - height/2) * math.pi / height
        shift_center = k * math.sin(theta_center) / width
        
        # Смещаем центр
        new_x_center = x_center + shift_center
        
        # Рассчитываем деформацию ширины
        theta_top = ((y_center - h/2)*height - height/2) * math.pi / height
        theta_bottom = ((y_center + h/2)*height - height/2) * math.pi / height
        width_scale = 1 + k*(math.cos(theta_top) + math.cos(theta_bottom))/(2*width)
        
        new_boxes.append([
            cls,
            max(0.0, min(1.0, new_x_center)),
            y_center,
            max(0.01, min(0.99, w * width_scale)),
            h
        ])
    
    return new_image, new_boxes