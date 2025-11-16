import random
from typing import List

def generate_key_by_swaps(seed: int | None = None, swaps: int = 1024) -> List[int]:
    """
    Генерирует перестановку 0..255 как ключ (KEY).
    Если указан seed — генерация воспроизводима.
    swaps — количество случайных попарных обменов для перестановки.
    """
    rng = random.Random(seed)
    key = list(range(256))
    n = 256
    for _ in range(swaps):
        i = rng.randrange(n)
        j = rng.randrange(n)
        key[i], key[j] = key[j], key[i]
    return key

def ksa_initialize_gen(key: List[int]) -> List[int]:
    """
    Инициализация генератора GEN по правилу:
    GEN := random key (копия key), затем
    j := 0; for i in 0..255: j := (j + GEN[i] + KEY[i]) mod 256; swap GEN[i], GEN[j]
    Возвращает модифицированный GEN (список 0..255 в переставленном порядке).
    """
    if len(key) != 256:
        raise ValueError("KEY длины 256 ожидается")
    gen = key.copy()
    j = 0
    for i in range(256):
        j = (j + gen[i] + key[i]) & 0xFF
        gen[i], gen[j] = gen[j], gen[i]
    return gen

def prga_generate_gamma(gen_init: List[int], length: int) -> bytes:
    """
    Вырабатывает гамму (GAMMA) длины length байт.
    gen_init — состояние GEN после KSA. PRGA: i := 0; j := 0; затем на каждом шаге:
    i := (i + 1) mod 256; j := (j + GEN[i]) mod 256; swap GEN[i], GEN[j];
    t := (GEN[i] + GEN[j]) mod 256; output := GEN[t]
    Возвращает GAMMA как bytes length.
    """
    gen = gen_init.copy()
    i = 0
    j = 0
    out = bytearray()
    for _ in range(length):
        i = (i + 1) & 0xFF
        j = (j + gen[i]) & 0xFF
        gen[i], gen[j] = gen[j], gen[i]
        t = (gen[i] + gen[j]) & 0xFF
        out.append(gen[t])
    return bytes(out)

def xor_bytes(data: bytes, gamma: bytes) -> bytes:
    """
    Выполняет побайтовое XOR между двумя байтовыми последовательностями одинаковой длины.
    """
    if len(data) != len(gamma):
        raise ValueError("data и gamma должны быть одной длины")
    return bytes(a ^ b for a, b in zip(data, gamma))

def encrypt_bytes(message: bytes, key: List[int]) -> bytes:
    """
    Шифрует байтовую последовательность message, используя Key (перестановка 0..255).
    Возвращает зашифрованные байты.
    """
    gen = ksa_initialize_gen(key)
    gamma = prga_generate_gamma(gen, len(message))
    return xor_bytes(message, gamma)

def decrypt_bytes(cipher: bytes, key: List[int]) -> bytes:
    """
    Расшифровывает байтовую последовательность (XOR с той же гаммой восстанавливает исход).
    """
    return encrypt_bytes(cipher, key)

def encrypt_text_unicode16be(plaintext: str, key: List[int]) -> bytes:
    """
    Шифрует строку plaintext. Перед шифрованием строка кодируется в 'utf-16-be'
    (каждый символ как 2 байта в большинстве случаев, BMP), затем выполняется шифрование.
    Возвращает зашифрованные байты.
    """
    data = plaintext.encode('utf-16-be')
    return encrypt_bytes(data, key)

def decrypt_text_unicode16be(cipher_bytes: bytes, key: List[int]) -> str:
    """
    Расшифровывает байты, полученные функцией encrypt_text_unicode16be,
    и декодирует обратно в строку 'utf-16-be'.
    """
    data = decrypt_bytes(cipher_bytes, key)
    return data.decode('utf-16-be')

if __name__ == "__main__":
    SEED = 12345
    key = generate_key_by_swaps(seed=SEED, swaps=4096)
    msg_bytes = b"Hello, world!"
    cipher_bytes = encrypt_bytes(msg_bytes, key)
    recovered_bytes = decrypt_bytes(cipher_bytes, key)
    print("Исходные байты:", msg_bytes)
    print("Зашифрованные (hex):", cipher_bytes.hex())
    print("Восстановлено:", recovered_bytes)
    plain_text = "Привет, мир"
    cipher_for_text = encrypt_text_unicode16be(plain_text, key)
    recovered_text = decrypt_text_unicode16be(cipher_for_text, key)
    print("Исходный текст:", plain_text)
    print("Зашифрованный (hex):", cipher_for_text.hex())
    print("Восстановленный текст:", recovered_text)
