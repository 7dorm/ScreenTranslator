from PIL import Image, ImageDraw
import math

def rotate_image_and_boxes(image, boxes, degrees):
    """
    Поворачивает изображение и корректирует координаты боксов.

    :param image: Объект изображения PIL.Image
    :param boxes: Список боксов в формате [class, x_center, y_center, width, height]
    :param degrees: Угол поворота в градусах
    :return: Повёрнутое изображение и список скорректированных боксов
    """
    # Открываем изображение
    width, height = image.size

    # Поворачиваем изображение
    rotated_image = image.rotate(degrees, expand=True)

    # Преобразуем угол из градусов в радианы
    radians = math.radians(degrees)
    cos_theta = math.cos(radians)
    sin_theta = math.sin(radians)

    # Функция для поворота точки
    def rotate_point(x, y, rotated_width, rotated_height):
        # Перенос центра изображения в начало координат
        x_shifted = x
        y_shifted = y

        # Поворот
        x_rotated = x_shifted * cos_theta - y_shifted * sin_theta
        y_rotated = -x_shifted * sin_theta + y_shifted * cos_theta

        x_new = x_rotated #+ rotated_height
        y_new = y_rotated #- rotated_width

        return x_new, y_new

    # Корректируем боксы
    new_boxes = []
    for box in boxes:
        cls, x_center, y_center, box_width, box_height = box

        # Вычисляем координаты углов бокса
        x_min = x_center - box_width / 2
        y_min = y_center - box_height / 2
        x_max = x_center + box_width / 2
        y_max = y_center + box_height / 2

        x_center_shifted = x_center * cos_theta - y_center * sin_theta

        # Поворачиваем углы бокса
        points = [
            rotate_point(x_min, y_min, x_center, y_center,),
            rotate_point(x_max, y_min, x_center, y_center,),
            rotate_point(x_max, y_max, x_center, y_center,),
            rotate_point(x_min, y_max, x_center, y_center,)
        ]
        # Находим новые границы бокса
        new_x_coords = [point[0] for point in points]
        new_y_coords = [point[1] for point in points]
        new_x_min = min(new_x_coords)
        new_y_min = min(new_y_coords)
        new_x_max = max(new_x_coords)
        new_y_max = max(new_y_coords)

        # Вычисляем новый центр и размеры бокса
        new_x_center = (new_x_min + new_x_max) / 2
        new_y_center = (new_y_min + new_y_max) / 2
        new_box_width = new_x_max - new_x_min
        new_box_height = new_y_max - new_y_min

        new_boxes.append([cls, new_x_center, new_y_center, new_box_width, new_box_height])

    return rotated_image, new_boxes