import random
from typing import List, Tuple

def char_to_16bit(ch: str) -> str:
    """
    Возвращает 16-битную строку '0'/'1' — двоичное представление кода символа ch.
    """
    code = ord(ch)
    return format(code, '016b')

def string_to_bits_two_chars(s: str) -> str:
    """
    Для строки из 2 символов возвращает 32-битную строку (16 бит на символ).
    Если строка короче — дополняет нулём; если длиннее — берёт первые 2 символа.
    """
    s = (s + '\x00\x00')[:2]
    return char_to_16bit(s[0]) + char_to_16bit(s[1])

def bits32_to_two_chars(bits32: str) -> str:
    """
    Для 32-битной строки возвращает строку из 2 символов, соответствующих 16-битным блокам.
    """
    a = bits32[:16]
    b = bits32[16:]
    return chr(int(a, 2)) + chr(int(b, 2))

def random_permutation_by_swaps(base: List[int], swaps: int = 64, rng: random.Random = None) -> List[int]:
    """
    Возвращает перестановку списка base, полученную путём случайных пару-обменов (swaps раз).
    """
    rng = rng or random
    perm = base.copy()
    n = len(perm)
    for _ in range(swaps):
        i = rng.randrange(n)
        j = rng.randrange(n)
        perm[i], perm[j] = perm[j], perm[i]
    return perm

def generate_permutations_list(base: List[int], count: int, swaps: int = 64, seed: int = None) -> List[List[int]]:
    """
    Возвращает список (count элементов) различных перестановок списка base.
    Гарантирует, что каждая перестановка отличается от оригинального base.
    """
    rng = random.Random(seed)
    perms = []
    attempts = 0
    while len(perms) < count and attempts < count * 10:
        p = random_permutation_by_swaps(base, swaps=swaps, rng=rng)
        if p != base and p not in perms:
            perms.append(p)
        attempts += 1
    if len(perms) < count:
        raise RuntimeError("Не удалось сгенерировать требуемое количество уникальных перестановок")
    return perms

def p_block_encrypt(bits32: str, p_perm: List[int]) -> str:
    """
    Шифрующий P-блок: на позицию i ставит бит из позиции p_perm[i].
    bits32 — строка длины 32, p_perm — перестановка индексов 0..31.
    """
    if len(bits32) != 32:
        raise ValueError("Ожидается 32-битная строка")
    return ''.join(bits32[p_perm[i]] for i in range(32))

def p_block_decrypt(bits32: str, p_perm: List[int]) -> str:
    """
    Расшифровывающий P-блок: восстанавливает оригинал по той же p_perm (находит обратную перестановку).
    """
    if len(bits32) != 32:
        raise ValueError("Ожидается 32-битная строка")
    inv = [0] * 32
    for i, src in enumerate(p_perm):
        inv[src] = i
    return ''.join(bits32[inv[i]] for i in range(32))

def bin4_to_dec(s: str) -> int:
    """
    Преобразует 4-битную строку в десятичное число 0..15.
    """
    return int(s, 2)

def dec_to_bin4(x: int) -> str:
    """
    Преобразует число 0..15 в 4-битную двоичную строку.
    """
    if not (0 <= x <= 15):
        raise ValueError("Ожидается число 0..15")
    return format(x, '04b')

def s_block_encrypt(nibble4: str, s_perm: List[int]) -> str:
    """
    Шифрующий S-блок: вход — 4-битная строка, s_perm — перестановка 0..15.
    Возвращает 4-битную зашифрованную строку.
    """
    v = bin4_to_dec(nibble4)
    out = s_perm[v]
    return dec_to_bin4(out)

def s_block_decrypt(nibble4: str, s_perm: List[int]) -> str:
    """
    Расшифровывающий S-блок: применяет обратное отображение перестановки s_perm.
    """
    v = bin4_to_dec(nibble4)
    inv = [0] * 16
    for i, val in enumerate(s_perm):
        inv[val] = i
    out = inv[v]
    return dec_to_bin4(out)

def s_battery_encrypt(bits32: str, s_perm: List[int]) -> str:
    """
    Батарея из 8 S-блоков: разбивает 32-битную строку на 8 частей по 4 бита и применяет s_block_encrypt ко всем.
    """
    if len(bits32) != 32:
        raise ValueError("Ожидается 32-битная строка")
    parts = [bits32[i*4:(i+1)*4] for i in range(8)]
    out_parts = [s_block_encrypt(p, s_perm) for p in parts]
    return ''.join(out_parts)

def s_battery_decrypt(bits32: str, s_perm: List[int]) -> str:
    """
    Обратная батарея S-блоков.
    """
    if len(bits32) != 32:
        raise ValueError("Ожидается 32-битная строка")
    parts = [bits32[i*4:(i+1)*4] for i in range(8)]
    out_parts = [s_block_decrypt(p, s_perm) for p in parts]
    return ''.join(out_parts)

def encrypt_two_chars(plain2: str,
                      p_perms: List[List[int]],
                      s_perms: List[List[int]],
                      p_index: int,
                      s_index: int) -> Tuple[str, dict]:
    """
    Шифрование двухсимвольной строки plain2 с использованием:
    - списка перестановок для P-блока p_perms (берём по индексу p_index)
    - списка перестановок для S-блока s_perms (берём по индексу s_index)
    Возвращает зашифрованную двухсимвольную строку и словарь с промежуточными битовыми формами.
    """
    bits = string_to_bits_two_chars(plain2)
    p_perm = p_perms[p_index]
    s_perm = s_perms[s_index]
    after_p1 = p_block_encrypt(bits, p_perm)
    after_s = s_battery_encrypt(after_p1, s_perm)
    after_p2 = p_block_encrypt(after_s, p_perm)
    cipher = bits32_to_two_chars(after_p2)
    return cipher, {
        'bits_plain': bits,
        'after_p1': after_p1,
        'after_s': after_s,
        'after_p2': after_p2
    }

def decrypt_two_chars(cipher2: str,
                      p_perms: List[List[int]],
                      s_perms: List[List[int]],
                      p_index: int,
                      s_index: int) -> Tuple[str, dict]:
    """
    Расшифрование двухсимвольной строки cipher2 (обратный порядок операций).
    Возвращает восстановленную исходную строку и словарь с промежуточными битовыми формами.
    """
    bits = string_to_bits_two_chars(cipher2)
    p_perm = p_perms[p_index]
    s_perm = s_perms[s_index]
    after_p1 = p_block_decrypt(bits, p_perm)
    after_s = s_battery_decrypt(after_p1, s_perm)
    after_p2 = p_block_decrypt(after_s, p_perm)
    plain = bits32_to_two_chars(after_p2)
    return plain, {
        'bits_cipher': bits,
        'after_p1_decrypt': after_p1,
        'after_s_decrypt': after_s,
        'after_p2_decrypt': after_p2
    }

if __name__ == "__main__":
    SEED = 12345
    p_base = list(range(32))
    s_base = list(range(16))
    p_perms = generate_permutations_list(p_base, count=12, swaps=128, seed=SEED)
    s_perms = generate_permutations_list(s_base, count=12, swaps=64, seed=SEED+1)
    p_idx = 3
    s_idx = 5
    plain = "ИД"
    cipher, enc_steps = encrypt_two_chars(plain, p_perms, s_perms, p_idx, s_idx)
    print("Исходное сообщение:", plain)
    print("Битовая форма исходного сообщения:", enc_steps['bits_plain'])
    print("Зашифрованная p-блоком битовая форма:", enc_steps['after_p1'])
    print("Зашифрованная батареей s-блоков битовая форма:", enc_steps['after_s'])
    print("Зашифрованная p-блоком битовая форма:", enc_steps['after_p2'])
    print("Зашифрованное сообщение:", cipher)
    recovered, dec_steps = decrypt_two_chars(cipher, p_perms, s_perms, p_idx, s_idx)
    print("Расшифрованное сообщение:", recovered)
    print("Расшифрованная p-блоком битовая форма:", dec_steps['after_p1_decrypt'])
    print("Расшифрованная батареей s-блоков битовая форма:", dec_steps['after_s_decrypt'])
    print("Расшифрованная p-блоком битовая форма:", dec_steps['after_p2_decrypt'])
