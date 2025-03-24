import json
import string
from deep_translator import GoogleTranslator, single_detection


def change_same_symbols(word):
    symbols = {"@": "a", "3": "e", "6": "b", "0": "o", "8": "B", "1": "i", "7": "t", "5": "s", "9": "g"}
    return "".join(symbols.get(c, c) for c in word)

def make_ngramms(word, n):
    length = len(word)
    ngramms = []
    for i in range(0, length - n + 1):
        ngramms.append(word[i:i + n])
    return ngramms

def checking_spaces(word, dictionary):
    return word

def get_closest_words(word, dictionary):
    n = 3
    ngramms = make_ngramms(word, n)
    alphabet = string.ascii_lowercase
    sim_words = dict()
    for ngramm in ngramms:
        if ngramm in dictionary:
            words = dictionary[ngramm]
            for one_word in words:
                if len(one_word) > len(word) + 1 or len(one_word) < len(word) - 1:
                    continue
                if one_word in sim_words:
                    sim_words[one_word] += 2
                else:
                    sim_words[one_word] = 2
        for i in range(n):
            for letter in alphabet:
                if letter != ngramm[i]:
                    variant = ngramm[:i] + letter + ngramm[i + 1:]
                    if variant in dictionary:
                        words = dictionary[variant]
                        for one_word in words:
                            if len(one_word) > len(word) + 1 or len(one_word) < len(word) - 1:
                                continue
                            if one_word in sim_words:
                                sim_words[one_word] += 1.5
                            else:
                                sim_words[one_word] = 1.5
    if not sim_words:
        return [word]
    max_value = max(sim_words.values())
    closest_words = [k for k, v in sim_words.items() if v >= max_value - 2]
    #for i in closest_words:
    #    print(i, sim_words[i])
    return closest_words

def get_closest_word(word, sim_words):
    if word in sim_words:
        return word
    distances = dict()
    for one_word in sim_words:
        distances[one_word] = levenshtein_dp(word, one_word)
    #print(distances)
    min_value = min(distances.values())
    #distances_n = [k for k, v in distances.items() if v == min_value]
    #for i in distances_n:
    #    print(i, distances[i])
    return min(distances, key=distances.get)

def levenshtein_dp(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i
            else:
                cost = 0 if s1[i - 1] == s2[j - 1] else 1
                dp[i][j] = min(dp[i - 1][j] + 1,
                               dp[i][j - 1] + 1,
                               dp[i - 1][j - 1] + cost)
    return dp[m][n]

def correcting_text(words):
    dict_file = open("3_gramm_index.json", "r")
    dictionary = json.load(dict_file)
    length = len(words)
    for i in range(0, length):
        word = words[i].lower()
        if word.isnumeric():
            continue
        word = change_same_symbols(word)
        #print(word)
        #word = checking_spaces(word, dictionary)
        if " " in word:
            left = word.split(" ")[0]
            right = word.split(" ")[1]
            left = get_closest_word(left, get_closest_words(left, dictionary))
            right = get_closest_word(right, get_closest_words(right, dictionary))
            word = f"{left} {right}"
        else:
            word = get_closest_word(word, get_closest_words(word, dictionary))
        words[i] = word
    return words

def translate(text):
    return GoogleTranslator(source='auto', target='ru').translate(text=" ".join(text))

