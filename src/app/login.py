import streamlit as st
import hashlib
from src.firebase_utils import login_user

# Import database connection utilities here


# --- FUNGSI HASHING (Kriteria 2) ---
# Di proyek nyata, ini ada di crypto_utils.py dan Anda akan menggunakan bcrypt
def hash_password(password):
    """Contoh hashing sederhana menggunakan SHA-512."""
    return hashlib.sha512(password.encode()).hexdigest()

def verify_password(password, stored_hash):
    """Memverifikasi password yang di-hash."""
    return hash_password(password) == stored_hash

# --- FUNGSI TAMPILAN LOGIN ---
def render_login_page(db):
    """Menampilkan halaman login dan menangani logikanya."""
    
    # Pindahkan st.session_state['page'] ke tombol
    st.set_page_config(page_title="Login")
    st.title("🔐 Secure Digital Dropbox Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
    
        if submitted:
            # Panggil login_user dengan 'db' dan password mentah
            # Asumsi: login_user mengembalikan (True, "pesan") jika sukses
            # dan (False, "pesan") jika gagal
            success, message = login_user(db, username, password)

            if success:
                # Jika login berhasil, atur Session State
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.success(message + " Mengalihkan...")
                st.rerun() # <-- TAMBAHKAN INI untuk pindah ke main_app
            else:
                st.error(message) # Tampilkan pesan error dari backend
    
    # Perbaiki logika tombol ini
    if st.button("Belum punya akun? Daftar di sini"):
        st.session_state['page'] = "register"
        st.rerun() # Cukup ubah state dan rerun