from PIL import Image
import numpy as np

def map_cylindrical_coords_tilted(x, y, width, height, radius, tilt_angle):
    """
    Отображает координаты пикселя на цилиндрические координаты с учётом угла наклона.

    :param x: Координата x пикселя.
    :param y: Координата y пикселя.
    :param width: Ширина изображения.
    :param height: Высота изображения.
    :param radius: Радиус цилиндра.
    :param tilt_angle: Угол наклона цилиндра в градусах.
    :return: Новые координаты (new_x, new_y).
    """
    # Нормализация координат
    x_norm = (2 * x - width) / width
    y_norm = (2 * y - height) / height

    # Вычисление xx (коэффициент искажения)
    zx = 1 - x_norm**2
    xx = np.sqrt(zx if zx >=0 else 0)

    # Применение цилиндрической проекции с учётом наклона
    new_x = x + radius * xx
    new_y = y - tilt_angle * xx

    return new_x, new_y

def cylindrical_projection_tilted(image, radius, tilt_angle):
    """
    Натягивает изображение на наклонённый цилиндр, создавая эффект перспективы.

    :param image: Объект изображения PIL.Image.
    :param radius: Радиус цилиндра.
    :param tilt_angle: Угол наклона цилиндра в градусах.
    :return: Новое изображение с эффектом цилиндрической проекции.
    """
    width, height = image.size

    # Создаём новое изображение с увеличенной высотой, чтобы избежать обрезания
    new_height = int(height + 2 * abs(tilt_angle))
    new_image = Image.new("RGB", (width, new_height), color=(0, 0, 0))  # Чёрный фон
    pixels = new_image.load()

    # Вычисляем смещение для центрирования изображения
    y_offset = (new_height - height) // 2

    # Применяем преобразование к каждому пикселю
    for x in range(width):
        for y in range(height):
            new_x, new_y = map_cylindrical_coords_tilted(x, y, width, height, radius, tilt_angle)

            # Корректируем координаты с учётом смещения
            new_x = int(np.clip(new_x, 0, width - 1))
            new_y = int(np.clip(new_y + y_offset, 0, new_height - 1))

            # Копируем пиксель
            pixels[new_x, new_y] = image.getpixel((x, y))

    return new_image

def adjust_boxes(boxes, width, height, radius, tilt_angle):
    """
    Корректирует координаты боксов после цилиндрической проекции.

    :param boxes: Список боксов в формате [class, x_center, y_center, width, height].
    :param width: Ширина изображения.
    :param height: Высота изображения.
    :param radius: Радиус цилиндра.
    :param tilt_angle: Угол наклона цилиндра в градусах.
    :return: Список скорректированных боксов.
    """
    new_boxes = []
    y_offset = (height + 2 * abs(tilt_angle) - height) // 2

    for box in boxes:
        cls, x_center, y_center, box_width, box_height = box

        # Преобразуем центр бокса
        new_x_center, new_y_center = map_cylindrical_coords_tilted(
            x_center * width, y_center * height, width, height, radius, tilt_angle
        )

        # Преобразуем ширину и высоту
        new_box_width = box_width * width
        new_box_height = box_height * height

        # Корректируем координаты с учётом смещения
        new_y_center += y_offset

        # Нормализуем координаты
        new_x_center_norm = new_x_center / width
        new_y_center_norm = new_y_center / (height + 2 * abs(tilt_angle))
        new_box_width_norm = new_box_width / width
        new_box_height_norm = new_box_height / (height + 2 * abs(tilt_angle))

        new_boxes.append([
            cls,
            np.clip(new_x_center_norm, 0.0, 1.0),
            np.clip(new_y_center_norm, 0.0, 1.0),
            np.clip(new_box_width_norm, 0.01, 0.99),
            np.clip(new_box_height_norm, 0.01, 0.99)
        ])

    return new_boxes

def stretch_image_on_tilted_cylinder_and_adjust_boxes(image, boxes, radius=100, tilt_angle=15):
    """
    Натягивает изображение на наклонённый цилиндр и корректирует координаты боксов.

    :param image: Объект изображения PIL.Image.
    :param boxes: Список боксов в формате [class, x_center, y_center, width, height].
    :param radius: Радиус цилиндра.
    :param tilt_angle: Угол наклона цилиндра в градусах.
    :return: Новое изображение с эффектом цилиндрической проекции и список скорректированных боксов.
    """
    # Применяем цилиндрическую проекцию
    transformed_image = cylindrical_projection_tilted(image, radius, tilt_angle)

    # Корректируем боксы
    new_boxes = adjust_boxes(boxes, image.width, image.height, radius, tilt_angle)

    return transformed_image, new_boxes