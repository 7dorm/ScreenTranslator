from PIL import Image 

def compress_image_and_boxes(image, boxes, scale=1):
    # Открываем изображение
    width, height = image.size

    # Сжимаем изображение
    new_width = width // scale
    new_height = height // scale
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)
    
    # Сжимаем боксы
    new_boxes = []
    for box in boxes:
        # Предполагается, что формат боксов: class x_center y_center width height
        cls, x_center, y_center, box_width, box_height = box
        new_x_center = x_center / scale
        new_y_center = y_center / scale
        new_box_width = box_width / scale
        new_box_height = box_height / scale
        new_boxes.append([cls, new_x_center, new_y_center, new_box_width, new_box_height])
    
    return resized_image, new_boxes