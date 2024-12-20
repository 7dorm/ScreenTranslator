import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm

# Параметры
DATASET_DIR = '/path/generated datasets'
PROBA_DIR = '/path/proba datasets'
BACKGROUNDS = 'backgrounds'
TRAIN_RATIO, VALID_RATIO = 0.7, 0.2
IMAGE_SIZE = (640, 480)
FONTS_DIR = 'fonts'  # Папка с шрифтами (добавьте шрифты в эту папку)
FONTS = [os.path.join(FONTS_DIR, f) for f in os.listdir(FONTS_DIR) if (f.endswith('.ttf') or f.endswith('.otf'))]
CLASS_NAMES = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
    'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', ',', '?', '!', '@'
]

CLASS_MAP = {c: i for i, c in enumerate(CLASS_NAMES)}

# Создание директорий
for split in ['train', 'valid', 'test']:
    os.makedirs(os.path.join(DATASET_DIR, split, 'images'), exist_ok=True)
    os.makedirs(os.path.join(DATASET_DIR, split, 'labels'), exist_ok=True)
os.makedirs(PROBA_DIR, exist_ok=True)

def generate_random_text():
    """Генерация случайного текста из доступных символов."""
    text_length = random.randint(5, 15)
    chars = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,?!@')
    return ''.join(random.choices(chars, k=text_length))

# Функция для проверки пересечения прямоугольников
def does_intersect(new_box, existing_boxes):
    for box in existing_boxes:
        if not (
            new_box[2] <= box[0] or  # new_box right <= box left
            new_box[0] >= box[2] or  # new_box left >= box right
            new_box[3] <= box[1] or  # new_box bottom <= box top
            new_box[1] >= box[3]     # new_box top >= box bottom
        ):
            return True
    return False

def add_noise_and_rotation(image):
    """Добавление шума и вращения текста."""
    # Генерация случайного угла наклона
    angle = random.uniform(-10, 10)  # Уменьшен диапазон угла наклона

    # Генерация случайного шума
    if random.random() < 0.5:  # Шанс добавления шума 50%
        noise = np.random.random((image.size[1], image.size[0], 3))  # Случайные числа от 0 до 1
        noise = (noise * (0.3 + random.random()*1.2)).astype(np.uint8)  # Меньше интенсивности шума
        image_array = np.array(image)
        noisy_image = np.clip(image_array + noise, 0, 255).astype(np.uint8)
        image = Image.fromarray(noisy_image)

    return image

def draw_char_with_box(draw, char, font, x, y, angle):
    """
    Рисует символ на изображении с заданным шрифтом, координатами и углом поворота.
    Возвращает бокс для символа с учетом поворота.
    """
    # Создаем изображение для символа
    char_image = Image.new('RGBA', (font.size * 2, font.size * 2), (255, 255, 255, 0))
    char_draw = ImageDraw.Draw(char_image)
    font_path = random.choice(FONTS)
    font = ImageFont.truetype(font_path, random.randint(20, 50))
    random_color = tuple(random.randint(0, 255) for _ in range(3))
    char_draw.text((0, 0), char, font=font, fill=random_color)

    # Поворачиваем символ
    rotated_char_image = char_image.rotate(angle, expand=True)

    # Получаем размер повернутого изображения
    rotated_width, rotated_height = rotated_char_image.size

    # Рассчитываем позицию для вставки повернутого символа
    paste_x = x - rotated_width // 2
    paste_y = y - rotated_height // 2

    random_color = tuple(random.randint(0, 255) for _ in range(3))
    # Накладываем повернутый символ на основное изображение
    draw.bitmap((paste_x, paste_y), rotated_char_image, fill=random_color)

    # Получаем бокс для повернутого символа (с учетом его нового положения после поворота)
    char_bbox = rotated_char_image.getbbox()  # Получаем бокс для повернутого символа

    x_min = char_bbox[0] + paste_x
    y_min = char_bbox[1] + paste_y
    x_max = char_bbox[2] + paste_x
    y_max = char_bbox[3] + paste_y

    # Возвращаем координаты бокса и класс символа
    return [x_min, y_min, x_max, y_max, CLASS_MAP.get(char, CLASS_MAP['.'])]  # 'dot' заменяем на '.'

def generate_image_and_labels(output_dir, num_images):
    """Создание изображений и разметки с увеличенными боками для каждой стороны."""
    for i in tqdm(range(num_images)):
        #background_path = random.choice(BACKGROUNDS)
        #print(f"Selected background path: {background_path}")
        #image = Image.open(background_path).convert('RGB').resize(IMAGE_SIZE)
        random_color = tuple(random.randint(230, 255) for _ in range(3))
        image = Image.new('RGB', IMAGE_SIZE, random_color)
        draw = ImageDraw.Draw(image)

        text_boxes = []
        y_offset = 30 + (random.random() * 20)  # Начальная вертикальная позиция
        x_offset = 20 + (random.random() * 30)  # Начальная горизонтальная позиция
        current_line_height = 0  # Высота текущей строки

        for _ in range(random.randint(3, 12)):  # Генерация от 1 до 5 строк текста
            text = generate_random_text()
            font = ImageFont.truetype(random.choice(FONTS), random.randint(20, 50))
            angle = random.uniform(-10, 10)  # Угол наклона для текста

            # Calculate the width of the line
            line_width = sum(font.getbbox(char)[2] for char in text) + len(text) * 5  # Ширина строки с учетом пробелов

            # If the line exceeds the image width, split the text into smaller parts
            if x_offset + line_width > IMAGE_SIZE[0] - 10:
                # Implement text wrapping logic here if necessary
                # For simplicity, we'll start a new line
                x_offset = 20 + (random.random() * 30)
                y_offset += current_line_height
                current_line_height = 0

            # Check if there's enough vertical space for the new line
            if y_offset + font.size > IMAGE_SIZE[1]:
                break  # Прерываем, если строки больше не помещаются

            # Draw the text line
            for char in text:
                char_width = font.getbbox(char)[2]  # Получаем ширину символа

                # Check if the character exceeds the image width
                if x_offset + char_width > IMAGE_SIZE[0] - 10:
                    # Start a new line
                    x_offset = 20 + (random.random() * 30)
                    y_offset += current_line_height
                    current_line_height = 0

                    # Check vertical space again
                    if y_offset + font.size > IMAGE_SIZE[1]:
                        break  # Прерываем, если строки больше не помещаются

                # Draw the character and get its bounding box
                char_box = draw_char_with_box(draw, char, font, x_offset, y_offset, angle)

                # Check if the box is within image boundaries
                if char_box[0] >= 0 and char_box[1] >= 0 and char_box[2] <= IMAGE_SIZE[0] and char_box[3] <= IMAGE_SIZE[1]:
                    text_boxes.append(char_box)

                # Update x_offset for the next character
                x_offset += char_width + random.randint(5, 10)

                # Update current_line_height
                char_height = font.getbbox(char)[3]
                if char_height > current_line_height:
                    current_line_height = char_height

            # Add some random spacing between lines
            y_offset += current_line_height + random.randint(5, 10)
            current_line_height = 0  # Reset for the next line

        # Добавление шума и вращения
        image = add_noise_and_rotation(image)

        # Сохраняем изображение
        image_path = os.path.join(output_dir, 'images', f'image_{i}.jpg')
        image.save(image_path)

        # Сохраняем разметку с увеличением боксов
        label_path = os.path.join(output_dir, 'labels', f'image_{i}.txt')
        with open(label_path, 'w') as label_file:
            for box in text_boxes:
                # Увеличиваем боксы на 2 пикселя для каждой стороны
                padding = 2
                x_min = max(0, box[0] - padding)
                y_min = max(0, box[1] - padding)
                x_max = min(IMAGE_SIZE[0], box[2] + padding)
                y_max = min(IMAGE_SIZE[1], box[3] + padding)

                # Сортировка координат
                x_min, x_max = sorted([x_min, x_max])
                y_min, y_max = sorted([y_min, y_max])

                # Преобразование координат в нормализованный формат
                x_center = (x_min + x_max) / 2 / IMAGE_SIZE[0]
                y_center = (y_min + y_max) / 2 / IMAGE_SIZE[1]
                width = (x_max - x_min) / IMAGE_SIZE[0]
                height = (y_max - y_min) / IMAGE_SIZE[1]

                # Ограничение значений в диапазоне [0, 1]
                x_center = max(0.0, min(1.0, x_center))
                y_center = max(0.0, min(1.0, y_center))
                width = max(0.0, min(1.0, width))
                height = max(0.0, min(1.0, height))

                # Записываем аннотацию
                label_file.write(f"{box[4]} {x_center} {y_center} {width} {height}\n")

# Генерация датасета
num_train = int(100 * TRAIN_RATIO)
num_valid = int(100 * VALID_RATIO)
num_test = 100 - num_train - num_valid

generate_image_and_labels(os.path.join(DATASET_DIR, 'train'), num_train)
generate_image_and_labels(os.path.join(DATASET_DIR, 'valid'), num_valid)
generate_image_and_labels(os.path.join(DATASET_DIR, 'test'), num_test)

def visualize_boxes(dataset_dir, proba_dir, num_images=2):
    """
    Визуализация боксов на изображениях из каждой папки (train, valid, test).
    Накладывает боксы на изображения и сохраняет результат в папке proba.

    :param dataset_dir: Путь к корневой папке с датасетом.
    :param proba_dir: Путь к папке, где будут сохранены визуализации.
    :param num_images: Количество изображений из каждой папки для проверки.
    """
    splits = ['train', 'valid', 'test']

    for split in splits:
        image_dir = os.path.join(dataset_dir, split, 'images')
        label_dir = os.path.join(dataset_dir, split, 'labels')
        image_files = os.listdir(image_dir)

        # Выбираем случайные изображения
        sampled_files = random.sample(image_files, min(num_images, len(image_files)))

        for image_file in sampled_files:
            # Открываем изображение
            image_path = os.path.join(image_dir, image_file)
            image = Image.open(image_path).convert('RGB')
            draw = ImageDraw.Draw(image)

            # Читаем аннотации
            label_path = os.path.join(label_dir, os.path.splitext(image_file)[0] + '.txt')
            with open(label_path, 'r') as label_file:
                for line in label_file:
                    parts = line.strip().split()
                    class_id = int(parts[0])
                    x_center = float(parts[1]) * IMAGE_SIZE[0]
                    y_center = float(parts[2]) * IMAGE_SIZE[1]
                    width = float(parts[3]) * IMAGE_SIZE[0]
                    height = float(parts[4]) * IMAGE_SIZE[1]

                    # Рассчитываем координаты бокса
                    x_min = x_center - width / 2
                    y_min = y_center - height / 2
                    x_max = x_center + width / 2
                    y_max = y_center + height / 2

                    # Проверка, что x_min <= x_max и y_min <= y_max
                    if x_min > x_max:
                        x_min, x_max = x_max, x_min
                    if y_min > y_max:
                        y_min, y_max = y_max, y_min

                    # Рисуем бокс и класс
                    draw.rectangle([x_min, y_min, x_max, y_max], outline='red', width=2)
                    draw.text((x_min, y_min - 10), CLASS_NAMES[class_id], fill='blue')

            # Сохраняем изображение с боксами
            output_path = os.path.join(proba_dir, f'{split}_{os.path.basename(image_file)}')
            image.save(output_path)
            print(f"Сохранено изображение с боксами: {output_path}")

# Вызов функции
visualize_boxes(DATASET_DIR, PROBA_DIR)
#font_path = random.choice(FONTS)
#print(f"Используемый шрифт: {font_path}")
#font = ImageFont.truetype(font_path, random.randint(20, 50))