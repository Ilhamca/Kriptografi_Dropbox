# firebase_utils.py
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage
import bcrypt
import json
from datetime import timedelta

# --- INI ADALAH KUNCI UTAMA ---
# Menggunakan st.singleton untuk memastikan Firebase hanya diinisialisasi sekali.
# Di Streamlit Cloud, kita akan menggunakan st.secrets.
@st.singleton
def init_firebase():
    """Menginisialisasi koneksi Firebase Admin SDK."""
    try:
        # Coba muat dari st.secrets (untuk deployment)
        creds_json = st.secrets["firebase_credentials"]
        creds_dict = json.loads(creds_json)
        creds = credentials.Certificate(creds_dict)
    except FileNotFoundError:
        # Jika gagal (lokal), muat dari file
        creds = credentials.Certificate("credentials.json")
    except Exception:
        # Jika di Streamlit Cloud tapi secrets belum diatur
        st.error("File credentials.json tidak ditemukan atau st.secrets tidak dikonfigurasi!")
        return None

    try:
        firebase_admin.get_app()
    except ValueError:
        firebase_admin.initialize_app(creds, {
            'storageBucket': 'secure-dropbox-project.appspot.com' # GANTI DENGAN NAMA BUCKET ANDA
        })
    
    return firestore.client()

# --- FUNGSI LOGIN & REGISTRASI ---
def register_user(db, username, name, password):
    """Mendaftarkan pengguna baru ke Firestore."""
    if not username or not password:
        return False, "Username dan password tidak boleh kosong."

    users_ref = db.collection('users')
    # Cek jika username sudah ada
    if users_ref.document(username).get().exists:
        return False, "Username sudah digunakan."
    
    # Hash password menggunakan bcrypt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Simpan ke Firestore
    user_data = {
        'name': name,
        'password_hash': hashed_password.decode('utf-8') # Simpan sebagai string
    }
    users_ref.document(username).set(user_data)
    return True, "Registrasi berhasil!"

def login_user(db, username, password):
    """Memverifikasi login pengguna dari Firestore."""
    if not username or not password:
        return False, "Username dan password tidak boleh kosong."

    users_ref = db.collection('users')
    user_doc = users_ref.document(username).get()
    
    if not user_doc.exists:
        return False, "Username tidak ditemukan."
    
    user_data = user_doc.to_dict()
    stored_hash = user_data.get('password_hash').encode('utf-8')
    
    # Verifikasi hash
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
        return True, "Login berhasil!"
    else:
        return False, "Password salah."

# --- FUNGSI PENYIMPANAN FILE ---
def upload_to_storage(file_bytes, destination_blob_name, content_type):
    """Mengunggah file (dalam bytes) ke Firebase Storage."""
    bucket = storage.bucket()
    blob = bucket.blob(destination_blob_name)
    
    # Upload dari bytes
    blob.upload_from_string(file_bytes, content_type=content_type)
    
    # Buat signed URL yang valid selama 1 hari (untuk referensi)
    url = blob.generate_signed_url(timedelta(days=1), method='GET')
    return blob.name, url # Mengembalikan nama blob (path file)

def log_file_to_firestore(db, username, original_filename, blob_name, crypto_type):
    """Mencatat metadata file ke Firestore."""
    files_ref = db.collection('files')
    file_data = {
        'owner': username,
        'original_filename': original_filename,
        'storage_blob_name': blob_name,
        'encryption_type': crypto_type,
        'upload_timestamp': firestore.SERVER_TIMESTAMP
    }
    files_ref.add(file_data) # 'add' untuk membuat ID dokumen acak