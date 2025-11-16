#!/usr/bin/env python3
"""
Hamming code simulator for teaching / lab tasks.

Features:
- choose minimal Hamming code (n,m) given alphabet size
- map alphabet -> fixed-length binary words
- encode each symbol into Hamming codeword (systematic, parity bits at positions 1,2,4,8,...)
- flip a bit in any codeword (by index or randomly)
- detect and correct single-bit errors, report positions
- decode corrected codewords back to message
"""

from typing import List, Tuple, Dict, Optional
import math
import secrets


# ---------- Utility functions ----------

def ceil_log2(x: int) -> int:
    """Minimal number of bits to represent x distinct values (ceil(log2(x)))."""
    if x <= 1:
        return 1
    return math.ceil(math.log2(x))


def choose_hamming_code_for_m(m_required: int) -> Tuple[int, int, int]:
    """
    Choose minimal k such that 2^k - 1 has m >= m_required informational bits.
    Returns (k, n, m) where n = 2^k - 1, m = n - k.
    """
    k = 1
    while True:
        n = (1 << k) - 1
        m = n - k
        if m >= m_required:
            return k, n, m
        k += 1


def is_power_of_two(x: int) -> bool:
    return x != 0 and (x & (x - 1)) == 0


# ---------- Hamming core: encode / decode ----------

def make_empty_codeword(n: int) -> List[int]:
    """
    Return list of length n+1 (1-based indexing, index 0 unused) with zeros.
    We will use indices 1..n.
    """
    return [0] * (n + 1)


def place_data_bits_into_codeword(data_bits: List[int], n: int) -> List[int]:
    """
    Place data bits (list of 0/1) into positions that are NOT powers of two.
    data_bits should be length m (<= available positions). We fill in increasing index order:
    the first bit in data_bits goes to the lowest-numbered data position.
    Returns codeword list (1-based).
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
    Compute parity bits in-place for code (1-based list).
    Parity bit at position p = 2^(j) controls positions i where (i & p) != 0.
    We set parity such that total parity (including parity bit itself) is even.
    """
    n = len(code) - 1
    for j in range(k):
        p = 1 << j  # parity position
        s = 0
        i = p
        # iterate positions controlled by p: start at p, take p bits, skip p bits, ...
        while i <= n:
            # sum block of length p
            for q in range(i, min(i + p, n + 1)):
                if q != p:
                    s ^= code[q]  # xor for parity (mod 2)
            i += 2 * p
        code[p] = s  # set parity so that overall parity is s ^ code[p] == 0 -> code[p] = s


def encode_data_bits_to_codeword(data_bits: List[int], k: int) -> List[int]:
    """Given data bits and number of parity bits k, produce full Hamming codeword (1-based list)."""
    n = (1 << k) - 1
    code = place_data_bits_into_codeword(data_bits, n)
    compute_parity_bits(code, k)
    return code


def syndrome_of_codeword(code: List[int], k: int) -> int:
    """
    Compute syndrome (integer) for the received codeword.
    syndrome = sum( j-th parity mismatch ? 2^(j) : 0 )
    If syndrome == 0 -> no errors detected.
    If syndrome != 0 -> that is the 1-based index of incorrect bit.
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
    return syn  # 0..n


def correct_codeword(code: List[int], k: int) -> Tuple[List[int], Optional[int]]:
    """
    Compute syndrome and correct single-bit error if present.
    Returns (corrected_code, error_position or None).
    Mutates a shallow copy and returns it (original not changed).
    """
    code_copy = code[:]  # copy
    syn = syndrome_of_codeword(code_copy, k)
    if syn == 0:
        return code_copy, None
    n = len(code_copy) - 1
    if 1 <= syn <= n:
        # flip that bit
        code_copy[syn] ^= 1
        return code_copy, syn
    else:
        # syndrome out of range -> cannot correct
        return code_copy, syn


def extract_data_bits_from_codeword(code: List[int], k: int) -> List[int]:
    """Return list of data bits (in the same order they were placed)."""
    n = len(code) - 1
    data = []
    for i in range(1, n + 1):
        if not is_power_of_two(i):
            data.append(code[i])
    return data


# ---------- Alphabet mapping ----------

def build_alphabet_mapping(alphabet: List[str]) -> Dict[str, int]:
    """
    Map each symbol in alphabet to integer index 0..len(alphabet)-1.
    """
    return {ch: idx for idx, ch in enumerate(alphabet)}


def int_to_bits(x: int, length: int) -> List[int]:
    """Convert integer x to list of bits length 'length' (MSB first)."""
    bits = [(x >> (length - 1 - i)) & 1 for i in range(length)]
    return bits


def bits_to_int(bits: List[int]) -> int:
    """Convert list of bits (MSB first) to integer."""
    x = 0
    for b in bits:
        x = (x << 1) | (b & 1)
    return x


# ---------- High-level functions: encode message, corrupt, decode ----------

def encode_message_with_hamming(message: str, alphabet: List[str]) -> Tuple[List[List[int]], Dict]:
    """
    Encode a text message (string of symbols from alphabet) into list of Hamming codewords (1-based lists).
    Returns (list_of_codewords, info) where info contains mapping and parameters.
    """
    mapping = build_alphabet_mapping(alphabet)
    alph_size = len(alphabet)
    symbol_bits = ceil_log2(alph_size)  # m_required
    k, n, m = choose_hamming_code_for_m(symbol_bits)
    # we will use exactly m bits for data (m >= symbol_bits). When decoding, the top unused data bits should be zeros.
    codewords = []
    for ch in message:
        if ch not in mapping:
            raise ValueError(f"Symbol '{ch}' not in alphabet")
        val = mapping[ch]
        data_bits_full = int_to_bits(val, m)  # MSB first
        cw = encode_data_bits_to_codeword(data_bits_full, k)
        codewords.append(cw)
    info = {"alphabet": alphabet, "mapping": mapping, "symbol_bits": symbol_bits, "k": k, "n": n, "m": m}
    return codewords, info


def flip_bit_in_codeword(codeword: List[int], position: int) -> None:
    """Flip bit at 1-based position in codeword (mutates the list)."""
    if position < 1 or position >= len(codeword):
        raise IndexError("position out of range")
    codeword[position] ^= 1


def flip_random_bit_in_codeword(codeword: List[int]) -> int:
    """Flip a random bit in codeword, return position flipped."""
    n = len(codeword) - 1
    pos = secrets.randbelow(n) + 1
    flip_bit_in_codeword(codeword, pos)
    return pos


def decode_codewords(codewords: List[List[int]], info: Dict) -> Tuple[str, List[Dict]]:
    """
    Decode list of received codewords. For each word:
      - compute syndrome, correct single error if present
      - extract data bits, convert to integer, then to symbol from alphabet
    Returns (decoded_message_str, report_list)
    report_list contains dicts with keys: index (0-based), corrected (bool), error_position (int or None),
    original_codeword, corrected_codeword, data_bits, symbol_index, symbol_char
    """
    alphabet = info["alphabet"]
    k = info["k"]
    m = info["m"]
    mapping = info["mapping"]
    reverse_map = {v: ch for ch, v in mapping.items()}
    out_chars = []
    reports = []
    for idx, rec in enumerate(codewords):
        # ensure we have a copy
        rec_copy = rec[:]
        corrected, error_pos = correct_codeword(rec_copy, k)
        data_bits = extract_data_bits_from_codeword(corrected, k)
        symbol_val = bits_to_int(data_bits)
        # if symbol_val >= len(alphabet) -> possibly decoding error (symbol out of alphabet range)
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


# ---------- Example / CLI-like demo ----------

def demo():
    # Пример: русская кириллица без учёта регистра (примерный алфавит 33 символа)
    rus_alphabet = list("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
    # Можно заменить на любой другой список символов, например:
    # rus_alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ ")
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

    # Портим некоторые последовательности: вручную или случайно
    # Пример: испортим 1-й символ в позиции 3 и случайно 3-й символ
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

if __name__ == "__main__":
    demo()
