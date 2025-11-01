import streamlit as st
import hashlib

# --- FUNGSI HASHING (Kriteria 2) ---
# Di proyek nyata, ini ada di crypto_utils.py dan Anda akan menggunakan bcrypt
def hash_password(password):
    """Contoh hashing sederhana menggunakan SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, stored_hash):
    """Memverifikasi password yang di-hash."""
    return hash_password(password) == stored_hash

# --- FUNGSI TAMPILAN LOGIN ---
def render_login_page():
    """Menampilkan halaman login dan menangani logikanya."""
    
    st.set_page_config(page_title="Login")
    st.title("🔐 Secure Digital Dropbox Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            # --- INI ADALAH KONEKTIVITASNYA ---
            # Di aplikasi Anda:
            # 1. Hubungkan ke MySQL
            # 2. SELECT password_hash FROM users WHERE username = ?
            
            # Untuk contoh ini, kita hardcode pengguna "admin"
            # Hash ini adalah untuk password "adminpass"
            EXAMPLE_HASH = "d292e76f6e1a8f6aad1d41162aa87663a232f232b61403d65b184236a3d1fd7c"

            if username == "admin" and verify_password(password, EXAMPLE_HASH):
                # Jika login berhasil, atur Session State
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                
                st.success("Login berhasil! Mengalihkan...")
                st.rerun()
            else:
                st.error("Username atau password salah")