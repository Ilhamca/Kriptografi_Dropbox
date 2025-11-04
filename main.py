import streamlit as st
from Crypto.Cipher import ARC4
from src.firebase_utils import init_firebase
from src.app.login import render_login_page
from src.app.registration import render_registration_page
from streamlit_cookies_controller import CookieController
from src.app.dashboard import main_app
import st_cookie
import datetime 
 
# Init firebase & Cookies Controller
st.set_page_config(
    page_title="Secure Digital Dropbox",
    page_icon="🧊",
    layout="centered",
        menu_items={
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

db = init_firebase()


# --- LOGIKA PENGONTROL UTAMA ---
controller = CookieController()
st_cookie.sync(
    'logged_in', 
    'username', 
    'page',
)

# Inisialisasi session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    try:
        logged_in_user = controller.get('logged_in_user')
        # Biarkan baris debug ini tetap ada
        print(f"DEBUG: Nilai cookie 'logged_in_user' saat dimuat: {logged_in_user}")
        
        if logged_in_user:
            st.session_state['logged_in'] = True
            st.session_state['username'] = logged_in_user
    except Exception as e:
        st.error(f"DEBUG: Terjadi kesalahan saat memuat cookie: {e}")
        st.session_state['logged_in'] = False
if 'page' not in st.session_state:
    st.session_state['page'] = "login"  # Halaman default harus "login"

# --- Router Utama (Lebih Sederhana) ---
if st.session_state['logged_in']:
    # Jika SUDAH login, selalu jalankan aplikasi utama
    # Berikan 'db' jika aplikasi utama membutuhkannya
    main_app(db, controller) 
else:
    # Jika BELUM login, cek halaman mana yang harus ditampilkan
    if st.session_state['page'] == "login":
        render_login_page(db, controller)  # Lewatkan 'db' dan 'controller' ke halaman login
    elif st.session_state['page'] == "register":
        render_registration_page(db, controller)  # Lewatkan 'db' dan 'controller' ke halaman registrasi

