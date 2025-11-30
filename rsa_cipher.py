import secrets
import math

def is_probable_prime(n: int, k: int = 40) -> bool:
    """Miller-Rabin проверка простоты. 
    k -- число раундов
    Возвращает True, если n с высокой вероятностью простое."""
    if n < 2:
        return False
    small_primes = [2,3,5,7,11,13,17,19,23,29]
    for p in small_primes:
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(k):
        a = secrets.randbelow(n - 3) + 2
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        composite = True
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                composite = False
                break
        if composite:
            return False
    return True

def generate_prime(bits: int) -> int:
    """Сгенерировать простое число заданной битности.
    Устанавливаем старший бит, чтобы число имело нужную битовую длину,
    и делаем его нечетным."""
    assert bits >= 2
    while True:
        p = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if is_probable_prime(p):
            return p

def egcd(a: int, b: int):
    """
    Расширенный алгоритм Евклида.
    Возвращает тройку (g, x, y) такую, что a*x + b*y = g = gcd(a, b).
    Нужен для вычисления обратного по модулю.
    """
    if b == 0:
        return (a, 1, 0)
    else:
        g, x1, y1 = egcd(b, a % b)
        x = y1
        y = x1 - (a // b) * y1
        return (g, x, y)

def modinv(a: int, m: int) -> int:
    """Модульная обратная: a^{-1} mod m. Бросает ValueError, если обратного нет."""
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError("Обратного не существует, gcd != 1")
    return x % m

def choose_random_coprime(phi: int, bits: int = None) -> int:
    """
    Выбирает случайное e, взаимно простое с phi.
    Если bits задан — пытаемся сгенерировать e нужной битности (< phi),
    иначе пробуем случайные числа в диапазоне.
    """
    if bits is None:
        # простой метод: пробуем случайные числа от 3 до phi-1
        while True:
            e = secrets.randbelow(phi - 3) + 3
            if math.gcd(e, phi) == 1:
                return e
    else:
        # генерируем числа нужной битности и проверяем < phi
        while True:
            e = secrets.randbits(bits) | 1  # нечётное
            if 2 <= e < phi and math.gcd(e, phi) == 1:
                return e

def generate_keypair(prime_bits: int = 2048, use_random_e: bool = False, e_bits: int = None):
    """
    Генерирует ключи RSA.
    prime_bits -- битность каждого простого p и q (по умолчанию 2048 -> p,q > 2^2047).
    use_random_e -- если True, выбираем случайный e взаимно-простой с phi; иначе используем рекомендованное 65537.
    e_bits -- при use_random_e можно задать битность e (опционально).
    Возвращает dict с p,q,n,phi,e,d.
    """
    if prime_bits < 16:
        raise ValueError("prime_bits слишком мало для RSA")
    print("Генерация p...")
    p = generate_prime(prime_bits)
    print("Генерация q...")
    q = generate_prime(prime_bits)
    while q == p:
        q = generate_prime(prime_bits)
    n = p * q
    phi = (p - 1) * (q - 1)
    if use_random_e:
        e = choose_random_coprime(phi, bits=e_bits)
    else:
        e = 65537
        if math.gcd(e, phi) != 1:
            # на редкость: попробуем выбрать другое e
            e = choose_random_coprime(phi, bits=e_bits)
    d = modinv(e, phi)
    return {"p": p, "q": q, "n": n, "phi": phi, "e": e, "d": d}

def encrypt_int(m: int, e: int, n: int) -> int:
    """Шифрование целого m: c = m^e mod n. Требуется 0 < m < n."""
    if not (0 < m < n):
        raise ValueError("m должно быть в диапазоне 1..n-1")
    return pow(m, e, n)

def decrypt_int(c: int, d: int, n: int) -> int:
    """Расшифровка целого c: m = c^d mod n."""
    return pow(c, d, n)

def bytes_to_int(b: bytes) -> int:
    return int.from_bytes(b, byteorder="big")

def int_to_bytes(i: int) -> bytes:
    # вычислим необходимую длину
    length = (i.bit_length() + 7) // 8
    return i.to_bytes(length, byteorder="big")

def encrypt_message(message: str, e: int, n: int) -> int:
    """Шифрует текстовую строку (UTF-8) как одно целое.
       Убедись, что int(message) < n."""
    m = bytes_to_int(message.encode("utf-8"))
    if m >= n:
        raise ValueError("Сообщение слишком длинное для данного n — нужно разбивать на блоки")
    return encrypt_int(m, e, n)

def decrypt_message(cipher_int: int, d: int, n: int) -> str:
    """Расшифровываем целое и обратно в строку UTF-8."""
    m = decrypt_int(cipher_int, d, n)
    return int_to_bytes(m).decode("utf-8")

if __name__ == "__main__":
    bits = 1024
    print(f"Генерация ключей с prime_bits = {bits}")
    keys = generate_keypair(prime_bits=bits, use_random_e=False)
    n, e, d = keys["n"], keys["e"], keys["d"]
    print("Ключи сгенерированы.")
    print("n битность:", n.bit_length(), "e:", e)
    text = "Привет, RSA!"
    c = encrypt_message(text, e, n)
    print("Шифротекст (int):", c)
    m0 = decrypt_message(c, d, n)
    print("Расшифровка:", m0)
