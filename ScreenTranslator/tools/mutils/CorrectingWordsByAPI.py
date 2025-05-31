import requests
from itertools import product
from ScreenTranslator.constants import SIMILAR_SYMBOLS

def change_same_symbols(word):
    possible_chars = [SIMILAR_SYMBOLS.get(c, [c]) for c in word]
    combinations = [''.join(combo) for combo in product(*possible_chars)]
    return combinations

def get_closest_word(word):
    url = f"https://api.datamuse.com/words?sp={word}&max=1"
    response = requests.get(url)
    suggestions = response.json()
    if suggestions and 'score' in suggestions[0]: 
        return suggestions[0]["word"], suggestions[0]["score"]
    return word, 0

def checking_spaces(word):
    length = len(word)

    whole_word, score = get_closest_word(word)
    if whole_word == word:
        return word, score
    for i in range(1, length):
        left, right = word[:i], word[i:]
        url1 = f"https://api.datamuse.com/words?sp={left}&max=1"
        url2 = f"https://api.datamuse.com/words?sp={right}&max=1"
        response1 = requests.get(url1)
        response2 = requests.get(url2)
        suggestions1 = response1.json()
        suggestions2 = response2.json()
        if suggestions1 and suggestions2 and suggestions1[0]["word"] == left and suggestions2[0]["word"] == right:
            return f"{left} {right}", max(suggestions1[0].get("score", 0), suggestions2[0].get("score", 0))
    return word, 0

def correcting_text(words):
    length = len(words)
    for i in range(0, length):
        word = words[i]
        if word.isnumeric():
            continue
        
        possible_words = change_same_symbols(word)
        
        best_word = word
        best_score = 0
        for candidate in possible_words:
            candidate, score = checking_spaces(candidate)
            if " " in candidate:
                left, right = candidate.split(" ")
                left, left_score = get_closest_word(left)
                right, right_score = get_closest_word(right)
                candidate = f"{left} {right}"
                score = max(left_score, right_score)
            else:
                candidate, score = get_closest_word(candidate)
            
            if score > best_score:
                best_word = candidate
                best_score = score
        
        words[i] = best_word
    return words

if __name__ == "__main__":
    words1 = ["1s", "h0m135", "t1gr1s", "10@d", "para11e1", "p1ate", "53nd 80085", "p111ow"]
    words2 = correcting_text(words1)
    print(" ".join(words2))