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
    # Nonce ChaCha20 default adalah 8 bytes (bisa 12 jika pakai nonce=... parameter)
    nonce_length = len(cipher.nonce).to_bytes(1, byteorder='big')  # Simpan panjang nonce (1 byte)
    return nonce_length + cipher.nonce + ciphertext

def decrypt_file(encrypted_bytes: bytes, password: str) -> bytes:
    """Mendekripsi file ChaCha20."""
    try:
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), b'salt_chacha', 100000, dklen=32)
        
        # Baca panjang nonce (1 byte pertama)
        nonce_length = encrypted_bytes[0]
        
        # Pisahkan nonce dan ciphertext
        nonce = encrypted_bytes[1:1+nonce_length]
        ciphertext = encrypted_bytes[1+nonce_length:]
        
        cipher = ChaCha20.new(key=key, nonce=nonce)
        decrypted_bytes = cipher.decrypt(ciphertext)
        return decrypted_bytes
    except (ValueError, KeyError, TypeError, IndexError) as e:
        # Error ini akan terjadi jika password salah (kunci salah)
        # atau jika file tersebut tidak dienkripsi dengan ChaCha20
        raise Exception(f"Password salah atau file korup: {str(e)}")
    
def encrypt_stenography(image_bytes: bytes, secret_text: str, encrypt_password: str) -> bytes:
    """
    Menyembunyikan teks rahasia di dalam gambar menggunakan Steganografi LSB.
    Teks rahasia dienkripsi dengan super enkripsi terlebih dahulu.
    """
    # 1. Enkripsi teks rahasia dengan super enkripsi
    secret_bytes = secret_text.encode('utf-8')
    encrypted_secret = encrypt_super(secret_bytes, encrypt_password)
    
    # 2. Siapkan header: panjang data rahasia (4 bytes)
    secret_len = len(encrypted_secret)
    header = secret_len.to_bytes(4, byteorder='big')
    data_to_hide = header + encrypted_secret
    
    # 3. Cek apakah gambar cukup besar
    max_bytes = len(image_bytes) // 8  # Setiap byte perlu 8 byte gambar (1 bit per byte)
    if len(data_to_hide) > max_bytes:
        raise Exception(f"Gambar terlalu kecil. Perlu {len(data_to_hide)} bytes, tersedia {max_bytes} bytes")
    
    # 4. Sembunyikan data di LSB (Least Significant Bit) gambar
    stego_image = bytearray(image_bytes)
    data_index = 0
    bit_index = 0
    
    for i in range(len(data_to_hide) * 8):
        if data_index >= len(data_to_hide):
            break
            
        # Ambil bit dari data yang akan disembunyikan
        data_byte = data_to_hide[data_index]
        bit = (data_byte >> (7 - bit_index)) & 1
        
        # Sembunyikan bit di LSB byte gambar
        stego_image[i] = (stego_image[i] & 0xFE) | bit
        
        bit_index += 1
        if bit_index == 8:
            bit_index = 0
            data_index += 1
    
    return bytes(stego_image)


def decrypt_stenography(stego_image_bytes: bytes, decrypt_password: str) -> str:
    """
    Mengekstrak dan mendekripsi teks rahasia dari gambar steganografi.
    """
    try:
        # 1. Ekstrak header (4 bytes pertama = 32 bit)
        header_bits = []
        for i in range(32):
            bit = stego_image_bytes[i] & 1
            header_bits.append(bit)
        
        # Konversi bits ke bytes
        header_bytes = bytearray()
        for i in range(0, 32, 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | header_bits[i + j]
            header_bytes.append(byte)
        
        secret_len = int.from_bytes(header_bytes, byteorder='big')
        
        # 2. Validasi panjang
        max_extractable = (len(stego_image_bytes) // 8) - 4
        if secret_len > max_extractable or secret_len <= 0:
            raise Exception("Data rahasia tidak valid atau password salah")
        
        # 3. Ekstrak data terenkripsi
        total_bits = (secret_len + 4) * 8
        extracted_bits = []
        for i in range(total_bits):
            bit = stego_image_bytes[i] & 1
            extracted_bits.append(bit)
        
        # Konversi bits ke bytes (skip header 32 bit pertama)
        extracted_bytes = bytearray()
        for i in range(32, len(extracted_bits), 8):
            byte = 0
            for j in range(8):
                if i + j < len(extracted_bits):
                    byte = (byte << 1) | extracted_bits[i + j]
            extracted_bytes.append(byte)
        
        encrypted_secret = bytes(extracted_bytes[:secret_len])
        
        # 4. Dekripsi dengan super dekripsi
        decrypted_bytes = decrypt_super(encrypted_secret, decrypt_password)
        secret_text = decrypted_bytes.decode('utf-8')
        
        return secret_text
        
    except Exception as e:
        raise Exception(f"Gagal mengekstrak pesan.")