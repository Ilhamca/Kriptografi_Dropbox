import streamlit as st
from src.firebase_utils import login_user, register_user
from streamlit_cookies_controller import CookieController
import datetime

# Import database connection utilities here


# --- FUNGSI TAMPILAN LOGIN ---
def render_login_page(db, controller: CookieController) -> None:
    """Menampilkan halaman login dan menangani logikanya."""
    
    st.title("🔐 Secure Digital Dropbox Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
    
        if submitted:
            # Panggil fungsi login dari backend
            success, message = login_user(db, username, password)

            if success:
                controller.set('logged_in_user', username)
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.success(message + " Mengalihkan...")
                st.rerun()
            else:
                st.toast(message, icon="❌") # Gunakan toast agar pesan error hilang
    
    # Tombol pindah halaman (sudah benar)
    if st.button("Belum punya akun? Daftar di sini"):
        st.session_state['page'] = "register"
        st.rerun()