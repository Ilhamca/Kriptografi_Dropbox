from typing import Tuple
from Crypto.Cipher import ARC4

def caesar_encrypt(plaintext: str, shift: int) -> str:
    """Encrypts plaintext using a Caesar cipher with given shift.

    Non-alphabetic characters are left unchanged. Preserves case.
    """
    if plaintext is None:
        raise ValueError("plaintext must not be None")
    if not isinstance(shift, int):
        raise ValueError("shift must be an integer")

    result = []
    for ch in plaintext:
        if 'a' <= ch <= 'z':
            base = ord('a')
            result.append(chr((ord(ch) - base + shift) % 26 + base))
        elif 'A' <= ch <= 'Z':
            base = ord('A')
            result.append(chr((ord(ch) - base + shift) % 26 + base))
        else:
            result.append(ch)
    return ''.join(result)


def caesar_decrypt(ciphertext: str, shift: int) -> str:
    """Decrypts ciphertext produced with a Caesar cipher with given shift."""
    return caesar_encrypt(ciphertext, -shift)


def caesar_bruteforce(ciphertext: str) -> Tuple[int, str]:
    """Return the most likely decryption by trying all shifts.

    For this simple demo, it returns a list of all possible shifts and plaintexts as a string.
    """
    candidates = []
    for s in range(26):
        candidates.append((s, caesar_decrypt(ciphertext, s)))
    return candidates

def encrypt_vigenere(text, key):
    """Encrypts plaintext using a Vigenère cipher with the given key.

    Non-alphabetic characters are left unchanged. Preserves case.
    """
    if text is None:
        raise ValueError("text must not be None")
    if not key.isalpha():
        raise ValueError("key must consist of alphabetic characters only")

    result = []
    key_length = len(key)
    key_index = 0

    for ch in text:
        if ch.isalpha():
            shift = ord(key[key_index % key_length].lower()) - ord('a')
            if ch.islower():
                base = ord('a')
                result.append(chr((ord(ch) - base + shift) % 26 + base))
            else:
                base = ord('A')
                result.append(chr((ord(ch) - base + shift) % 26 + base))
            key_index += 1
        else:
            result.append(ch)

    return ''.join(result)

def decrypt_vigenere(ciphertext, key):
    """Decrypts ciphertext produced with a Vigenère cipher with the given key.

    Non-alphabetic characters are left unchanged. Preserves case.
    """
    if ciphertext is None:
        raise ValueError("ciphertext must not be None")
    if not key.isalpha():
        raise ValueError("key must consist of alphabetic characters only")

    result = []
    key_length = len(key)
    key_index = 0

    for ch in ciphertext:
        if ch.isalpha():
            shift = ord(key[key_index % key_length].lower()) - ord('a')
            if ch.islower():
                base = ord('a')
                result.append(chr((ord(ch) - base - shift) % 26 + base))
            else:
                base = ord('A')
                result.append(chr((ord(ch) - base - shift) % 26 + base))
            key_index += 1
        else:
            result.append(ch)

    return ''.join(result)

def encrypt_railway_fence(plaintext: str, num_rails: int) -> str:
    """Encrypts plaintext using the Rail Fence cipher with the given number of rails."""
    if plaintext is None:
        raise ValueError("plaintext must not be None")
    if num_rails < 2:
        raise ValueError("num_rails must be at least 2")

    rails = ['' for _ in range(num_rails)]
    rail = 0
    direction = 1  # 1 for down, -1 for up

    for ch in plaintext:
        rails[rail] += ch
        rail += direction
        if rail == 0 or rail == num_rails - 1:
            direction *= -1

    return ''.join(rails)

def encrypt_rc4(data, key):
    """Encrypts data using the RC4 stream cipher with the given key."""
    if data is None:
        raise ValueError("data must not be None")
    if not isinstance(key, (bytes, bytearray)):
        raise ValueError("key must be bytes or bytearray")

    cipher = ARC4.new(key)
    return cipher.encrypt(data)

def encrypt_super(plaintext: str, key: str) -> str:
    """A placeholder for a custom 'Super Encryption' algorithm."""
    # Combines Railway Fence, Vigenère, and RC4 concepts.
    if plaintext is None:
        raise ValueError("plaintext must not be None")
    # Change plaintext to hexadecimal representation
    hex_plaintext = plaintext.encode('utf-8').hex()
    # Step 1: Railway Fence with 3 rails
    rail_fence_encrypted = encrypt_railway_fence(hex_plaintext, 3)
    # Step 2: Vigenère cipher with the provided key
    vigenere_encrypted = encrypt_vigenere(rail_fence_encrypted, key)
    # Step 3: RC4 encryption
    rc4_encrypted = encrypt_rc4(vigenere_encrypted.encode('utf-8'), key.encode('utf-8'))
    return rc4_encrypted.hex()
