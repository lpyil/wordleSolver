def get_user_input():
    pattern = input("Kelime deseni (örnek: '_a___'): ").strip()
    must_include = set(input("Kelimenin içermesi gereken harfler (örnek: 'as'): ").strip())
    must_not_include = set(input("Kelimenin içermemesi gereken harfler (örnek: 'groupnimewtchbl'): ").strip())
    excluded_positions = {}
    while True:
        letter = input("Hariç tutulacak harf (çıkmak için Enter): ").strip()
        if not letter:
            break
        positions = input(f"{letter} harfinin bulunmaması gereken pozisyonlar (örnek: '1,3'): ").strip()
        excluded_positions[letter] = [int(pos) - 1 for pos in positions.split(',') if pos.isdigit()]
    return pattern, must_include, must_not_include, excluded_positions