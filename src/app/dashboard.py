# src/app/dashboard.py
import streamlit as st
import datetime
# Impor file-file utilitas Anda
from src import firebase_utils
from src import google_utils
from src import crypto_utils
from stegano import lsb
import io

def main_app(db, controller) -> None:
    st.sidebar.title(f"Selamat Datang, {st.session_state['username']}!")
    # ... (kode logout Anda) ...

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Upload File", "🗃️ File Saya"])

    # Inisialisasi service GDrive
    # Ini akan diambil dari cache jika sudah ada
    gdrive_service = google_utils.init_gdrive_service()

    if page == "Home":
        st.title("Secure Digital Dropbox")
        st.write("Silakan pilih menu dari sidebar.")

    elif page == "Upload File":
        st.title("📤 Upload File Baru")
        uploaded_file = st.file_uploader("Pilih file untuk dienkripsi dan diupload")
        file_type = st.selectbox("Jenis File (Sesuai Kriteria TA):", 
                                 ["Pesan Teks (.txt)", 
                                  "Pesan Gambar (Steganografi)", 
                                  "File Lain (.pdf, .docx, dll)"])
        
        encrypt_password = st.text_input("Password untuk file ini", type="password", key="upload_pass")
        
        stegano_message = ""
        if file_type == "Pesan Gambar (Steganografi)":
            stegano_message = st.text_input("Pesan Teks yang akan disembunyikan dalam gambar")

        if st.button("Enkripsi & Upload"):
           if uploaded_file and encrypt_password:
                file_bytes = uploaded_file.getvalue()
                original_name = uploaded_file.name

                try:
                    # --- INI ADALAH LOGIKA KRITERIA ANDA ---
                    if file_type == "Pesan Teks (.txt)":
                        st.write("Mode: Super Enkripsi (RC4+Vigenere+Railway)")
                        with st.spinner("1/3: Menjalankan Super Enkripsi..."):
                            encrypted_bytes = crypto_utils.encrypt_super(file_bytes, encrypt_password)
                            crypto_tag = "SuperEncrypt"

                    elif file_type == "Pesan Gambar (Steganografi)":
                        st.write("Mode: Steganografi")
                        if not stegano_message:
                            st.error("Harap masukkan pesan rahasia untuk steganografi.")
                            return # Hentikan jika pesan kosong
                        
                        with st.spinner("1/3: Menerapkan steganografi..."):
                            
                            
                            # Ubah bytes gambar ke format PIL Image
                            img_io = io.BytesIO(file_bytes)
                            img = lsb.hide(img_io, stegano_message)
                            
                            # Simpan gambar baru ke memori
                            img_bytes_io = io.BytesIO()
                            img.save(img_bytes_io, format='PNG')
                            encrypted_bytes = img_bytes_io.getvalue() # Ini adalah file gambar .png baru
                            crypto_tag = "Steganography"
                    
                    else: # "File Lain"
                        st.write("Mode: Kriptografi Lain (ChaCha20)")
                        with st.spinner("1/3: Mengenkripsi file (ChaCha20)..."):
                            encrypted_bytes = crypto_utils.encrypt_file(file_bytes, encrypt_password)
                            crypto_tag = "ChaCha20"
                    
                    # --- Lanjutan proses upload (SAMA) ---
                    with st.spinner("2/3: Mengupload ke Google Drive..."):
                        unique_filename = f"{original_name}_{datetime.datetime.now().timestamp()}.enc"
                        gdrive_id = google_utils.upload_to_gdrive(gdrive_service, encrypted_bytes, unique_filename)
                    
                    if gdrive_id:
                        with st.spinner("3/3: Menyimpan metadata..."):
                            firebase_utils.log_file_to_firestore(
                                db, st.session_state['username'],
                                original_name, gdrive_id, crypto_tag # Simpan tag
                            )
                        st.success(f"File '{original_name}' berhasil disimpan!")
                    
                except Exception as e:
                    st.error(f"Proses gagal: {e}")

    elif page == "🗃️ File Saya":
        st.title("🗃️ File Saya")

        # 1. Ambil daftar file dari Firestore
        try:
            # Menggunakan st.session_state['username'] untuk mengambil file
            file_list = firebase_utils.get_user_files(db, st.session_state['username'])
        except Exception as e:
            st.error(f"Gagal mengambil daftar file: {e}")
            file_list = []

        if not file_list:
            st.info("Anda belum mengupload file apapun.")
        else:
            # 2. Tampilkan file dalam bentuk yang rapi
            st.write(f"Anda memiliki **{len(file_list)}** file tersimpan.")
            
            display_files = [
                {
                    "Nama File": f.get("original_filename", "N/A"),
                    "Tipe Enkripsi": f.get("encryption_type", "N/A"),
                    "Doc ID": f.get("doc_id", "N/A") # 'doc_id' dari Firestore
                }
                for f in file_list
            ]
            st.dataframe(display_files, use_container_width=True, hide_index=True)

            st.divider()

            # --- Bagian Download & Dekripsi ---
            st.subheader("⬇️ Download dan Dekripsi File")
            
            # Buat pilihan berdasarkan 'Nama File' dan 'Doc ID'
            file_options = {f"{file['Nama File']} (ID: ...{file['Doc ID'][-5:]})": file['Doc ID'] for file in display_files}
            selected_option = st.selectbox("Pilih file untuk di-download", file_options.keys())
            
            decrypt_password = st.text_input("Masukkan Password (jika diperlukan)", type="password", key="decrypt_pass")

            if st.button("Proses dan Download"):
                if selected_option:
                    # Ambil data file lengkap berdasarkan pilihan
                    doc_id = file_options[selected_option]
                    file_data = next(f for f in file_list if f.get("doc_id") == doc_id)
                    gdrive_id = file_data.get("gdrive_file_id")
                    crypto_tag = file_data.get("encryption_type")

                    try:
                        with st.spinner("1/2: Mengunduh file dari Google Drive..."):
                            encrypted_bytes = google_utils.download_from_gdrive(gdrive_service, gdrive_id)
                        
                        if encrypted_bytes is None:
                            raise Exception("File tidak ditemukan di Google Drive.")

                        with st.spinner("2/2: Memproses file..."):
                            # --- LOGIKA DEKRIPSI BERDASARKAN KRITERIA ---
                            if crypto_tag == "SuperEncrypt":
                                decrypted_bytes = crypto_utils.decrypt_super(encrypted_bytes, decrypt_password)
                            elif crypto_tag == "ChaCha20":
                                decrypted_bytes = crypto_utils.decrypt_file(encrypted_bytes, decrypt_password)
                            elif crypto_tag == "Steganography":
                                img_io = io.BytesIO(encrypted_bytes)
                                hidden_message = lsb.reveal(img_io)
                                if hidden_message:
                                    st.success(f"Pesan Tersembunyi Ditemukan: **{hidden_message}**")
                                else:
                                    st.warning("Tidak ada pesan tersembunyi di gambar ini.")
                                decrypted_bytes = encrypted_bytes # Berikan file gambarnya
                            else:
                                decrypted_bytes = encrypted_bytes # Tipe tidak diketahui

                        # Berikan tombol download
                        st.download_button(
                            label=f"Download '{file_data['original_filename']}'",
                            data=decrypted_bytes,
                            file_name=file_data['original_filename']
                        )
                        st.success("File berhasil diproses!")

                    except Exception as e:
                        # Ini akan menangkap error password salah
                        st.error(f"Gagal: Password salah atau file korup. ({e})")
                
                else:
                    st.warning("Harap pilih file.")
            
            st.divider()

            # --- Bagian Hapus File ---
            st.subheader("❌ Hapus File")
            st.warning("PERINGATAN: Tindakan ini tidak dapat dibatalkan.")
            
            delete_option = st.selectbox("Pilih file untuk dihapus", file_options.keys(), key="delete_select")
            
            if st.button("Hapus File Ini Secara Permanen", type="primary"):
                if delete_option:
                    doc_id = file_options[delete_option]
                    file_data = next(f for f in file_list if f.get("doc_id") == doc_id)
                    gdrive_id = file_data.get("gdrive_file_id")
                    
                    try:
                        with st.spinner("Menghapus file dari Google Drive dan Database..."):
                            # 1. Hapus dari GDrive
                            google_utils.delete_file_from_gdrive(gdrive_service, gdrive_id)
                            # 2. Hapus dari Firestore
                            firebase_utils.delete_file_from_firestore(db, st.session_state['username'], doc_id)
                        
                        st.success(f"File '{file_data['original_filename']}' telah dihapus.")
                        st.rerun() # Muat ulang halaman untuk memperbarui daftar file
                    except Exception as e:
                        st.error(f"Gagal menghapus file: {e}")