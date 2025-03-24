import requests

def change_same_symbols(word):
    symbols = {"@": "a", "3": "e", "6": "b", "0": "o", "8": "B", "1": "l", "7": "t", "5": "s"}
    return "".join(symbols.get(c, c) for c in word)

def get_closest_word(word):
    url = f"https://api.datamuse.com/words?sp={word}&max=1"
    response = requests.get(url)
    suggestions = response.json()
    if suggestions:
        return suggestions[0]["word"]
    return word

def checking_spaces(word):
    length = len(word)
    if get_closest_word(word) == word:
        return word
    for i in range(1, length):
        left, right = word[:i], word[i:]
        url1 = f"https://api.datamuse.com/words?sp={left}&max=1"
        url2 = f"https://api.datamuse.com/words?sp={right}&max=1"
        response1 = requests.get(url1)
        response2 = requests.get(url2)
        suggestions1 = response1.json()
        suggestions2 = response2.json()
        if suggestions1 and suggestions2 and suggestions1[0]["word"] == left and suggestions2[0]["word"] == right:
            return f"{left} {right}"
    return word

def correcting_text(words):
    length = len(words)
    for i in range(0, length):
        word = words[i]
        if word.isnumeric():
            continue
        word = change_same_symbols(word)
        word = checking_spaces(word)
        if " " in word:
            left = word.split(" ")[0]
            right = word.split(" ")[1]
            left = get_closest_word(left)
            right = get_closest_word(right)
            word = f"{left} {right}"
        else:
            word = get_closest_word(word)
        words[i] = word
    return words

words1 = ["th3@pple", "34", "of", "exampl", "1s", "g00d"]
words2 = correcting_text(words1)
print(" ".join(words2))