import os
import cv2

# Папки с изображениями и разметкой
IMAGE_DIR = "dataset/images"
LABEL_DIR = "dataset/labels"
OUTPUT_DIR = "dataset/visualized"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Символы и их классы
CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
CLASS_TO_CHAR = {i: char for i, char in enumerate(CHARACTERS)}

def visualize_image(image_path, label_path, output_path):
    """Рисует bounding boxes на изображении на основе разметки YOLO."""
    image = cv2.imread(image_path)

    with open(label_path, "r") as f:
        lines = f.readlines()

    img_h, img_w, _ = image.shape

    for line in lines:
        parts = line.strip().split()
        class_id = int(parts[0])  # Символ (индекс)
        x_center, y_center, width, height = map(float, parts[1:])

        # Преобразуем в пиксели
        x1 = int((x_center - width / 2) * img_w)
        y1 = int((y_center - height / 2) * img_h)
        x2 = int((x_center + width / 2) * img_w)
        y2 = int((y_center + height / 2) * img_h)

        # Рисуем bounding box
        color = (0, 255, 0)  # Зеленый
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

        # Подпись (буква)
        label = CLASS_TO_CHAR[class_id]
        cv2.putText(image, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    # Сохраняем визуализированное изображение
    cv2.imwrite(output_path, image)


# Обрабатываем все изображения
for filename in os.listdir(IMAGE_DIR):
    if filename.endswith(".png"):
        image_path = os.path.join(IMAGE_DIR, filename)
        label_path = os.path.join(LABEL_DIR, filename.replace(".png", ".txt"))
        output_path = os.path.join(OUTPUT_DIR, filename)

        if os.path.exists(label_path):
            visualize_image(image_path, label_path, output_path)
            print(f"Saved visualization {output_path}")

print("Визуализация завершена!")
