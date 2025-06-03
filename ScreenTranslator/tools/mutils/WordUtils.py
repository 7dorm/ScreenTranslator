import pandas as pd
import numpy as np
from ScreenTranslator.tools.mutils.CorrectingWords import correcting_text, translate

def merger(df: pd.DataFrame) -> list:
    x1 = df.columns[0]
    y1 = df.columns[1]
    x2 = df.columns[2]
    y2 = df.columns[3]
    letter = df.columns[6]
    
    avg_width = np.mean(df[x2] - df[x1])
    max_dist_x = avg_width * 0.3

    avg_height = np.mean(df[y2] - df[y1])
    max_dist_y = avg_height * 0.8

    df = df.sort_values(by=y1).reset_index(drop=True)
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
    words_with_bbox = []

    for line_df in lines:
        line_df = line_df.sort_values(by=x1).reset_index(drop=True)
        current_word = str(line_df.iloc[0][letter])
        cur_word_x_min = line_df.iloc[0][x1]
        cur_word_y_min = line_df.iloc[0][y1]
        cur_word_x_max = line_df.iloc[0][x2]
        cur_word_y_max = line_df.iloc[0][y2]

        for i in range(1, len(line_df)):
            if line_df.iloc[i][x1] - line_df.iloc[i - 1][x2] <= max_dist_x:
                current_word += str(line_df.iloc[i][letter])
                cur_word_x_max = max(cur_word_x_max, line_df.iloc[i][x2])
                cur_word_y_max = max(cur_word_y_max, line_df.iloc[i][y2])
                cur_word_x_min = min(cur_word_x_min, line_df.iloc[i][x1])
                cur_word_y_min = min(cur_word_y_min, line_df.iloc[i][y1])
            else:
                words.append(current_word)
                words_with_bbox.append({
                    current_word: {
                        'x_min': float(cur_word_x_min),
                        'y_min': float(cur_word_y_min),
                        'x_max': float(cur_word_x_max),
                        'y_max': float(cur_word_y_max)
                    }
                })
                current_word = str(line_df.iloc[i][letter])
                cur_word_x_min = line_df.iloc[i][x1]
                cur_word_y_min = line_df.iloc[i][y1]
                cur_word_x_max = line_df.iloc[i][x2]
                cur_word_y_max = line_df.iloc[i][y2]
        
        words.append(current_word)
        words_with_bbox.append({
            current_word: {
                'x_min': float(cur_word_x_min),
                'y_min': float(cur_word_y_min),
                'x_max': float(cur_word_x_max),
                'y_max': float(cur_word_y_max)
            }
        })

    original_words = " ".join(words)
    original_translation = translate(original_words)
    corrected_words = " ".join(correcting_text(words))
    corrected_translation = translate(corrected_words)

    return [
        words_with_bbox,
        original_words,
        original_translation,
        corrected_words,
        corrected_translation
    ]
