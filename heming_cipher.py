from typing import List, Tuple, Dict, Optional
import math
import secrets

def ceil_log2(x: int) -> int:
    """Минимальное число бит для представления x значений (ceil(log2))"""
    if x <= 1:
        return 1
    return math.ceil(math.log2(x))


def choose_hamming_code_for_m(m_required: int) -> Tuple[int, int, int]:
    """
    Выбирает минимальное k такое, что n=2^k-1, m=n-k >= m_required
    Возвращает (k, n, m).
    """
    k = 1
    while True:
        n = (1 << k) - 1
        m = n - k
        if m >= m_required:
            return k, n, m
        k += 1


def is_power_of_two(x: int) -> bool:
    """Проверка, является ли число степенью двойки"""
    return x != 0 and (x & (x - 1)) == 0


def make_empty_codeword(n: int) -> List[int]:
    """Пустое кодовое слово длины n (1-based, индекс 0 не используется)"""
    return [0] * (n + 1)


def place_data_bits_into_codeword(data_bits: List[int], n: int) -> List[int]:
    """
    Вставляет информационные биты в позиции, которые не являются степенью двойки
    Возвращает кодовое слово (1-based).
    """
    code = make_empty_codeword(n)
    data_pos = 0
    for i in range(1, n + 1):
        if not is_power_of_two(i):
            if data_pos < len(data_bits):
                code[i] = data_bits[data_pos]
            else:
                code[i] = 0
            data_pos += 1
    return code


def compute_parity_bits(code: List[int], k: int) -> None:
    """
    Вычисляет контрольные биты (чётность) и записывает их в код (in-place)
    Каждый бит p=2^j контролирует блоки по p бит
    """
    n = len(code) - 1
    for j in range(k):
        p = 1 << j  # позиция контрольного бита
        s = 0
        i = p
        # цикл: берём p бит, пропускаем p бит и т.д.
        while i <= n:
            for q in range(i, min(i + p, n + 1)):
                if q != p:
                    s ^= code[q]  # XOR — сумма по mod2
            i += 2 * p
        code[p] = s


def encode_data_bits_to_codeword(data_bits: List[int], k: int) -> List[int]:
    """Формирует полное кодовое слово Хэмминга по data_bits и k контрольным битам"""
    n = (1 << k) - 1
    code = place_data_bits_into_codeword(data_bits, n)
    compute_parity_bits(code, k)
    return code


def syndrome_of_codeword(code: List[int], k: int) -> int:
    """
    Вычисляет синдром (число). 0 — ошибок нет, иначе — позиция ошибочного бита.
    Возвращает целое от 0 до n.
    """
    n = len(code) - 1
    syn = 0
    for j in range(k):
        p = 1 << j
        s = 0
        i = p
        while i <= n:
            for q in range(i, min(i + p, n + 1)):
                s ^= code[q]
            i += 2 * p
        if s != 0:
            syn |= p
    return syn


def correct_codeword(code: List[int], k: int) -> Tuple[List[int], Optional[int]]:
    """
    Вычисляет синдром и, если синдром != 0 и в диапазоне, исправляет один бит.
    Возвращает (исправленное_слово, позиция_ошибки или None).
    """
    code_copy = code[:]  # копия, чтобы не менять исходник
    syn = syndrome_of_codeword(code_copy, k)
    if syn == 0:
        return code_copy, None
    n = len(code_copy) - 1
    if 1 <= syn <= n:
        code_copy[syn] ^= 1  # инвертируем бит
        return code_copy, syn
    else:
        return code_copy, syn


def extract_data_bits_from_codeword(code: List[int], k: int) -> List[int]:
    """Извлекает информационные биты из кодового слова (в исходном порядке)"""
    n = len(code) - 1
    data = []
    for i in range(1, n + 1):
        if not is_power_of_two(i):
            data.append(code[i])
    return data


def build_alphabet_mapping(alphabet: List[str]) -> Dict[str, int]:
    """Строит отображение символ -> индекс (0..len-1)"""
    return {ch: idx for idx, ch in enumerate(alphabet)}


def int_to_bits(x: int, length: int) -> List[int]:
    """Преобразует целое x в список бит длины length (MSB первым)"""
    bits = [(x >> (length - 1 - i)) & 1 for i in range(length)]
    return bits


def bits_to_int(bits: List[int]) -> int:
    """Преобразует список бит (MSB первым) в целое"""
    x = 0
    for b in bits:
        x = (x << 1) | (b & 1)
    return x


def encode_message_with_hamming(message: str, alphabet: List[str]) -> Tuple[List[List[int]], Dict]:
    """
    Кодирует строку посимвольно в список кодовых слов Хэмминга.
    Возвращает (codewords, info) с параметрами и отображением
    """
    mapping = build_alphabet_mapping(alphabet)
    alph_size = len(alphabet)
    symbol_bits = ceil_log2(alph_size)  # сколько бит нужно для одного символа
    k, n, m = choose_hamming_code_for_m(symbol_bits)
    codewords = []
    for ch in message:
        if ch not in mapping:
            raise ValueError(f"Symbol '{ch}' not in alphabet")
        val = mapping[ch]
        data_bits_full = int_to_bits(val, m)
        cw = encode_data_bits_to_codeword(data_bits_full, k)
        codewords.append(cw)
    info = {"alphabet": alphabet, "mapping": mapping, "symbol_bits": symbol_bits, "k": k, "n": n, "m": m}
    return codewords, info


def flip_bit_in_codeword(codeword: List[int], position: int) -> None:
    """Инвертирует бит в кодовом слове по 1-based позиции (меняет список)."""
    if position < 1 or position >= len(codeword):
        raise IndexError("position out of range")
    codeword[position] ^= 1


def flip_random_bit_in_codeword(codeword: List[int]) -> int:
    """Инвертирует случайный бит в кодовом слове, возвращает позицию."""
    n = len(codeword) - 1
    pos = secrets.randbelow(n) + 1
    flip_bit_in_codeword(codeword, pos)
    return pos


def decode_codewords(codewords: List[List[int]], info: Dict) -> Tuple[str, List[Dict]]:
    """
    Декодирует список кодовых слов:
    - исправляет одиночные ошибки,
    - извлекает данные и восстанавливает символы.
    Возвращает (строка, отчёт по каждому слову).
    """
    alphabet = info["alphabet"]
    k = info["k"]
    m = info["m"]
    mapping = info["mapping"]
    reverse_map = {v: ch for ch, v in mapping.items()}
    out_chars = []
    reports = []
    for idx, rec in enumerate(codewords):
        rec_copy = rec[:]
        corrected, error_pos = correct_codeword(rec_copy, k)
        data_bits = extract_data_bits_from_codeword(corrected, k)
        symbol_val = bits_to_int(data_bits)
        symbol_char = reverse_map.get(symbol_val, None)
        out_chars.append(symbol_char if symbol_char is not None else "?")
        reports.append({
            "index": idx,
            "corrected": error_pos is not None,
            "error_position": error_pos,
            "received_codeword": rec,
            "corrected_codeword": corrected,
            "data_bits": data_bits,
            "symbol_index": symbol_val,
            "symbol_char": symbol_char
        })
    return "".join(out_chars), reports

if __name__ == "__main__":
    rus_alphabet = list("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
    alphabet = rus_alphabet
    message = "привет"
    print("Алфавит:", "".join(alphabet))
    print("Сообщение:", message)

    codewords, info = encode_message_with_hamming(message, alphabet)
    k, n, m = info["k"], info["n"], info["m"]
    print(f"Выбрали код Хэмминга: k={k}, n={n}, m={m} (m >= требуемых {info['symbol_bits']})")
    print("Закодированные последовательности (по одной строке на символ, 1-based indices):")
    for i, cw in enumerate(codewords):
        print(f"{i}: ", "".join(str(b) for b in cw[1:]))

    # Портим некоторые последовательности
    print("\nИскажаем (инвертируем) биты:")
    print(" - инвертируем бит 3 в первом кодовом слове")
    flip_bit_in_codeword(codewords[0], 3)
    pos_rand = flip_random_bit_in_codeword(codewords[-1])
    print(f" - случайно инвертировали позицию {pos_rand} в последнем кодовом слове")

    # Показать искажённые кодовые слова
    print("\nИскажённые кодовые слова:")
    for i, cw in enumerate(codewords):
        print(f"{i}: ", "".join(str(b) for b in cw[1:]))

    # Декодируем и исправляем
    decoded_message, reports = decode_codewords(codewords, info)
    print("\nРезультат декодирования после исправления:")
    print("Раскодированное сообщение:", decoded_message)
    print("\nОтчёт по каждому кодовому слову:")
    for r in reports:
        print(f"Индекс {r['index']}: исправлено={r['corrected']}, error_pos={r['error_position']}, "
              f"symbol_index={r['symbol_index']}, symbol_char={r['symbol_char']}")
