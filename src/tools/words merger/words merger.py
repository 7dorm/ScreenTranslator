import pandas as pd
import numpy as np

def merger(file):
    d = pd.read_csv(file, sep="\s+", header=0)
    # создали таблицу данных df
    df = pd.DataFrame(data=d)
    x1=df.columns[0]
    y1=df.columns[1]
    x2=df.columns[2]
    y2=df.columns[3]
    letter=df.columns[6]

    # Определяем среднюю ширину буквы
    avg_width = np.mean(df[x2] - df[x1])
    max_dist_x = avg_width * 0.5
    # Определяем среднюю высоту буквы
    avg_height = np.mean(df[y2] - df[y1])
    max_dist_y= avg_height

    # Разделяем буквы на строки текста
    df = df.sort_values(by=y1).reset_index(drop=True) # Отсортировали по возрастанию y
    lines = []
    current_line = [df.iloc[0]]
    for i in range(1, len(df)):
        if df.iloc[i][y1] - df.iloc[i - 1][y1] <= max_dist_y:
            current_line.append(df.iloc[i])
        else:
            lines.append(pd.DataFrame(current_line))
            current_line = [df.iloc[i]]
    lines.append(pd.DataFrame(current_line))

    # Составляем слова
    words = []
    for line_df in lines:
        line_df = line_df.sort_values(by=x1).reset_index(drop=True)  # Сортируем по X
        current_word = line_df.iloc[0][letter]

        for i in range(1, len(line_df)):
            if line_df.iloc[i][x1] - line_df.iloc[i - 1][x2] <= max_dist_x:
                if line_df.iloc[i][letter] == 'dot':
                    current_word += '.'
                elif line_df.iloc[i][letter] == 'comma':
                    current_word += ','
                elif line_df.iloc[i][letter] == 'quest':
                    current_word += '?'
                elif line_df.iloc[i][letter] == 'excl':
                    current_word += '!'
                elif line_df.iloc[i][letter] == 'dog':
                    current_word += '@'
                else:
                    current_word += line_df.iloc[i][letter]
            else:
                words.append(current_word)
                current_word = line_df.iloc[i][letter]
        words.append(current_word)
    print(words)

def main():
    d = pd.DataFrame([
        (10, 10, 30, 50, 'П'),
        (35, 10, 55, 50, 'Р'),
        (60, 10, 80, 50, 'И'),
        (85, 10, 105, 50, 'В'),
        (110, 10, 130, 50, 'Е'),
        (135, 10, 155, 50, 'Т'),

        (10, 70, 30, 110, 'К'),
        (35, 70, 55, 110, 'А'),
        (60, 70, 80, 110, 'К')
    ], columns=['x1', 'y1', 'x2', 'y2', 'letter'])
    #merger(d)
    merger(filepath) # путь к файлу

if __name__ == "__main__":
    main()