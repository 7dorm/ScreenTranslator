import os
import json

input_file = "en_US-large.txt"

def generate_ngrams(word, n):
    """Разделяет слово на n-граммы"""
    return [word[i:i + n] for i in range(len(word) - n + 1)]

def build_ngram_index(n):
    output_file = f"mutils/{n}_gramm_index.json"

    if os.path.exists(output_file):
        print(f"Файл {output_file} уже существует. Пропускаем.")
        return

    if not os.path.exists(input_file):
        print(f"Файл {input_file} не найден.")
        return

    ngram_index = {}

    with open(input_file, "r", encoding="utf-8") as f:
        words = [line.strip() for line in f.readlines() if line.strip()]

    for word in words:
        ngrams = generate_ngrams(word, n)
        for ngram in ngrams:
            if ngram not in ngram_index:
                ngram_index[ngram] = set()
            ngram_index[ngram].add(word)

    # Преобразуем множества в списки для сохранения в JSON
    ngram_index = {key: list(value) for key, value in ngram_index.items()}

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(ngram_index, f, ensure_ascii=False, indent=4)

    print(f"Файл {output_file} успешно создан.")



def ngramm(words, n):
    
    build_ngram_index(n)
    for word in words:
        splt = [word[i:i+n] for i in range(len(word) - n + 1)]
        print(splt)

if __name__ == "__main__":
    ngramm(["аобоба"], 3)