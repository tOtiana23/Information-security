from typing import List, Optional, Tuple

class ModArithmetic:
    def __init__(self, mod):
        if mod <= 0:
            raise ValueError("Модуль должен быть положительным числом")
        self.mod = mod

    @staticmethod
    def gcd(a: int, b: int) -> int:
        """Наибольший общий делитель алгоритмом Евклида"""
        a, b = abs(a), abs(b)
        while b:
            a, b = b, a%b
        return a
    
    @staticmethod
    def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
        """
        Расширенный алгоритм Евклида.
        Возвращает (gcd, x, y) такие, что a*x + b*y = g = gcd(a,b).
        """
        if b == 0:
            return a, 1, 0
        else:
            gcd, x1, y1 = ModArithmetic.extended_gcd(b, a % b)
            x = y1
            y = x1 - (a // b) * y1
            return gcd, x, y
        
    def modinv(self, a: int) -> Optional[int]:
        """
        Обратный элемент a^{-1} по модулю m, если он существует.
        Возвращает None, если gcd(a, m) != 1.
        """
        g, x, _ = self.extended_gcd(a, self.mod)
        if g != 1:
            return None
        # x может быть отрицательным => нормализуем в [0, m-1]
        return x % self.mod
    
def build_maps(alphabet: str):
    """
    Возвращает два словаря: char->index и index->char.
    Предполагается, что alphabet содержит уникальные символы.
    """
    idx = {ch: i for i, ch in enumerate(alphabet)}
    inv = {i: ch for i, ch in enumerate(alphabet)}
    return idx, inv

def encrypt_affine(plain: str, a: int, b: int, alphabet: str) -> str:
    """
    Шифрование аффинным шифром: E(x) = (a*x + b) mod N
    Символы не из alphabet остаются без изменений.
    """
    N = len(alphabet)
    if N == 0:
        raise ValueError("Алфавит не может быть пустым.")
    ma = ModArithmetic(N)
    if ModArithmetic.gcd(a, N) != 1:
        raise ValueError(f"Параметр a={a} не взаимно-прост с N={N} (НОД != 1).")
    idx, inv = build_maps(alphabet)
    result = []
    for ch in plain:
        if ch in idx:
            x = idx[ch]
            y = (a * x + b) % N
            result.append(inv[y])
        else:
            result.append(ch)
    return ''.join(result)

def decrypt_affine(cipher: str, a: int, b: int, alphabet: str) -> str:
    """
    Дешифрование аффинным шифром: D(y) = a^{-1} * (y - b) mod N
    """
    N = len(alphabet)
    if N == 0:
        raise ValueError("Алфавит не может быть пустым.")
    ma = ModArithmetic(N)
    a_inv = ma.modinv(a)
    if a_inv is None:
        raise ValueError(f"Обратного элемента для a={a} по модулю N={N} не существует.")
    idx, inv = build_maps(alphabet)
    result = []
    for ch in cipher:
        if ch in idx:
            y = idx[ch]
            x = (a_inv * (y - b)) % N
            result.append(inv[x])
        else:
            result.append(ch)
    return ''.join(result)

def brute_force_affine(cipher: str, alphabet: str) -> List[Tuple[int, int, str]]:
    """
    Перебирает все допустимые пары (a, b) и возвращает список кортежей
    (a, b, candidate_plain). Допустимые a — те, у которых gcd(a, N) == 1.
    """
    N = len(alphabet)
    if N == 0:
        return []
    results = []
    # допустимые a: 0..N-1, но gcd(a,N) == 1
    for a in range(N):
        if ModArithmetic.gcd(a, N) != 1:
            continue
        for b in range(N):
            try:
                pt = decrypt_affine(cipher, a, b, alphabet)
                results.append((a, b, pt))
            except ValueError:
                continue
    return results

if __name__ == "__main__":
    alphabet = "ОИНТК_"
    print("Алфавит:", list(alphabet))
    plain = "НИТКИ_ТОНКИ"
    a = 5
    b = 2
    print("Исходная строка:", plain)
    cipher = encrypt_affine(plain, a, b, alphabet)
    print(f"Зашифрована (a={a}, b={b}):", cipher)

    # Расшифровка
    recovered = decrypt_affine(cipher, a, b, alphabet)
    print(f"Расшифрована (a={a}, b={b}):", recovered)

    # Атака перебором (N известен, a и b неизвестны)
    print("\nАтака полным перебором (все допустимые пары a,b):")
    candidates = brute_force_affine(cipher, alphabet)
    for a_c, b_c, cand in candidates:
        print(f" a={a_c:2d}, b={b_c:2d}  => {cand}")
