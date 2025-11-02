import streamlit as st
from Crypto.Cipher import ARC4
from src.crypto import caesar_encrypt, caesar_decrypt, caesar_bruteforce, encrypt_vigenere, decrypt_vigenere, encrypt_rc4, encrypt_super
from src.firebase_utils import init_firebase
# Impor fungsi tampilan login dari file login.py
from src.app.login import render_login_page
from src.app.dashboard import main_app as render_main_app
from src.app.registration import render_registration_page
 
# Init firebase
db = init_firebase()

# --- LOGIKA PENGONTROL UTAMA ---

# Inisialisasi session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'page' not in st.session_state:
    st.session_state['page'] = "login"  # Halaman default harus "login"

# --- Router Utama (Lebih Sederhana) ---
if st.session_state['logged_in']:
    # Jika SUDAH login, selalu jalankan aplikasi utama
    # Berikan 'db' jika aplikasi utama membutuhkannya
    render_main_app(db) 
else:
    # Jika BELUM login, cek halaman mana yang harus ditampilkan
    if st.session_state['page'] == "login":
        render_login_page(db)  # Lewatkan 'db' ke halaman login
    elif st.session_state['page'] == "register":
        render_registration_page(db)  # Lewatkan 'db' ke halaman registrasi

