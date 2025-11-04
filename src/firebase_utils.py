# firebase_utils.py
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage
import json
from datetime import timedelta
import hashlib  # Untuk hashing
import os       # Untuk membuat salt (data acak)
import hmac     # Untuk compare_digest

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
    
    # --- PERBAIKAN 1: Logika Inisialisasi Diperbaiki ---
    try:
        # Coba ambil aplikasi yang sudah ada
        firebase_admin.get_app()
    except ValueError:
        # Jika belum ada, baru inisialisasi
        firebase_admin.initialize_app(creds)
    
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
        # --- PERBAIKAN 2: Hapus semua st.write() ---
        user_doc_ref = db.collection('dropboxaccount').document(username)
        user_doc = user_doc_ref.get()
        
        if not user_doc.exists:
            return False, "Username tidak ditemukan."
        
        user_data = user_doc.to_dict()
        stored_hash_hex = user_data.get('password_hash')
        salt_hex = user_data.get('salt')
        
        if not stored_hash_hex or not salt_hex:
            return False, "Data pengguna korup (hash/salt tidak ada)."
        
        salt = bytes.fromhex(salt_hex)
        
        check_hash = hashlib.pbkdf2_hmac(
            'sha512',
            password.encode('utf-8'),
            salt,
            100000  # Iterasi harus SAMA dengan saat registrasi
        )
        
        stored_hash = bytes.fromhex(stored_hash_hex)
        
        # Ganti nama 'compare_digest' (dari 'timing_safe_compare')
        if hmac.compare_digest(check_hash, stored_hash):
            return True, "Login berhasil!"
        else:
            return False, "Password salah."
            
    except Exception as e:
        st.error(f"Terjadi error: {e}")
        return False, "Terjadi error saat login."

# --- FUNGSI REGISTRASI (Sudah Benar) ---
def register_user(db, username, name, password):
    """Mendaftarkan pengguna baru menggunakan username sebagai ID Dokumen."""
    if db is None:
        return False, "Koneksi database gagal."
        
    users_ref = db.collection('dropboxaccount')
    
    if users_ref.document(username).get().exists:
        return False, "Username sudah digunakan."
    
    salt = os.urandom(16)
    hashed_password = hashlib.pbkdf2_hmac(
        'sha512',
        password.encode('utf-8'),
        salt,
        100000
    )
    
    user_data = {
        'name': name,
        'password_hash': hashed_password.hex(),
        'salt': salt.hex()
    }
    
    users_ref.document(username).set(user_data)
    return True, "Registrasi berhasil!"

# --- Fungsi File (Semua sudah benar) ---

def log_file_to_firestore(db, username, original_filename, gdrive_file_id, crypto_type):
    """Mencatat metadata file ke subkoleksi 'files' milik pengguna."""
    try:
        files_ref = db.collection('dropboxaccount').document(username).collection('files')
        
        file_data = {
            'owner': username, 
            'original_filename': original_filename,
            'gdrive_file_id': gdrive_file_id,
            'encryption_type': crypto_type,
            'upload_timestamp': firestore.SERVER_TIMESTAMP
        }
        files_ref.add(file_data)
        return True
    except Exception as e:
        st.error(f"Gagal mencatat file ke Firestore: {e}")
        return False

def get_user_files(db, username):
    """Mengambil semua metadata file untuk pengguna tertentu dari Firestore."""
    files_ref = db.collection('dropboxaccount').document(username).collection('files')
    
    query = files_ref.order_by('upload_timestamp', direction=firestore.Query.DESCENDING).stream()
    
    file_list = []
    for doc in query:
        file_data = doc.to_dict()
        file_data['doc_id'] = doc.id
        file_list.append(file_data)
        
    return file_list

def delete_file_from_firestore(db, username, doc_id):
    """Menghapus catatan metadata file dari Firestore berdasarkan ID Dokumen."""
    try:
        doc_ref = db.collection('dropboxaccount').document(username).collection('files').document(doc_id)
        doc_ref.delete()
        return True
    except Exception as e:
        st.error(f"Error menghapus dari Firestore: {e}")
        return False

# --- PERBAIKAN 3: Hapus fungsi 'hash_password' dan 'verify_password' ---
# (Fungsi-fungsi tidak aman yang ada di bawah sini telah dihapus)