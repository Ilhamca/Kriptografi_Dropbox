import streamlit as st
from Crypto.Cipher import ARC4
from src.crypto import caesar_encrypt, caesar_decrypt, caesar_bruteforce, encrypt_vigenere, decrypt_vigenere, encrypt_rc4, encrypt_super
from src.firebase_utils import init_firebase, login_user, register_user

# Impor fungsi tampilan login dari file login.py
from src.app.login import render_login_page

# Init firebase
db = init_firebase()

# --- FUNGSI APLIKASI UTAMA ---
def render_main_app():
    """Menampilkan aplikasi dropbox utama setelah login berhasil."""
    
    st.set_page_config(page_title="Dropbox", layout="wide")
    
    # --- Sidebar (Navigasi) ---
    st.sidebar.title(f"Selamat Datang, {st.session_state['username']}!")
    
    # --- Tombol Logout (Penting!) ---
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""
        st.rerun() # Muat ulang untuk kembali ke halaman login

    # --- Konten Aplikasi Utama Anda ---
    st.title("📤 Secure Digital Dropbox")
    st.subheader("Aplikasi Anda dimulai di sini...")

    tab_upload, tab_files = st.tabs(["Upload File", "Lihat File"])

    with tab_upload:
        st.write("Form upload Anda (untuk file, gambar, teks) ada di sini.")
        # ... (st.file_uploader, st.text_area, dll.) ...

    with tab_files:
        st.write("Daftar file Anda (dari MySQL) ada di sini.")
        # ... (st.dataframe, st.download_button, dll.) ...

# --- LOGIKA PENGONTROL UTAMA ---

# Inisialisasi session state jika belum ada
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Memutuskan halaman apa yang akan ditampilkan
if st.session_state['logged_in'] == False:
    # Jika BELUM login, jalankan fungsi dari login.py
    render_login_page()
else:
    # Jika SUDAH login, jalankan aplikasi utama
    render_main_app()






