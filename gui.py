import tkinter as tk
from tkinter import messagebox
from word_filter import filter_wordlist
import nltk
from nltk.corpus import words, wordnet
from nltk.data import find

# NLTK veri setlerini kontrol et ve indir
try:
    find('corpora/words.zip')  # 'words' veri seti kontrol ediliyor
except LookupError:
    nltk.download('words')

try:
    find('corpora/wordnet.zip')  # 'wordnet' veri seti kontrol ediliyor
except LookupError:
    nltk.download('wordnet')

excluded_positions_entries = {}

def generate_pattern():
    """Kullanıcının girdiği kelime uzunluğuna göre düzenlenebilir bir desen oluşturur."""
    try:
        word_length = int(word_length_entry.get().strip())
        if word_length <= 0:
            raise ValueError

        # Mevcut desen alanını temizle
        for widget in pattern_frame.winfo_children():
            widget.destroy()

        # pattern_entries listesini sıfırla
        global pattern_entries
        pattern_entries = []

        # Yeni desen alanını oluştur
        for i in range(word_length):
            entry = tk.Entry(pattern_frame, width=2, justify="center")  # Daha dar giriş alanı
            entry.grid(row=0, column=i, padx=2, pady=2)
            entry.insert(0, "_")  # Varsayılan olarak alt çizgi
            pattern_entries.append(entry)

            # Pozisyon etiketlerini ekle
            label = tk.Label(pattern_frame, text=str(i + 1))
            label.grid(row=1, column=i, padx=2, pady=2)

    except ValueError:
        messagebox.showerror("Hata", "Geçerli bir kelime uzunluğu girin!")

def add_excluded_positions():
    """Dinamik olarak hariç tutulacak pozisyon giriş alanları ekler."""
    must_include = must_include_entry.get().strip()
    for letter in must_include:
        if letter not in excluded_positions_entries:
            row = len(excluded_positions_entries) + 4
            excluded_position = ExcludedPosition(letter, row, scrollable_frame)
            excluded_positions_entries[letter] = excluded_position

    # Dinamik alanlar eklendikten sonra butonları yeniden yerleştir
    reposition_buttons()

def reposition_buttons():
    """Dinamik olarak eklenen alanlardan sonra butonları yeniden yerleştirir."""
    current_row = len(excluded_positions_entries) + 4
    add_positions_button.grid(row=current_row, column=0, columnspan=2)
    run_button.grid(row=current_row + 1, column=0, columnspan=2)
    clear_button.grid(row=current_row + 2, column=0, columnspan=2)
    result_text.grid(row=current_row + 3, column=0, columnspan=2)

def run_solver():
    # Kullanıcı girdilerini al
    pattern = get_pattern()  # Deseni Entry alanlarından al
    must_include = set(must_include_entry.get().strip())
    must_not_include = set(must_not_include_entry.get().strip())
    excluded_positions = {}

    # Hariç tutulacak harf ve pozisyonları al
    for letter, excluded_position in excluded_positions_entries.items():
        pos_text = excluded_position.entry.get().strip()
        if pos_text:
            excluded_positions[letter] = [int(pos) - 1 for pos in pos_text.split(',') if pos.isdigit()]

    # Girdilerin doğruluğunu kontrol et
    if not pattern or len(pattern) == 0:
        messagebox.showerror("Hata", "Kelime deseni boş olamaz!")
        return

    word_length = len(pattern)

    # 1. nltk.words listesini filtrele
    global nltk_words, wordnet_words
    nltk_words = words.words()
    wordnet_words = set()
    for syn in wordnet.all_synsets():
        for lemma in syn.lemmas():
            wordnet_words.add(lemma.name().lower())
    filtered_nltk = set(filter_wordlist(nltk_words, word_length, pattern, must_include, must_not_include, excluded_positions))
    filtered_wordnet = set(filter_wordlist(wordnet_words, word_length, pattern, must_include, must_not_include, excluded_positions))

    # 3. words.txt listesini oku ve filtrele
    try:
        with open('words.txt', 'r') as f:
            words_txt = [line.strip().lower() for line in f]
            filtered_words_txt = set(filter_wordlist(words_txt, word_length, pattern, must_include, must_not_include, excluded_positions))
    except FileNotFoundError:
        messagebox.showerror("Hata", "words.txt dosyası bulunamadı!")
        return

    # 3 listenin kesişimi (ortak kelimeler)
    common_words = filtered_nltk & filtered_wordnet & filtered_words_txt

    # Sonuçları göster
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f"{len(common_words)} uygun kelime bulundu:\n\n")
    for word in sorted(common_words):
        result_text.insert(tk.END, word + "\n")

    # Harf sıklığını analiz et ve önerilen kelimeleri bul
    if common_words:
        suggested_words = suggest_words(common_words, word_length)
        result_text.insert(tk.END, "\nÖnerilen Kelimeler:\n")
        for word in suggested_words:
            result_text.insert(tk.END, word + "\n")

def suggest_words(common_words, word_length):
    """Harf sıklığını analiz ederek önerilen kelimeleri döndürür."""
    # Harf sıklığını pozisyon bazında hesapla
    position_frequency = [{} for _ in range(word_length)]
    for word in common_words:
        for i, letter in enumerate(word):
            if letter not in position_frequency[i]:
                position_frequency[i][letter] = 0
            position_frequency[i][letter] += 1

    # En sık kullanılan harfleri pozisyon bazında bul
    most_frequent_letters = []
    for freq in position_frequency:
        if freq:
            most_frequent_letters.append(max(freq, key=freq.get))
        else:
            most_frequent_letters.append(None)

    # Önerilen kelimeleri seç
    suggested_words = []
    for word in common_words:
        match_score = sum(1 for i, letter in enumerate(word) if letter == most_frequent_letters[i])
        suggested_words.append((match_score, word))

    # Skora göre sırala ve en iyi 3 kelimeyi döndür
    suggested_words.sort(reverse=True, key=lambda x: x[0])
    return [word for _, word in suggested_words[:3]]

def clear_all():
    """Tüm giriş alanlarını ve sonuçları temizler."""
    word_length_entry.delete(0, tk.END)
    must_include_entry.delete(0, tk.END)
    must_not_include_entry.delete(0, tk.END)
    result_text.delete(1.0, tk.END)

    # Kelime deseni alanını temizle
    clear_widgets(pattern_frame)
    global pattern_entries
    pattern_entries = []

    # Hariç tutulacak pozisyon giriş alanlarını temizle
    for letter, excluded_position in excluded_positions_entries.items():
        excluded_position.destroy()
    excluded_positions_entries.clear()

    reposition_buttons()

def get_pattern():
    """Deseni Entry alanlarından al ve birleştir."""
    return "".join(entry.get().strip() for entry in pattern_entries)

def clear_widgets(frame):
    """Belirtilen çerçevedeki tüm widget'ları temizler."""
    for widget in frame.winfo_children():
        widget.destroy()

class ExcludedPosition:
    def __init__(self, letter, row, frame):
        self.letter = letter
        self.label = tk.Label(frame, text=f"{letter.upper()} Harfinin Hariç Pozisyonları (örnek: 1,3):")
        self.label.grid(row=row, column=0, sticky="w")
        self.entry = tk.Entry(frame, width=30)
        self.entry.grid(row=row, column=1)

    def destroy(self):
        self.label.destroy()
        self.entry.destroy()

# Tkinter arayüzü
root = tk.Tk()
root.title("Wordle Solver")

# Pencere boyutunu ayarla (örneğin, 800x600 piksel)
root.geometry("800x600")

# Ana çerçeve
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=1)

# Canvas ve ScrollBar
canvas = tk.Canvas(main_frame)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

scrollable_frame = tk.Frame(canvas)

# Scrollable frame'i canvas'a ekle
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Girdi alanları
tk.Label(scrollable_frame, text="Kelime Uzunluğu:").grid(row=0, column=0, sticky="w")
word_length_entry = tk.Entry(scrollable_frame, width=30)
word_length_entry.grid(row=0, column=1)

generate_pattern_button = tk.Button(scrollable_frame, text="Desen Oluştur", command=generate_pattern)
generate_pattern_button.grid(row=0, column=2)

tk.Label(scrollable_frame, text="Kelime Deseni (örnek: _a___):").grid(row=1, column=0, sticky="w")
pattern_entry = tk.Entry(scrollable_frame, width=30)
pattern_entry.grid(row=1, column=1)
pattern_entry.config(state="readonly")

tk.Label(scrollable_frame, text="İçermesi Gereken Harfler (örnek: as):").grid(row=2, column=0, sticky="w")
must_include_entry = tk.Entry(scrollable_frame, width=30)
must_include_entry.grid(row=2, column=1)

tk.Label(scrollable_frame, text="İçermemesi Gereken Harfler (örnek: groupnimewtchbl):").grid(row=3, column=0, sticky="w")
must_not_include_entry = tk.Entry(scrollable_frame, width=30)
must_not_include_entry.grid(row=3, column=1)

# Desen alanı için bir çerçeve
pattern_frame = tk.Frame(scrollable_frame)
pattern_frame.grid(row=1, column=1, sticky="w")
pattern_entries = []

# Dinamik pozisyon ekleme butonu
add_positions_button = tk.Button(scrollable_frame, text="Hariç Pozisyonları Ekle", command=add_excluded_positions)
add_positions_button.grid(row=4, column=0, columnspan=2)

# Çalıştır butonu
run_button = tk.Button(scrollable_frame, text="Çalıştır", command=run_solver)
run_button.grid(row=5, column=0, columnspan=2)

# Sonuç alanı
result_text = tk.Text(scrollable_frame, height=20, width=50)
result_text.grid(row=6, column=0, columnspan=2)

# "Her Şeyi Temizle" butonu
clear_button = tk.Button(scrollable_frame, text="Clear", command=clear_all)
clear_button.grid(row=6, column=0, columnspan=2)

# Tkinter döngüsü başlamadan önce butonları yerleştir
reposition_buttons()

# Tkinter döngüsü
root.mainloop()