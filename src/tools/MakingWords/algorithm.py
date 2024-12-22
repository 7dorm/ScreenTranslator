import math
import argparse

# Список символов
s = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 
     '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'dot', 'comma', 'quest', 'excl', 'dog']

class Letter:
    def __init__(self, ids, conf, bbx_x, bbx_y, bbx_w, bbx_h):
        self.letter = s[int(ids)]
        self.conf = float(conf)
        self.bbx = [float(bbx_x), float(bbx_y), float(bbx_w), float(bbx_h)]

    def iou(self, other):
        """Расчет пересечения (IoU) двух bounding боксов"""
        x1 = max(self.bbx[0], other.bbx[0])
        y1 = max(self.bbx[1], other.bbx[1])
        x2 = min(self.bbx[0] + self.bbx[2], other.bbx[0] + other.bbx[2])
        y2 = min(self.bbx[1] + self.bbx[3], other.bbx[1] + other.bbx[3])
        
        inter_area = max(0, x2 - x1) * max(0, y2 - y1)
        self_area = self.bbx[2] * self.bbx[3]
        other_area = other.bbx[2] * other.bbx[3]
        
        union_area = self_area + other_area - inter_area
        return inter_area / union_area if union_area > 0 else 0

    def __repr__(self):
        return f"{self.letter} ({self.conf:.2f}) [{', '.join(map(str, self.bbx))}]"

def filter_overlapping(elements, iou_threshold=0.5):
    """Удаляет сильно пересекающиеся bounding боксы с учетом confidence"""
    filtered = []
    elements.sort(key=lambda x: -x.conf)  # Сортируем по убыванию confidence
    used = set()

    for i, letter in enumerate(elements):
        if i in used:
            continue
        for j, other in enumerate(elements):
            if i != j and j not in used and letter.iou(other) > iou_threshold:
                if letter.conf >= other.conf:
                    used.add(j)
                else:
                    used.add(i)
                    break
        else:
            filtered.append(letter)
    return filtered

def group_letters_to_words(letters, spacing_threshold=20, line_threshold=30):
    """Группирует буквы в слова с учетом пробелов и переносов строки"""
    letters.sort(key=lambda x: x.bbx[0])  # Сортируем по x-координате
    result = []
    current_line = []
    prev_letter = None

    for letter in letters:
        if prev_letter:
            # Проверяем расстояние между буквами
            dx = letter.bbx[0] - (prev_letter.bbx[0] + prev_letter.bbx[2])
            dy = abs(letter.bbx[1] - prev_letter.bbx[1])
            
            if dy > line_threshold:
                # Перенос строки
                result.append("".join(current_line))
                result.append("\n")
                current_line = [letter.letter]
            elif dx > spacing_threshold:
                # Добавление пробела
                current_line.append(" ")
                current_line.append(letter.letter)
            else:
                current_line.append(letter.letter)
        else:
            current_line.append(letter.letter)
        
        prev_letter = letter

    if current_line:
        result.append("".join(current_line))

    return "".join(result)

def main():
    # Парсер аргументов командной строки
    parser = argparse.ArgumentParser(description="Process a file with bounding boxes and letters.")
    parser.add_argument("file", help="Path to the input file")
    args = parser.parse_args()

    # Чтение данных из файла
    with open(args.file, 'r') as f:
        lines = [i.split() for i in f.readlines()]
        elements = [Letter(*i) for i in lines]

    # Фильтрация пересечений
    filtered_elements = filter_overlapping(elements)

    # Группировка в слова
    text = group_letters_to_words(filtered_elements)

    # Вывод результата
    print(text)

if __name__ == "__main__":
    main()
