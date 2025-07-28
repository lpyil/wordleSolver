import nltk
from nltk.corpus import words, wordnet

nltk.download('words')
nltk.download('wordnet')

word_length = 5
pattern = '_a___'  # Örnek: Son harf 'e'
must_include = set('as')  # Kelimede mutlaka 'o', 'r', 'e' harfleri olmalı
must_not_include = set('groupnimewtchbl')  # İçermemesi gereken harfler
excluded_positions = {
 
    's': [4]    

}



def check_pattern(w, pattern):
    for i, ch in enumerate(pattern):
        if ch != '_' and w[i] != ch:
            return False
    return True


def check_must_include(w, must_include, excluded_positions):
    w_set = set(w)
    if not must_include.issubset(w_set):
        return False
    for letter, positions in excluded_positions.items():
        for pos in positions:
            if w[pos] == letter:
                return False
    return True


def filter_wordlist(word_list):
    filtered = []
    for w in word_list:
        w = w.lower()
        if len(w) != word_length:
            continue
        if not check_pattern(w, pattern):
            continue
        if not check_must_include(w, must_include, excluded_positions):
            continue
        if set(w) & must_not_include:
            continue
        filtered.append(w)
    return filtered


# 1. nltk.words listesini filtrele
nltk_words = words.words()
filtered_nltk = set(filter_wordlist(nltk_words))

# 2. wordnet kelimeleri (lemma isimleri) filtrele
wordnet_words = set()
for syn in wordnet.all_synsets():
    for lemma in syn.lemmas():
        wordnet_words.add(lemma.name().lower())
filtered_wordnet = set(filter_wordlist(wordnet_words))

# 3. words.txt listesini oku ve filtrele
filtered_words_txt = set()
with open('words.txt', 'r') as f:
    words_txt = [line.strip().lower() for line in f]
    filtered_words_txt = set(filter_wordlist(words_txt))

# 3 listenin kesişimi (ortak kelimeler)
common_words = filtered_nltk & filtered_wordnet & filtered_words_txt

# Alt alta yazdır
print(f"{len(common_words)} ortak kelime bulundu:\n")
for w in sorted(common_words):
    print(w)
