import pandas as pd
import numpy as np
from tools.mutils.CorretingWords import correcting_text, translate


def merger(df: pd.DataFrame, translated=True) -> dict:
    x1=df.columns[0]
    y1=df.columns[1]
    x2=df.columns[2]
    y2=df.columns[3]
    letter=df.columns[6]
    translated = True
    # Определяем среднюю ширину буквы
    avg_width = np.mean(df[x2] - df[x1])
    max_dist_x = avg_width * 0.3
    # Определяем среднюю высоту буквы
    avg_height = np.mean(df[y2] - df[y1])
    max_dist_y= avg_height * 0.8

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

    words = []
    words_with_bbox = {}
    punto = {'dot': '.', 'comma': ',', 'quest': '?', 'excl': '!', 'dog': '@'}
    print("\t" * 4, len(lines))
    for line_df in lines:

        line_df = line_df.sort_values(by=x1).reset_index(drop=True)  # Сортируем по X
        print(line_df)
        current_word = line_df.iloc[0][letter]
        cur_word_x_min = line_df.iloc[0][x1]
        cur_word_y_min = line_df.iloc[0][y1]
        cur_word_x_max = line_df.iloc[0][x2]
        cur_word_y_max = line_df.iloc[0][y2]

        for i in range(1, len(line_df)):
            if line_df.iloc[i][x1] - line_df.iloc[i - 1][x2] <= max_dist_x:
                if line_df.iloc[i][letter] in punto.keys():
                    words.append(current_word)
                    cur_word_x_max = max(cur_word_x_max, line_df.iloc[i - 1][x2])
                    cur_word_y_max = max(cur_word_y_max, line_df.iloc[i - 1][y2])
                    cur_word_x_min = min(cur_word_x_min, line_df.iloc[i - 1][x1])
                    cur_word_y_min = min(cur_word_y_min, line_df.iloc[i - 1][y1])
                    tmp = {'x_min': float(cur_word_x_min), 'y_min': float(cur_word_y_min),
                           'x_max': float(cur_word_x_max), 'y_max': float(cur_word_y_max)}
                    words_with_bbox[current_word] = tmp
                    current_word = punto[line_df.iloc[i][letter]]
                    cur_word_x_min = line_df.iloc[i][x1]
                    cur_word_y_min = line_df.iloc[i][y1]
                    cur_word_x_max = line_df.iloc[i][x2]
                    cur_word_y_max = line_df.iloc[i][y2]
                elif line_df.iloc[i - 1][letter] in punto.keys():
                    current_word = line_df.iloc[i][letter]
                else:
                    current_word += line_df.iloc[i][letter]
            else:
                words.append(current_word)
                cur_word_x_max = max(cur_word_x_max, line_df.iloc[i - 1][x2])
                cur_word_y_max = max(cur_word_y_max, line_df.iloc[i - 1][y2])
                cur_word_x_min = min(cur_word_x_min, line_df.iloc[i - 1][x1])
                cur_word_y_min = min(cur_word_y_min, line_df.iloc[i - 1][y1])
                tmp = {'x_min': float(cur_word_x_min), 'y_min': float(cur_word_y_min),
                       'x_max': float(cur_word_x_max), 'y_max': float(cur_word_y_max)}
                print(tmp)
                words_with_bbox[current_word] = tmp
                current_word = line_df.iloc[i][letter]
                cur_word_x_min = line_df.iloc[i][x1]
                cur_word_y_min = line_df.iloc[i][y1]
                cur_word_x_max = line_df.iloc[i][x2]
                cur_word_y_max = line_df.iloc[i][y2]
        words.append(current_word)
        cur_word_x_max = max(cur_word_x_max, line_df.iloc[len(line_df) - 1][x2])
        cur_word_y_max = max(cur_word_y_max, line_df.iloc[len(line_df) - 1][y2])
        cur_word_x_min = min(cur_word_x_min, line_df.iloc[len(line_df) - 1][x1])
        cur_word_y_min = min(cur_word_y_min, line_df.iloc[len(line_df) - 1][y1])
        tmp = {'x_min': float(cur_word_x_min), 'y_min': float(cur_word_y_min), 'x_max': float(cur_word_x_max),
               'y_max': float(cur_word_y_max)}
        words_with_bbox[current_word] = tmp
        print(words_with_bbox)
    return [words_with_bbox, translate(correcting_text(words))]