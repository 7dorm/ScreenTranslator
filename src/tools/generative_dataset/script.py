import os
import random
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Папки для сохранения датасета
OUTPUT_DIR = "dataset"
IMAGE_DIR = os.path.join(OUTPUT_DIR, "images")
LABEL_DIR = os.path.join(OUTPUT_DIR, "labels")
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(LABEL_DIR, exist_ok=True)

# Пути к шрифтам
FONT_DIR = "fonts"
FONT_PATHS = [os.path.join(FONT_DIR, f) for f in os.listdir(FONT_DIR) if f.endswith(".ttf")]

# Параметры генерации
IMAGE_SIZE = (640, 640)
NUM_IMAGES = 3  # Количество изображений
CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
CHAR_TO_CLASS = {char: i for i, char in enumerate(CHARACTERS)}

def random_color():
    """Генерирует случайный цвет (RGB)."""
    return tuple(random.randint(0, 255) for _ in range(3))

def is_overlapping(new_box, existing_boxes):
    """Проверяет, пересекается ли новый bbox с уже существующими."""
    x1_new, y1_new, x2_new, y2_new = new_box
    for x1, y1, x2, y2 in existing_boxes:
        if not (x2_new < x1 or x1_new > x2 or y2_new < y1 or y1_new > y2):
            return True  # Есть пересечение
    return False

def ensure_contrast(fg_color, bg_color, min_diff=20):
    """Обеспечивает различие цветов не менее чем на min_diff по каждому каналу."""
    while all(abs(fg_color[i] - bg_color[i]) < min_diff for i in range(3)):
        bg_color = random_color()
    return bg_color

def apply_perspective_transform(image, bbox):
    """Применяет перспективное преобразование к символу."""
    x1, y1, x2, y2 = bbox

    # Опорные точки bbox
    src_pts = np.float32([[x1, y1], [x2, y1], [x2, y2], [x1, y2]])

    # Смещение точек для искажения
    max_offset = 20
    dst_pts = src_pts + np.random.randint(-max_offset, max_offset, src_pts.shape).astype(np.float32)

    # Вычисляем матрицу трансформации
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)

    # Преобразуем PIL → OpenCV → Применяем трансформацию → OpenCV → PIL
    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    transformed = cv2.warpPerspective(image_cv, M, (IMAGE_SIZE[0], IMAGE_SIZE[1]))
    transformed = cv2.cvtColor(transformed, cv2.COLOR_BGR2RGB)

    return Image.fromarray(transformed)

def generate_image(idx):
    """Генерирует изображение с буквами и разметку YOLO."""
    image = Image.new("RGB", IMAGE_SIZE, random_color())
    draw = ImageDraw.Draw(image)
    
    objects = []  # Разметка YOLO
    existing_boxes = []  # Проверка пересечений

    num_chars = random.randint(15, 30)  # Случайное количество символов
    for _ in range(num_chars):
        char = random.choice(CHARACTERS)
        class_id = CHAR_TO_CLASS[char]  # ID символа
        font_path = random.choice(FONT_PATHS)
        font_size = random.randint(30, 100)
        
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()

        text_color = random_color()
        bg_color = ensure_contrast(text_color, random_color())

        # Генерация случайного положения буквы
        for _ in range(10):  # Пробуем до 10 раз, чтобы избежать пересечений
            x = random.randint(20, IMAGE_SIZE[0] - 120)
            y = random.randint(20, IMAGE_SIZE[1] - 120)

            # Определяем bbox
            bbox = draw.textbbox((x, y), char, font=font)
            x_min, y_min, x_max, y_max = bbox

            # Проверяем выход за границы
            if x_min < 0 or y_min < 0 or x_max > IMAGE_SIZE[0] or y_max > IMAGE_SIZE[1]:
                continue

            if not is_overlapping((x_min, y_min, x_max, y_max), existing_boxes):
                existing_boxes.append((x_min, y_min, x_max, y_max))
                break
        else:
            continue  # Если не нашли свободное место, пропускаем символ

        # Рисуем фон (контрастный прямоугольник)
        draw.rectangle(bbox, fill=bg_color)

        # Рисуем букву
        draw.text((x, y), char, font=font, fill=text_color)

        # Применяем перспективное искажение
        #image = apply_perspective_transform(image, bbox)

        # YOLO формат (нормализованные координаты)
        x_center = (x_min + x_max) / 2 / IMAGE_SIZE[0]
        y_center = (y_min + y_max) / 2 / IMAGE_SIZE[1]
        width = (x_max - x_min) / IMAGE_SIZE[0]
        height = (y_max - y_min) / IMAGE_SIZE[1]

        objects.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

    # Сохраняем изображение
    img_path = os.path.join(IMAGE_DIR, f"img_{idx}.png")
    image.save(img_path)

    # Сохраняем разметку YOLO
    label_path = os.path.join(LABEL_DIR, f"img_{idx}.txt")
    with open(label_path, "w") as f:
        f.write("\n".join(objects))

    print(f"Saved {img_path} with {len(objects)} objects.")

# Генерируем датасет
for i in range(NUM_IMAGES):
    generate_image(i)

print("Генерация завершена!")
