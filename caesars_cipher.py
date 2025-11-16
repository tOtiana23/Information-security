def normalize_shift(shift: int, alphabet_length: int) -> int:
    """"
    Нормализует сдвиг shift для алфавита длины alphabet_length.
    """
    if alphabet_length == 0:
        return 0
    return shift % alphabet_length

def get_shifted_alphabet(shift: int, alphabet: str) -> str:
    """"
    Возвращает алфавит со сдвигом на указанное количество позиций.
    """
    alphabet_length = len(alphabet)
    if alphabet_length == 0:
        return ""
    
    shift = normalize_shift(shift, alphabet_length)
    shifted_alphabet = []
    
    for i in range(alphabet_length):
        new_index = (i + shift) % alphabet_length
        shifted_alphabet.append(alphabet[new_index])
    
    return ''.join(shifted_alphabet)


def encrypt(text: str, shift: int, alphabet: str) -> str:
    """"
    Шифрует text, сдвигая буквы на заданное число позиций shift в указанном alphabet.
    alphabet — строка уникальных символов в порядке алфавита.
    Неизвестные символы остаются без изменений.
    """
    alphabet_length = len(alphabet)
    if alphabet_length == 0:
        return text
    shift = normalize_shift(shift, alphabet_length)
    encrypted_text = []
    for char in text:
        lower_char = char.lower()
        if lower_char in alphabet:
            original_index = alphabet.index(lower_char)
            new_index = (original_index + shift) % alphabet_length
            encrypted_text.append(alphabet[new_index].upper() if char.isupper() else alphabet[new_index])
        else:
            encrypted_text.append(char)
    return ''.join(encrypted_text)


def decrypt(text: str, shift: int, alphabet: str) -> str:
    """"
    Дешифрует text, сдвигая буквы на заданное число позиций shift в обратную сторону в указанном alphabet.
    alphabet — строка уникальных символов в порядке алфавита.
    Неизвестные символы остаются без изменений.
    """
    alphabet_length = len(alphabet)
    if alphabet_length == 0:
        return text
    shift = normalize_shift(shift, alphabet_length)
    decrypted_text = []
    for char in text:
        lower_char = char.lower()
        if lower_char in alphabet:
            original_index = alphabet.index(lower_char)
            new_index = (original_index - shift) % alphabet_length
            decrypted_text.append(alphabet[new_index].upper() if char.isupper() else alphabet[new_index])
        else:
            decrypted_text.append(char)
    return ''.join(decrypted_text)


def brute_force_caesar(text: str, alphabet: str) -> list[tuple[int, str]]:
    """"
    Пытается расшифровать text, перебирая все возможные сдвиги в указанном alphabet.
    Возвращает список кортежей (shift, decrypted_text) для каждого возможного сдвига.
    """
    alphabet_length = len(alphabet)
    if alphabet_length == 0:
        return [(0, text)]
    results = []
    for shift in range(alphabet_length):
        decrypted_text = decrypt(text, shift, alphabet)
        results.append((shift, decrypted_text))
    return results


if __name__ == "__main__":
    # alphabet = "abcdefghijklmnopqrstuvwxyz"
    # text = "Hello World!"
    alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    text = "приветики пистолетики"
    shift = 3
    print("Начальный алфавит:", alphabet)
    shifted_alphabet = get_shifted_alphabet(shift, alphabet)
    print(f"Алфавит со сдвигом {shift}: {shifted_alphabet}")

    encrypted = encrypt(text, shift, alphabet)
    print(f"Зашифрованный: {encrypted}")

    decrypted = decrypt(encrypted, shift, alphabet)
    print(f"Расшифрованный: {decrypted}")

    brute_force_results = brute_force_caesar(encrypted, alphabet)
    for s, t in brute_force_results:
        print(f"Сдвиг: {s}, Расшифрованный текст: {t}")