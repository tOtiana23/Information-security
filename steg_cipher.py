import docx

def analyze_docx_by_size(file_path):
    """
    Извлекаем скрытые биты по размеру шрифта
    Находим все размеры
    Берём два наиболее распространённых
    Меньший - 0, больший - 1
    """

    doc = docx.Document(file_path)

    size_stats = {}
    runs_info = []

    # Собираем статистику размеров
    for p in doc.paragraphs:
        for run in p.runs:
            text = run.text
            if not text:
                continue

            fs = run.font.size
            size_pt = round(fs.pt, 1) if fs else None

            size_stats[size_pt] = size_stats.get(size_pt, 0) + len(text)
            runs_info.append((text, size_pt))

    print("Статистика размеров:", size_stats)

    if len(size_stats) < 2:
        print("Недостаточно разных размеров для декодирования.")
        return []

    # Берём 2 самых частых размера
    sizes_sorted = sorted(size_stats.items(), key=lambda x: x[1], reverse=True)
    size1, size2 = sizes_sorted[0][0], sizes_sorted[1][0]

    if size1 < size2:
        mapping = {size1: "0", size2: "1"}
    else:
        mapping = {size1: "1", size2: "0"}

    print("Сопоставление:", mapping)

    # Генерируем битовую последовательность
    binary_seq = []
    for text, sz in runs_info:
        bit = mapping.get(sz, None)
        if bit is None:
            continue
        for ch in text:
            if ch != '\n':
                binary_seq.append(bit)

    return binary_seq


def binary_to_bytes(binary_seq):
    """
    Конвертация списка битов в байты
    """
    b = ''.join(binary_seq)
    
    if len(b) % 8 != 0:
        b = b[:len(b) - (len(b) % 8)]

    data = bytearray()
    for i in range(0, len(b), 8):
        data.append(int(b[i:i+8], 2))
    return data


def try_encodings(data):
    encodings = [
        'utf-8', 'utf-16', 'utf-16-le', 'utf-16-be',
        'windows-1251', 'koi8-r', 'koi8-u', 'iso-8859-5'
    ]
    out = {}
    for enc in encodings:
        try:
            out[enc] = data.decode(enc, errors='ignore')
        except:
            out[enc] = "<decode error>"
    return out


def main():
    file_path = "test_04.docx"

    print("Извлекаем биты...")
    bits = analyze_docx_by_size(file_path)
    print("Бинарная строка:", ''.join(bits)[:100], "...")

    print("\nКонвертируем в байты...")
    data = binary_to_bytes(bits)
    print("Байт:", data)

    print("\nПробуем кодировки:")
    results = try_encodings(data)
    for enc, text in results.items():
        print(f"\n[{enc}]")
        print(text)


if __name__ == "__main__":
    main()
