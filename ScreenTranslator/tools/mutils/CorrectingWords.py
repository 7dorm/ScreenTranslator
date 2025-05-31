import json
import string
from itertools import product
from deep_translator import GoogleTranslator
from ScreenTranslator.constants import SIMILAR_SYMBOLS, RESOURCES_3_GRAMM_INDEX

def change_same_symbols(word):
    possible_chars = [SIMILAR_SYMBOLS.get(c, [c]) for c in word]
    combinations = [''.join(combo) for combo in product(*possible_chars)]
    return combinations

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
            if words and word in words:
                return [word]
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
    return closest_words

def get_closest_word(word, sim_words):
    if word in sim_words:
        return word
    distances = dict()
    for one_word in sim_words:
        distances[one_word] = levenshtein_dp(word, one_word)
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
    dict_file = open(RESOURCES_3_GRAMM_INDEX, "r")
    dictionary = json.load(dict_file)
    length = len(words)

    for i in range(0, length):
        word = words[i].lower()
        if word.isnumeric() or word in ['.', ',', '?', '!', '@']:
            continue
        
        possible_words = change_same_symbols(word)
        
        best_word = word
        min_distance = float('inf')
        for candidate in possible_words:
            candidate = checking_spaces(candidate, dictionary)
            if " " in candidate:
                left, right = candidate.split(" ")
                left = get_closest_word(left, get_closest_words(left, dictionary))
                right = get_closest_word(right, get_closest_words(right, dictionary))
                candidate = f"{left} {right}"
            else:
                candidate_words = get_closest_words(candidate, dictionary)
                candidate = get_closest_word(candidate, candidate_words)
            
            distance = levenshtein_dp(word, candidate)
            if distance < min_distance:
                min_distance = distance
                best_word = candidate
        
        words[i] = best_word
    return words

def translate(text):
    print('test', ' '.join(text))
    t = GoogleTranslator(source='english', target='russian').translate(' '.join(text))
    print(t)
    return t


if __name__ == "__main__":
    words1 = ["1s", "h0m135", "t1gr1s", "10@d", "para11e1", "p1ate", "53nd 80085", "p111ow"]
    words2 = correcting_text(words1)
    print(" ".join(words2))