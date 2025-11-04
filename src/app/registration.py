import streamlit as st
import hashlib
from src.app.login import render_login_page
from src.firebase_utils import register_user
from streamlit_cookies_controller import CookieController

# --- FUNGSI HASHING (Kriteria 2) ---
# Di proyek nyata, ini ada di crypto_utils.py dan Anda akan menggunakan hash
def hash_password(password):
    """Contoh hashing sederhana menggunakan SHA-512."""
    return hashlib.sha512(password.encode()).hexdigest()

def verify_password(password, stored_hash):
    """Memverifikasi password yang di-hash."""
    return hash_password(password) == stored_hash

def render_registration_page(db, controller: CookieController) -> None:
    """Menampilkan halaman registrasi dan menangani logikanya."""
    
    st.title("📝 Registrasi Akun Dropbox Digital Anda")

    with st.form("registration_form"):
        username = st.text_input("Username")
        name = st.text_input("Nama Lengkap")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Konfirmasi Password", type="password")
        submitted = st.form_submit_button("Daftar")

        if submitted:
            if password != confirm_password:
                st.error("Password dan konfirmasi password tidak cocok.")
            elif not username or not name or not password:
                st.error("Semua field harus diisi.")
            else:
                # Panggil fungsi registrasi dari firebase_utils
                # Gunakan 'db' dari parameter
                # Kirim password MENTAH, biarkan firebase_utils yang melakukan hashing
                

                
                success, message = register_user(
                    db=db,
                    username=username,
                    name=name,
                    password=password  # Kirim password mentah
                )
                
                if success:
                    st.success("Registrasi berhasil! Silakan login.")
                    # Arahkan kembali ke halaman login
                    st.session_state['page'] = "login"
                    st.rerun() # Ganti st.experimental_rerun()
                else:
                    st.error(f"Registrasi gagal: {message}")

    # Perbaiki logika tombol ini
    if st.button("Sudah punya akun? Login di sini"):
        st.session_state['page'] = "login"
        # JANGAN panggil render_login_page()
        st.rerun() # Cukup ubah state dan rerun