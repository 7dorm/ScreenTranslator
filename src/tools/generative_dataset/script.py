from PIL import Image, ImageDraw, ImageFont
import numpy as np
import argparse
import random
import cv2
import os

# Параметры генерации
IMAGE_SIZE = (640, 640)
CHARACTER_MAP = {
    'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9,
    'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17, 'S': 18, 'T': 19,
    'U': 20, 'V': 21, 'W': 22, 'X': 23, 'Y': 24, 'Z': 25,
    'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9,
    'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16, 'r': 17, 's': 18, 't': 19,
    'u': 20, 'v': 21, 'w': 22, 'x': 23, 'y': 24, 'z': 25,
    '0': 26, '1': 27, '2': 28, '3': 29, '4': 30, '5': 31, '6': 32, '7': 33, '8': 34, '9': 35,
    #   '.': 36, ',': 37, '?': 38, '!': 39, '@': 40
}
CHARACTERS = list(CHARACTER_MAP.keys())
FONT_DIR = "fonts"
OUTPUT_DIR = "dataset"
IMAGES_DIR = os.path.join(OUTPUT_DIR, "images")
LABELS_DIR = os.path.join(OUTPUT_DIR, "labels")

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(LABELS_DIR, exist_ok=True)

FONT_PATHS = [os.path.join(FONT_DIR, f) for f in os.listdir(FONT_DIR) if f.endswith(".ttf")]

def random_color():
    return tuple(random.randint(0, 255) for _ in range(3))

def sufficient_contrast(bg_color, text_color, threshold=50):
    return all(abs(bg_color[i] - text_color[i]) > threshold for i in range(3))

def find_content_bounds(image, symbol_color):
    """Находит границы символа по цвету."""
    pixels = image.load()
    width, height = image.size

    top, bottom, left, right = height, 0, width, 0
    found = False

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]  # Получаем цвет с учетом альфа-канала
            if a > 0 and (r, g, b) == symbol_color:
                found = True
                top = min(top, y)
                bottom = max(bottom, y)
                left = min(left, x)
                right = max(right, x)

    if not found:
        return None  # Нет содержимого

    # Добавляем отступы по 3 пикселя с каждой стороны
    top = max(top - 3, 0)
    bottom = min(bottom + 3, height - 1)
    left = max(left - 3, 0)
    right = min(right + 3, width - 1)

    return top, bottom, left, right

def generate_transformed_character(char, font_path, font_size):
    """Создаёт изображение буквы и применяет искажение."""
    font = ImageFont.truetype(font_path, font_size)
    text_color = random_color()
    bg_color = random_color()

    while not sufficient_contrast(bg_color, text_color):
        text_color = random_color()

    # Определяем размер символа
    temp_img = Image.new("RGB", (500, 500), bg_color)
    temp_draw = ImageDraw.Draw(temp_img)
    bbox = temp_draw.textbbox((0, 0), char, font=font)
    char_w, char_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Добавляем запас на искажение
    max_distortion = int(max(char_w, char_h))
    canvas_size = (char_w + max_distortion * 5, char_h + max_distortion * 5)

    char_img = Image.new("RGBA", canvas_size, bg_color + (255,))
    draw = ImageDraw.Draw(char_img)
    draw.text((max_distortion, max_distortion), char, font=font, fill=text_color)

    # Применяем искажение
    char_img_cv = np.array(char_img)
    transformed_img_cv = apply_perspective_transform(char_img_cv)

    # Преобразуем обратно в PIL
    transformed_img_pil = Image.fromarray(transformed_img_cv).convert("RGBA")

    # Обрезаем символ по цвету
    bounds = find_content_bounds(transformed_img_pil, text_color)
    if bounds:
        top, bottom, left, right = bounds
        transformed_img_pil = transformed_img_pil.crop((left, top, right + 1, bottom + 1))

    return transformed_img_pil

def apply_perspective_transform(image):
    """Применяет перспективное искажение."""
    h, w = image.shape[:2]
    src_pts = np.float32([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]])

    max_offset = min(w, h) // 3 # Тут константу подвигать полезно
    dst_pts = np.float32([
        [random.randint(0, max_offset), random.randint(0, max_offset)],
        [w - random.randint(0, max_offset), random.randint(0, max_offset)],
        [w - random.randint(0, max_offset), h - random.randint(0, max_offset)],
        [random.randint(0, max_offset), h - random.randint(0, max_offset)]
    ])

    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    transformed = cv2.warpPerspective(image, M, (w, h))

    return transformed

def find_available_position(existing_boxes, bbox, img_size):
    """Ищет место для вставки символа."""
    x_min, y_min, x_max, y_max = bbox
    w, h = x_max - x_min, y_max - y_min

    for _ in range(20):  # Пробуем до 20 раз
        x = random.randint(0, img_size[0] - w)
        y = random.randint(0, img_size[1] - h)
        new_bbox = (x, y, x + w, y + h)

        if not any(is_overlapping(new_bbox, box) for box in existing_boxes):
            return new_bbox

    return None  # Не нашли место

def is_overlapping(box1, box2):
    """Проверяет пересечение bbox."""
    x1, y1, x2, y2 = box1
    a1, b1, a2, b2 = box2
    return not (x2 < a1 or x1 > a2 or y2 < b1 or y1 > b2)

def generate_image(image_id):
    """Генерирует изображение с буквами и разметкой."""
    image = Image.new("RGB", IMAGE_SIZE, random_color())
    existing_boxes = []
    annotations = []

    for _ in range(random.randint(15, 30)):
        char = random.choice(CHARACTERS)
        font_path = random.choice(FONT_PATHS)
        font_size = random.randint(50, 200)

        # Применяем искажение и обрезку символа
        transformed_img = generate_transformed_character(char, font_path, font_size)
        bounds = find_content_bounds(transformed_img, random_color())
        if bounds:
            top, bottom, left, right = bounds
            transformed_img = transformed_img.crop((left, top, right + 1, bottom + 1))

        # Получаем новые размеры символа после обрезки и искажения
        new_w, new_h = transformed_img.size
        bbox = (0, 0, new_w, new_h)

        # Найти место для вставки с учётом искажений
        new_bbox = find_available_position(existing_boxes, bbox, IMAGE_SIZE)
        if new_bbox is None:
            continue  # Пропускаем символ, если нет места

        # Вставляем символ
        image.paste(transformed_img, (new_bbox[0], new_bbox[1]), transformed_img)

        # Добавляем разметку
        x_min, y_min, x_max, y_max = new_bbox
        x_center = (x_min + x_max) / (2 * IMAGE_SIZE[0])
        y_center = (y_min + y_max) / (2 * IMAGE_SIZE[1])
        width = (x_max - x_min) / IMAGE_SIZE[0]
        height = (y_max - y_min) / IMAGE_SIZE[1]

        class_id = CHARACTER_MAP[char]
        annotations.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

        # Добавляем новый bounding box в список
        existing_boxes.append(new_bbox)

    # Сохранение изображений и разметок
    image.save(os.path.join(IMAGES_DIR, f"image_{image_id}.png"))
    with open(os.path.join(LABELS_DIR, f"image_{image_id}.txt"), "w") as f:
        f.write("\n".join(annotations))

parser = argparse.ArgumentParser(description="Генерация изображений с символами")
parser.add_argument("NUM_IMAGES", type=int, help="Количество изображений для генерации")
args = parser.parse_args()

# Генерация изображений
for i in range(args.NUM_IMAGES):
    generate_image(i)

print(f"Сгенерировано {args.NUM_IMAGES} изображений и разметок в {OUTPUT_DIR}")
