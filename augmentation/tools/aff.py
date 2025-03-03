from PIL import Image
import numpy as np

def affine_transform_image_and_boxes(image, boxes, transform_matrix):
    """
    Применяет аффинное преобразование с автоматическим определением нового размера 
    и корректным преобразованием боксов.
    
    :param image: Исходное изображение (PIL.Image)
    :param boxes: Список боксов [[class, x_center, y_center, width, height], ...]
    :param transform_matrix: Матрица аффинного преобразования 3x3
    :return: (transformed_image, new_boxes)
    """
    # Рассчитываем новые границы изображения
    width, height = image.size
    corners = np.array([
        [0, 0, 1],
        [width, 0, 1],
        [0, height, 1],
        [width, height, 1]
    ])
    
    # Применяем преобразование ко всем углам
    transformed_corners = np.dot(transform_matrix, corners.T).T[:, :2]
    
    # Находим новые границы
    x_min, y_min = transformed_corners.min(axis=0)
    x_max, y_max = transformed_corners.max(axis=0)
    
    # Рассчитываем новый размер изображения
    new_width = int(np.ceil(x_max - x_min))
    new_height = int(np.ceil(y_max - y_min))
    
    # Создаем матрицу преобразования с компенсацией смещения
    offset_matrix = np.array([
        [1, 0, -x_min],
        [0, 1, -y_min],
        [0, 0, 1]
    ])
    combined_matrix = np.dot(offset_matrix, transform_matrix)
    
    # Применяем преобразование к изображению
    transformed_image = image.transform(
        (new_width, new_height),
        Image.AFFINE,
        data=np.linalg.inv(combined_matrix).flatten()[:6],
        resample=Image.BILINEAR
    )
    
    # Преобразуем боксы
    new_boxes = []
    for box in boxes:
        cls, x_center, y_center, w, h = box
        
        # Конвертируем в абсолютные координаты
        x = x_center * width
        y = y_center * height
        half_w = w * width / 2
        half_h = h * height / 2
        
        # Углы исходного бокса
        corners = np.array([
            [x - half_w, y - half_h, 1],
            [x + half_w, y - half_h, 1],
            [x - half_w, y + half_h, 1],
            [x + half_w, y + half_h, 1]
        ])
        
        # Применяем преобразование
        transformed = np.dot(combined_matrix, corners.T).T
        
        # Находим новые границы
        tx = transformed[:, 0]
        ty = transformed[:, 1]
        
        new_x_min = tx.min()
        new_y_min = ty.min()
        new_x_max = tx.max()
        new_y_max = ty.max()
        
        # Конвертируем в относительные координаты
        new_w = (new_x_max - new_x_min) / new_width
        new_h = (new_y_max - new_y_min) / new_height
        new_x_center = (new_x_min + new_x_max) / (2 * new_width)
        new_y_center = (new_y_min + new_y_max) / (2 * new_height)
        
        new_boxes.append([
            cls,
            np.clip(new_x_center, 0.0, 1.0),
            np.clip(new_y_center, 0.0, 1.0),
            np.clip(new_w, 0.0, 1.0),
            np.clip(new_h, 0.0, 1.0)
        ])
    
    return transformed_image, new_boxes