# firebase_utils.py
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage
import json
from datetime import timedelta
import hashlib  # Untuk hashing
import os       # Untuk membuat salt (data acak)
import hmac

# Placeholder for DB connection

@st.cache_resource
def init_firebase():
    """Menginisialisasi koneksi Firebase Admin SDK."""
    try:
        creds_json = st.secrets["credentials"]
        creds_dict = json.loads(creds_json)
        creds = credentials.Certificate(creds_dict)
    except:
        try:
            creds = credentials.Certificate("credentials.json")
        except FileNotFoundError:
            st.error("File credentials.json tidak ditemukan!")
            return None
        except ValueError as e:
            st.error(f"Error saat memuat credentials.json: {e}")
            return None
    
    try:
        firebase_admin.initialize_app(creds)
    except ValueError:
        firebase_admin.get_app()
    
    return firestore.client() 

# --- FUNGSI LOGIN YANG DIPERBAIKI ---
def login_user(db, username, password):
    """
    Memverifikasi kredensial pengguna dengan Firestore.
    Menggunakan username sebagai ID Dokumen dan memverifikasi hash dengan salt.
    """
    if db is None:
        return False, "Koneksi database gagal."
    if not username or not password:
        return False, "Username dan password tidak boleh kosong."

    try:
        # 1. GUNAKAN .document() UNTUK MENGAMBIL USER SECARA LANGSUNG
        # Ini jauh lebih cepat dan tidak perlu indeks
        st.write("Mencari user...")
        user_doc_ref = db.collection('dropboxaccount').document(username)
        user_doc = user_doc_ref.get()
        
        if not user_doc.exists:
            st.write("User tidak ditemukan.")
            return False, "Username tidak ditemukan."
        
        # 2. AMBIL DATA HASH DAN SALT
        st.write("Mengambil data user...")
        user_data = user_doc.to_dict()
        stored_hash_hex = user_data.get('password_hash')
        salt_hex = user_data.get('salt')
        
        if not stored_hash_hex or not salt_hex:
            st.write("Data pengguna korup.")
            return False, "Data pengguna korup (hash/salt tidak ada)."
        
        # 3. VERIFIKASI HASH MENGGUNAKAN SALTs
        st.write("Memverifikasi password...")
        salt = bytes.fromhex(salt_hex)
        
        # Hash password yang dimasukkan PENGGUNA menggunakan SALT YANG TERSIMPAN
        check_hash = hashlib.pbkdf2_hmac(
            'sha512',
            password.encode('utf-8'),
            salt,
            100000  # Iterasi harus SAMA dengan saat registrasi
        )
        
        stored_hash = bytes.fromhex(stored_hash_hex)
        
        # 4. BANDINGKAN HASH DENGAN AMAN
        st.write("Membandingkan hash...")
        if hmac.compare_digest(check_hash, stored_hash):
            return True, "Login berhasil!"
        else:
            return False, "Password salah."
            
    except Exception as e:
        st.error(f"Terjadi error: {e}")
        return False, "Terjadi error saat login."

# --- FUNGSI REGISTRASI (YANG COCOK DENGAN LOGIN DI ATAS) ---
def register_user(db, username, name, password):
    """Mendaftarkan pengguna baru menggunakan username sebagai ID Dokumen."""
    if db is None:
        return False, "Koneksi database gagal."
        
    users_ref = db.collection('dropboxaccount')
    
    # Cek jika dokumen dengan ID username itu sudah ada
    if users_ref.document(username).get().exists:
        return False, "Username sudah digunakan."
    
    # Buat salt baru
    salt = os.urandom(16)
    
    # Buat hash baru
    hashed_password = hashlib.pbkdf2_hmac(
        'sha512',
        password.encode('utf-8'),
        salt,
        100000
    )
    
    # Simpan data, hash, dan salt
    user_data = {
        'name': name,
        'password_hash': hashed_password.hex(),
        'salt': salt.hex()
    }
    
    # Simpan data menggunakan username sebagai ID Dokumen
    users_ref.document(username).set(user_data)
    return True, "Registrasi berhasil!"

def hash_password(password):
    """Contoh hashing sederhana menggunakan SHA-512."""
    return hashlib.sha512(password.encode()).hexdigest()

def verify_password(password, stored_hash):
    """Memverifikasi password yang di-hash."""
    return hash_password(password) == stored_hash
