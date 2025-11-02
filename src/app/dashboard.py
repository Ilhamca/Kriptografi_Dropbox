import streamlit as st
from Crypto.Cipher import ARC4
from src.crypto import caesar_encrypt, caesar_decrypt, caesar_bruteforce, encrypt_vigenere, decrypt_vigenere, encrypt_rc4, encrypt_super
from streamlit_cookies_controller import CookieController

def vinegere_page() -> None:
	st.title("Vigenère Cipher Demo")

	col1, col2 = st.columns(2)
	with col1:
		mode = st.radio("Mode", ["Encrypt", "Decrypt"], index=0)
		key = st.text_input("Key", value="")
	with col2:
		text = st.text_area("Input text", height=200)
	if st.button("Run"):
		if not text:
			st.warning("Please provide input text.")
			return
		if text and not key.isalpha():
			st.warning("Key must consist of alphabetic characters only.")
			return
		if not key:
			st.warning("Please provide a key.")
			return
		if mode == "Encrypt":
			out = encrypt_vigenere(text, key)
			st.success("Encrypted text:")
			st.code(out)
		else:
			out = decrypt_vigenere(text, key)
			st.success("Decrypted text:")
			st.code(out)

def SuperEncryption_page() -> None:
	st.title("Super Encryption Demo")

	col1, col2 = st.columns(2)
	with col1:
		mode = st.radio("Mode", ["Encrypt", "Decrypt"], index=0)
		key = st.text_input("Key", value="")
	with col2:
		text = st.text_area("Input text", height=200)
	if st.button("Run"):
		if not text:
			st.warning("Please provide input text.")
			return
		if not key:
			st.warning("Please provide a key.")
			return
		if mode == "Encrypt":
			out = encrypt_super(text, key)
			st.success("Encrypted text:")
			st.code(out)
		else:
			#out = decrypt_super(text, key)
			st.success("Decrypted text:")
			st.code(out)


def ARC4_page() -> None:
	st.title("ARC4 Cipher Demo")

	col1, col2 = st.columns(2)
	with col1:
		mode = st.radio("Mode", ["Encrypt", "Decrypt"], index=0)
		key = st.text_input("Key", value="")
	with col2:
		text = st.text_area("Input text", height=200)
	if st.button("Run"):
		if not text:
			st.warning("Please provide input text.")
			return
		if not key:
			st.warning("Please provide a key.")
			return
		cipher = ARC4.new(key.encode('utf-8'))
		if mode == "Encrypt":
			out = cipher.encrypt(text.encode('utf-8'))
			st.success("Encrypted text (hex):")
			st.code(out.hex())
		else:
			try:
				ciphertext_bytes = bytes.fromhex(text)
				out = cipher.decrypt(ciphertext_bytes)
				st.success("Decrypted text:")
				st.code(out.decode('utf-8'))
			except ValueError:
				st.error("Invalid hex input for decryption.")
     
     
def main_app(db) -> None:
	"""Menampilkan aplikasi dropbox utama setelah login berhasil."""
	# --- Sidebar (Navigasi) ---
	st.sidebar.title(f"Selamat Datang, {st.session_state['username']}!")

	# --- Tombol Logout (Penting!) ---
	if st.sidebar.button("Logout"):
		st.session_state['logged_in'] = False
		st.session_state['username'] = ""
		st.session_state['page'] = "login"
		st.rerun()  # Muat ulang untuk kembali ke halaman login

	st.sidebar.title("Navigation")
	page = st.sidebar.radio("Go to", ["Home", "Caesar Cipher", "Vigenère Cipher", "ARC4 Cipher", "Super Encryption"])

	if page == "Home":
		st.title("Kriptografi — Streamlit Demo")
		st.write("Select a demo from the sidebar.")
	elif page == "Caesar Cipher":
		#caesar_page()
		pass
	elif page == "Vigenère Cipher":
		vinegere_page()
	elif page == "ARC4 Cipher":
		ARC4_page()
	elif page == "Super Encryption":
		SuperEncryption_page()