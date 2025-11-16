import numpy as np

alphabet = "ОИНТК_"
N = len(alphabet)
char_to_idx = {ch: i for i, ch in enumerate(alphabet)}
idx_to_char = {i: ch for i, ch in enumerate(alphabet)}

def text_to_numbers(text: str):
    """Преобразует текст в список индексов"""
    return [char_to_idx[ch] for ch in text if ch in char_to_idx]

def numbers_to_text(nums: list[int]):
    """Преобразует список индексов обратно в текст"""
    return ''.join(idx_to_char[n % N] for n in nums)

def mod_matrix_inverse(matrix: np.ndarray, mod: int):
    """Обратная матрица по модулю mod (через расширенный алгоритм Евклида)"""
    det = int(round(np.linalg.det(matrix)))  # определитель
    det %= mod
    # найти обратный к det
    def egcd(a, b):
        if b == 0: return (a, 1, 0)
        g, x1, y1 = egcd(b, a % b)
        return g, y1, x1 - (a // b) * y1
    g, x, _ = egcd(det, mod)
    if g != 1:
        raise ValueError("Матрица не обратима по модулю {}".format(mod))
    det_inv = x % mod
    # матрица алгебраических дополнений (союзная)
    adj = np.round(det * np.linalg.inv(matrix)).astype(int) % mod
    return (det_inv * adj) % mod

def hill_encrypt(text: str, A: np.ndarray) -> str:
    block_size = A.shape[0]
    nums = text_to_numbers(text)
    # дополняем пробелами "_" если не хватает
    while len(nums) % block_size != 0:
        nums.append(char_to_idx["_"])
    cipher_nums = []
    for i in range(0, len(nums), block_size):
        block = np.array(nums[i:i+block_size])
        enc = A.dot(block) % N
        cipher_nums.extend(enc)
    return numbers_to_text(cipher_nums)

def hill_decrypt(cipher: str, A: np.ndarray) -> str:
    A_inv = mod_matrix_inverse(A, N)
    block_size = A.shape[0]
    nums = text_to_numbers(cipher)
    plain_nums = []
    for i in range(0, len(nums), block_size):
        block = np.array(nums[i:i+block_size])
        dec = A_inv.dot(block) % N
        plain_nums.extend(dec)
    return numbers_to_text(plain_nums)

if __name__ == "__main__":
    plain = "НИТКИ_ТОНКИ"
    A = np.array([[1, 2],
                  [3, 5]])
    print("Алфавит:", list(alphabet))
    print("Исходный текст:", plain)

    cipher = hill_encrypt(plain, A)
    print("Зашифрованный:", cipher)

    recovered = hill_decrypt(cipher, A)
    print("Расшифрованный:", recovered)