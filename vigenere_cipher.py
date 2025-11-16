def _build_index_map(alphabet: str) -> dict[str, int]:
    """Создает словарь для быстрого поиска индексов символов в алфавите."""
    return {char: index for index, char in enumerate(alphabet)}

def _normalize_key(key: str, alphabet: str) -> str:
    """Оставляет в ключе только сиволы, которые есть в alphabet и приводит их в нижний регистр
    Возвращает нормализованный ключ. Если ключ пуст - ошибка"""

    alphabet_set = set(alphabet)
    filtered_key = ''.join([char.lower() for char in key if char.lower() in alphabet_set])
    if not filtered_key:
        raise ValueError("Key must contain at least one character from the alphabet.")
    return filtered_key

def _key_stream(key: str, text: str, alphabet: str) -> list[int]:
    """Генерирует последовательность индексов сдвигов для каждого символа в text.
    Для символов, не входящих в alphabet, сдвиг равен 0."""
    key=_normalize_key(key, alphabet)
    alphabet_length = len(alphabet)
    index_map = _build_index_map(alphabet)
    key_indices = [index_map[char] for char in key]
    stream = []
    ki = 0
    for char in text:
        lower = char.lower()
        if lower in index_map:
            stream.append(key_indices[ki % len(key_indices)])
            ki += 1
        else:
            stream.append(None)
    return stream

def encrypt(text: str, key: str, alphabet: str) -> str:
    """Шифрует text с помощью ключа key, используя алфавит alphabet.
    Неизвестные символы остаются без изменений."""
    if len(alphabet) == 0:
        return text
    index_map = _build_index_map(alphabet)
    inverse_index_map = {index: char for index, char in enumerate(alphabet)}
    stream = _key_stream(key, text, alphabet)
    alphabet_length = len(alphabet)
    encrypted_text = []
    for char, shift in zip(text, stream):
        if shift is None:
            encrypted_text.append(char)
        else:
            lower = char.lower()
            pi = index_map[lower]
            ci = (pi + shift) % alphabet_length
            cchar = inverse_index_map[ci]
            encrypted_text.append(cchar.upper() if char.isupper() else cchar)
    return ''.join(encrypted_text)


def vigenere_decrypt(text: str, key: str, alphabet: str) -> str:
    """Дешифрует text с помощью ключа key, используя алфавит alphabet.
    Неизвестные символы остаются без изменений."""
    if len(alphabet) == 0:
        return text
    index_map = _build_index_map(alphabet)
    inverse_index_map = {index: char for index, char in enumerate(alphabet)}
    stream = _key_stream(key, text, alphabet)
    alphabet_length = len(alphabet)
    decrypted_text = []
    for char, shift in zip(text, stream):
        if shift is None:
            decrypted_text.append(char)
        else:
            lower = char.lower()
            ci = index_map[lower]
            pi = (ci - shift) % alphabet_length
            pchar = inverse_index_map[pi]
            decrypted_text.append(pchar.upper() if char.isupper() else pchar)
    return ''.join(decrypted_text)


if __name__ == "__main__":
    # alphabet = "abcdefghijklmnopqrstuvwxyz"
    alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    # key = "lemon"
    key = "выбрать"
    # text = "Attack at dawn!"
    text = "Метод прямого перебора"
    encrypted = encrypt(text, key, alphabet)
    print(f"Зашифрованный: {encrypted}")
    decrypted = vigenere_decrypt(encrypted, key, alphabet)
    print(f"Расшифрованный: {decrypted}")
