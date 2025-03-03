import os
import yaml
import shutil
import numpy as np
import random
from tqdm import tqdm
from PIL import Image, ImageDraw
from tools.shift import shift_image_and_boxes_no_crop
from tools.scale import compress_image_and_boxes
from tools.rotate import rotate_image_and_boxes
from tools.cilinder import stretch_image_on_tilted_cylinder_and_adjust_boxes as stretch_image_on_cylinder_and_adjust_boxes
from tools.aff import affine_transform_image_and_boxes

def create_and_clear_directory(path):
    if os.path.exists(path):
        #shutil.rmtree(path)
        print(f"Директория '{path}' удалена.")
    os.makedirs(path)
    print(f"Директория '{path}' создана.")

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data


def save_image_and_boxes(image, image_path, boxes):
    # Сохраняем изображение
    image.save(image_path)
    
    # Путь для сохранения аннотаций
    labels_dir = os.path.join(os.path.split(image_path)[0], '..', 'labels')
    os.makedirs(labels_dir, exist_ok=True)
    txt_path = os.path.join(labels_dir, os.path.splitext(os.path.split(image_path)[1])[0] + '.txt')
    
    with open(txt_path, 'w') as f:
        for box in boxes:
            cls, x_center, y_center, box_width, box_height = box
            cls = int(cls)
            # Убеждаемся, что координаты находятся в диапазоне [0, 1]
            x_center = min(max(x_center, 0), 1)
            y_center = min(max(y_center, 0), 1)
            box_width = min(max(box_width, 0), 1)
            box_height = min(max(box_height, 0), 1)
            line = f"{cls} {x_center} {y_center} {box_width} {box_height}\n"
            f.write(line)

def draw_boxes_on_image(image, boxes, labels):
    draw = ImageDraw.Draw(image)
    width, height = image.size
    for box in boxes:
        cls, x_center, y_center, box_width, box_height = box
        
        # Переводим координаты из диапазона [0, 1] в пиксели
        x_center_pixel = x_center * width
        y_center_pixel = y_center * height
        box_width_pixel = box_width * width
        box_height_pixel = box_height * height
        
        # Вычисляем координаты углов прямоугольника
        x_min = x_center_pixel - (box_width_pixel / 2)
        y_min = y_center_pixel - (box_height_pixel / 2)
        x_max = x_center_pixel + (box_width_pixel / 2)
        y_max = y_center_pixel + (box_height_pixel / 2)
        
        # Рисуем прямоугольник
        draw.rectangle([x_min, y_min, x_max, y_max], outline="red", width=2)
        
        # Наносим текст с именем класса
        class_name = labels[int(cls)]
        text_position = (x_min, y_min)
        draw.text(text_position, class_name, fill="black")
    return image


  # Импортируем библиотеку для прогресс-бара

def process_dataset(data, input_base_path, output_base_path, subset, labels):
    image_counter = 0  # Инициализация счётчика
    for image_dir in data[subset]:
        if not image_dir.startswith('../'):
            print(f"Неподдерживаемый формат пути: {image_dir}")
            continue
        relative_path = image_dir[3:]  # Удаляем '../'
        input_dir = os.path.join(input_base_path, relative_path)
        output_dir = os.path.join(output_base_path, subset, 'images')
        os.makedirs(output_dir, exist_ok=True)

        os.makedirs(os.path.join(output_base_path, subset, 'labels'), exist_ok=True)
        
        # Директория для изображений с боксами
        boxes_dir = os.path.join(output_base_path, 'boxes', 'images')
        os.makedirs(boxes_dir, exist_ok=True)
        
        # Получаем список изображений
        image_files = [f for f in os.listdir(input_dir) if f.endswith(('.jpg', '.png'))]
        
        # Прогресс-бар для обработки изображений
        for image_name in tqdm(image_files, desc=f"Обработка {subset}", unit="изображений"):
            image_path = os.path.join(input_dir, image_name)
            txt_name = os.path.splitext(image_name)[0] + '.txt'
            txt_path = os.path.join(input_dir, '../labels', txt_name)
            boxes = []
            if os.path.exists(txt_path):
                with open(txt_path, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) != 5:
                            continue
                        cls, x_center, y_center, box_width, box_height = map(float, parts)
                        boxes.append([cls, x_center, y_center, box_width, box_height])
            image = Image.open(image_path)

            new_image = image
            new_boxes = boxes
            #new_image, new_boxes = compress_image_and_boxes(image, boxes, scale=1)
            #new_image, new_boxes = rotate_image_and_boxes(image, boxes, 15)
            if random.random() <= 0.80:
                new_image, new_boxes = shift_image_and_boxes_no_crop(new_image, new_boxes, int(random.random() * 800) - 400, int(random.random() * 800)-400)
            if random.random() >= 0.93:
                new_image, new_boxes = stretch_image_on_cylinder_and_adjust_boxes(new_image, new_boxes, 0, int(random.random() * 500) - 250)

            if random.random() >= 0.80:
                angle1 = int(random.random() * 30) - 15  # в градусах
                theta1 = np.deg2rad(angle1)

                angle2 = int(random.random() * 30) - 15
                theta2 = np.deg2rad(angle2)
                transform_matrix = np.array([
                    [1, np.tan(theta1), 0],
                    [np.tan(theta2), 1, 0],
                    [0, 0, 1]
                ])

                new_image, new_boxes = affine_transform_image_and_boxes(new_image, new_boxes, transform_matrix)
        
            save_image_and_boxes(new_image, os.path.join(output_dir, image_name), new_boxes)
            
            # Сохраняем каждое 10-е изображение с боксами
            image_counter += 1  # Увеличиваем счётчик
            if image_counter % 10 == 0:
                # Копируем изображение для нанесения квадратов
                #print(boxes)
                #print(new_boxes)
                image_with_boxes = new_image.copy()
                image_with_boxes = draw_boxes_on_image(image_with_boxes, new_boxes, labels)
                
                # Сохраняем изображение с квадратами
                image_with_boxes_path = os.path.join(boxes_dir, image_name)
                image_with_boxes.save(image_with_boxes_path)
                #print(f"Сохранено изображение с квадратами: {image_name}")
    
    # После обработки всех изображений в подмножестве, сбрасываем счётчик
    image_counter = 0

def create_data_yaml(data, input_base_path, output_base_path):
    new_data = {}
    for subset in ['test']:
        new_data[subset] = []
        for image_dir in data[subset]:
            if not image_dir.startswith('../'):
                print(f"Неподдерживаемый формат пути: {image_dir}")
                continue
            relative_path = image_dir[3:]
            new_path = os.path.join(output_base_path, subset, relative_path, 'images')
            new_data[subset].append(new_path)
    new_data['nc'] = data['nc']
    new_data['names'] = data['names']
    with open(os.path.join(output_base_path, 'data.yaml'), 'w') as f:
        yaml.dump(new_data, f)
    print("Файл 'data.yaml' создан.")

def main():
    input_base_path = '../'
    output_base_path = './dataset'
    
    # Создаем директорию для сохранения изображений с боксами
    boxes_output_path = os.path.join(output_base_path, 'boxes')
    create_and_clear_directory(output_base_path)
    create_and_clear_directory(boxes_output_path)
    
    # Создаем основную директорию dataset
    
    # Загружаем данные из data.yaml
    data = load_yaml('../datasets/norm/data.yaml')
    
    # Определяем метки классов
    labels = data['names']
    
    # Обрабатываем train, val, test
    for subset in ['train', 'val', 'test']:
        process_dataset(data, input_base_path, output_base_path, subset, labels)
    
    # Создаём новый data.yaml
    create_data_yaml(data, input_base_path, output_base_path)

if __name__ == "__main__":
    main()