import pytest
from src.crypto import caesar_encrypt, caesar_decrypt


def test_encrypt_basic():
    assert caesar_encrypt("abc", 1) == "bcd"
    assert caesar_encrypt("xyz", 2) == "zab"


def test_encrypt_preserve_case_and_nonalpha():
    assert caesar_encrypt("Hello, World!", 3) == "Khoor, Zruog!"


def test_decrypt_basic():
    assert caesar_decrypt("bcd", 1) == "abc"
    assert caesar_decrypt("zab", 2) == "xyz"


def test_invalid_inputs():
    with pytest.raises(ValueError):
        caesar_encrypt(None, 3)
    with pytest.raises(ValueError):
        caesar_encrypt("text", "not-an-int")
        
