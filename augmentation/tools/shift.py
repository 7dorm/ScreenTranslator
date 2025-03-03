from PIL import Image
import numpy as np

def shift_image_and_boxes_no_crop(image, boxes, shift_x, shift_y):
    """
    Сдвигает изображение и корректирует координаты боксов без обрезки.

    :param image: Объект изображения PIL.Image.
    :param boxes: Список боксов в формате [class, x_center, y_center, width, height].
    :param shift_x: Величина сдвига по оси x (в пикселях).
    :param shift_y: Величина сдвига по оси y (в пикселях).
    :return: Преобразованное изображение и список скорректированных боксов.
    """
    width, height = image.size

    # Вычисляем новые размеры изображения с учетом сдвига
    new_width = width + abs(shift_x)
    new_height = height + abs(shift_y)

    # Создаем новое изображение с расширенными размерами
    new_image = Image.new("RGB", (new_width, new_height), (0, 0, 0))  # Заполняем черным цветом

    # Вычисляем смещение для центрирования изображения после сдвига
    offset_x = shift_x if shift_x >= 0 else 0
    offset_y = shift_y if shift_y >= 0 else 0

    # Вставляем исходное изображение в новое с учетом сдвига
    new_image.paste(image, (offset_x, offset_y))

    # Создаем матрицу преобразования для сдвига
    translation_matrix = np.array([
        [1, 0, shift_x],
        [0, 1, shift_y],
        [0, 0, 1]
    ])

    # Преобразуем боксы
    new_boxes = []
    for box in boxes:
        cls, x_center, y_center, box_width, box_height = box

        # Вычисляем углы бокса
        if (shift_y>0):
            y_min = (y_center - box_height / 2) * height
            y_max = (y_center + box_height / 2) * height
            new_y_max = y_max + shift_y
            new_y_min = y_min + shift_y
            new_box_height = new_y_max - new_y_min
            new_y_center = new_y_min + new_box_height / 2
            new_y_center /= new_height
            new_box_height /= new_height
        else:
            new_box_height = box_height/( 1 - shift_y/height)
            new_y_center = y_center/( 1 - shift_y/height)

        if(shift_x > 0):
            x_min = (x_center - box_width / 2) * width
            x_max = (x_center + box_width / 2) * width
            new_x_max = x_max + shift_x
            new_x_min = x_min + shift_x
            new_box_width = new_x_max - new_x_min
            new_x_center = new_x_min + new_box_width / 2
            new_box_width /= new_width
            new_x_center /= new_width
        else:
            
            new_x_center = x_center/( 1 - shift_x/width)
            new_box_width = box_width/( 1 - shift_x/width)

        # Добавляем новый бокс в список
        new_boxes.append([cls, new_x_center, new_y_center, new_box_width, new_box_height])

    return new_image, new_boxes