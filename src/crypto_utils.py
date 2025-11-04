# src/crypto_utils.py
import hashlib
import os
from Crypto.Cipher import ARC4, ChaCha20
from Crypto.Random import get_random_bytes

# --- Bagian 1: Algoritma Super Enkripsi (Kriteria 3) ---
# Ini adalah 3 algoritma yang Anda minta (Vigenere, Railway, RC4)
# Semuanya diimplementasikan dalam "Byte Mode" agar berfungsi pada file apa pun.

def _derive_keys(password: str, salt: bytes = b'static_salt_for_project') -> tuple:
    """
    Menghasilkan semua kunci yang diperlukan dari satu password.
    Kita akan menghasilkan 48 bytes:
    - 32 bytes untuk kunci RC4
    - 16 bytes untuk kunci Vigenere
    
    Sumber (hashlib.pbkdf2_hmac): https://docs.python.org/3/library/hashlib.html
    """
    # PBKDF2 digunakan untuk membuat kunci kriptografi yang kuat dari password
    derived_key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,  # Idealnya, salt ini unik per file, tapi statis tidak apa-apa untuk proyek ini
        100000,
        dklen=48  # Minta total 48 byte
    )
    
    rc4_key = derived_key[:32]       # 32 byte pertama untuk RC4
    vigenere_key = derived_key[32:]  # 16 byte sisanya untuk Vigenere
    
    # Tentukan jumlah "rel" berdasarkan panjang password (2-9 rel)
    num_rails = (len(password) % 8) + 2
    
    return rc4_key, vigenere_key, num_rails

def _encrypt_vigenere_bytes(data: bytes, key: bytes) -> bytes:
    """Versi Vigenere Cipher yang beroperasi pada bytes (mod 256)."""
    encrypted = bytearray()
    key_len = len(key)
    for i, byte in enumerate(data):
        key_byte = key[i % key_len]
        # (P + K) % 256
        encrypted_byte = (byte + key_byte) % 256
        encrypted.append(encrypted_byte)
    return bytes(encrypted)

def _decrypt_vigenere_bytes(data: bytes, key: bytes) -> bytes:
    """Dekripsi Vigenere Cipher mode byte."""
    decrypted = bytearray()
    key_len = len(key)
    for i, byte in enumerate(data):
        key_byte = key[i % key_len]
        # (C - K + 256) % 256
        decrypted_byte = (byte - key_byte + 256) % 256
        decrypted.append(decrypted_byte)
    return bytes(decrypted)

def _encrypt_railway_bytes(data: bytes, rails: int) -> bytes:
    """Versi Railway Fence Cipher yang beroperasi pada bytes."""
    if rails <= 1 or rails >= len(data):
        return data
    
    # Buat "pagar" (fence)
    fence = [bytearray() for _ in range(rails)]
    rail_idx = 0
    direction = 1  # 1 = turun, -1 = naik

    for byte in data:
        fence[rail_idx].append(byte)
        
        # Ubah arah jika mencapai rel atas atau bawah
        if rail_idx == rails - 1:
            direction = -1
        elif rail_idx == 0:
            direction = 1
        
        rail_idx += direction
            
    # Gabungkan semua rel
    return b"".join(fence)

def _decrypt_railway_bytes(data: bytes, rails: int) -> bytes:
    """Dekripsi Railway Fence Cipher mode byte."""
    if rails <= 1 or rails >= len(data):
        return data

    data_len = len(data)
    
    # 1. Buat template pagar untuk mengetahui panjang setiap rel
    fence_template = [[] for _ in range(rails)]
    rail_idx = 0
    direction = 1
    
    for i in range(data_len):
        fence_template[rail_idx].append(i) # Isi dengan placeholder
        if rail_idx == rails - 1: direction = -1
        elif rail_idx == 0: direction = 1
        rail_idx += direction
    
    # 2. Pisahkan data terenkripsi ke dalam rel
    fence = []
    start = 0
    for rail in fence_template:
        rail_len = len(rail)
        fence.append(bytearray(data[start : start + rail_len]))
        start += rail_len
    
    # 3. Baca kembali dalam urutan zig-zag
    decrypted = bytearray()
    rail_idx = 0
    direction = 1
    
    for _ in range(data_len):
        # Ambil byte pertama dari rel saat ini
        decrypted.append(fence[rail_idx].pop(0))
        
        if rail_idx == rails - 1: direction = -1
        elif rail_idx == 0: direction = 1
        rail_idx += direction
            
    return bytes(decrypted)

# --- FUNGSI PUBLIK (SUPER ENKRIPSI) ---

def encrypt_super(file_bytes: bytes, password: str) -> bytes:
    """
    Mengenkripsi file menggunakan Vigenere -> Railway -> RC4.
    Sumber (PyCryptodome ARC4): https://www.pycryptodome.org/en/latest/src/cipher/arc4.html
    """
    rc4_key, vigenere_key, num_rails = _derive_keys(password)
    
    # Lapisan 1: Vigenere
    vigenere_encrypted = _encrypt_vigenere_bytes(file_bytes, vigenere_key)
    
    # Lapisan 2: Railway Fence
    railway_encrypted = _encrypt_railway_bytes(vigenere_encrypted, num_rails)
    
    # Lapisan 3: RC4
    cipher_rc4 = ARC4.new(rc4_key)
    final_encrypted = cipher_rc4.encrypt(railway_encrypted)
    
    return final_encrypted

def decrypt_super(file_bytes: bytes, password: str) -> bytes:
    """Mendekripsi file dalam urutan terbalik: RC4 -> Railway -> Vigenere."""
    rc4_key, vigenere_key, num_rails = _derive_keys(password)

    # Lapisan 1: RC4
    cipher_rc4 = ARC4.new(rc4_key)
    rc4_decrypted = cipher_rc4.decrypt(file_bytes)
    
    # Lapisan 2: Railway Fence
    try:
        railway_decrypted = _decrypt_railway_bytes(rc4_decrypted, num_rails)
    except IndexError:
        # Ini terjadi jika password salah (jumlah rel salah)
        raise Exception("Password salah atau file korup (Railway)")
    except Exception as e:
        raise Exception(f"Dekripsi Railway gagal: {e}")
        
    # Lapisan 3: Vigenere
    final_decrypted = _decrypt_vigenere_bytes(railway_decrypted, vigenere_key)
    
    return final_decrypted

# --- Bagian 2: Kriptografi Lain (Kriteria 5) ---
# Kita gunakan ChaCha20, algoritma modern yang berbeda dari RC4.
# Ini akan menjadi `encrypt_file` dan `decrypt_file` Anda.

def encrypt_file(file_bytes: bytes, password: str) -> bytes:
    """
    Mengenkripsi file menggunakan ChaCha20 (Konsep Kriptografi Lain).
    Sumber (PyCryptodome ChaCha20): https://www.pycryptodome.org/en/latest/src/cipher/chacha20.html
    """
    # Gunakan KDF yang sama untuk mendapatkan kunci
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), b'salt_chacha', 100000, dklen=32)
    
    cipher = ChaCha20.new(key=key)
    ciphertext = cipher.encrypt(file_bytes)
    
    # Kita harus menyimpan 'nonce' (nilai unik) bersama dengan ciphertext
    # Nonce ChaCha20 adalah 12 byte
    return cipher.nonce + ciphertext

def decrypt_file(encrypted_bytes: bytes, password: str) -> bytes:
    """Mendekripsi file ChaCha20."""
    try:
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), b'salt_chacha', 100000, dklen=32)
        
        # Pisahkan nonce (12 byte pertama) dari sisa ciphertext
        nonce = encrypted_bytes[:12]
        ciphertext = encrypted_bytes[12:]
        
        cipher = ChaCha20.new(key=key, nonce=nonce)
        decrypted_bytes = cipher.decrypt(ciphertext)
        return decrypted_bytes
    except (ValueError, KeyError, TypeError):
        # Error ini akan terjadi jika password salah (kunci salah)
        # atau jika file tersebut tidak dienkripsi dengan ChaCha20
        raise Exception("Password salah atau file korup.")