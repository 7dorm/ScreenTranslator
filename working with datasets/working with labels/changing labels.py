import yaml
import os


def load_yaml(file_path):
    """Загрузить YAML файл."""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def save_yaml(data, file_path):
    """Сохранить YAML файл."""
    with open(file_path, 'w') as file:
        yaml.dump(data, file)


def map_classes(prev_classes, new_classes):
    """Создать отображение между старыми номерами классов и новыми."""
    mapping = {}
    normalized_new_classes = {name.lower(): idx for idx, name in enumerate(new_classes)}

    for old_idx, old_name in enumerate(prev_classes):
        normalized_name = old_name.lower()
        if normalized_name in normalized_new_classes:
            mapping[old_idx] = normalized_new_classes[normalized_name]
        else:
            print(f"Предупреждение: класс '{old_name}' отсутствует в новом списке. Он будет пропущен.")
    return mapping


def update_annotations(annotations_dir, mapping):
    """Обновить номера классов в аннотациях YOLO."""
    for root, _, files in os.walk(annotations_dir):
        for file in files:
            if file.endswith('.txt'):
                annotation_path = os.path.join(root, file)
                with open(annotation_path, 'r') as f:
                    lines = f.readlines()

                updated_lines = []
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) < 5:
                        continue  # Пропуск некорректных строк
                    old_class = int(parts[0])
                    if old_class in mapping:
                        new_class = mapping[old_class]
                        updated_lines.append(f"{new_class} {' '.join(parts[1:])}\n")


                # Записать обновленные аннотации
                with open(annotation_path, 'w') as f:
                    f.writelines(updated_lines)

def update_annotations2(annotations_dir, new_classes):
    """Обновить номера классов в аннотациях YOLO."""
    normalized_new_classes = {name: idx for idx, name in enumerate(new_classes)}
    for root, _, files in os.walk(annotations_dir):
        for file in files:
            if file.endswith('.txt'):
                annotation_path = os.path.join(root, file)
                with open(annotation_path, 'r') as f:
                    lines = f.readlines()

                updated_lines = []
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) < 5:
                        continue  # Пропуск некорректных строк
                    old_class = parts[0]
                    new_class = normalized_new_classes[old_class]
                    updated_lines.append(f"{new_class} {' '.join(parts[1:])}\n")


                # Записать обновленные аннотации
                with open(annotation_path, 'w') as f:
                    f.writelines(updated_lines)


def main(prev_yaml_path, data_yaml_path):
    """Основной процесс преобразования аннотаций."""
    # Загрузить YAML файлы
    prev_data = load_yaml(prev_yaml_path)
    new_data = load_yaml(data_yaml_path)

    prev_classes = prev_data['names']
    new_classes = new_data['names']

    # Создать отображение между старыми и новыми классами
    class_mapping = map_classes(prev_classes, new_classes)
    print(f"Сопоставление классов: {class_mapping}")

    # Обновить аннотации в папках train, val, test
    annotations_dir = '/Users/...'
    print(f"Обновление аннотаций в папке: {annotations_dir}")
    update_annotations(annotations_dir, class_mapping)


if __name__ == "__main__":
    # Путь к классам, которые надо исправить
    prev_yaml_path = '/Users/...'
    # Путь к классам, на которые надо исправить
    data_yaml_path = '/Users/...'

    main(prev_yaml_path, data_yaml_path)