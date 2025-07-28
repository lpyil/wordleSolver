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


def filter_wordlist(word_list, word_length, pattern, must_include, must_not_include, excluded_positions):
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