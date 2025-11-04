# src/google_utils.py
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import os
import json

# Scope ini HARUS SAMA dengan yang ada di generate_token.py
SCOPES = ['https://www.googleapis.com/auth/drive']

# ID Folder GDrive Anda (dari langkah sebelumnya)
GDRIVE_FOLDER_ID = "1_zseYdyiQFYh3PjkINm8-edDx1DwOmCh" # <-- GANTI DENGAN ID FOLDER ANDA

def get_gdrive_credentials():
    """Memuat kredensial dari st.secrets atau file lokal (token.json)."""
    creds = None
    
    # --- Blok 1: Coba dari Streamlit Secrets (Untuk Deployment) ---
    try:
        # Kita perlu DUA secrets sekarang: token dan client_secret
        token_json_str = st.secrets["GDRIVE_TOKEN_JSON"]
        client_secret_json_str = st.secrets["GDRIVE_CLIENT_SECRET_JSON"]
        
        token_dict = json.loads(token_json_str)
        creds = Credentials.from_authorized_user_info(token_dict, SCOPES)
        
    # --- Blok 2: Coba dari File Lokal (Untuk Testing) ---
    except: 
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Jika tidak ada kredensial, atau sudah kedaluwarsa, refresh
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Kredensial sudah ada tapi kedaluwarsa, kita refresh
            client_secret_dict = {}
            try:
                creds.refresh(Request())
            except Exception as e:
                st.error(f"Gagal me-refresh token GDrive: {e}")
                st.error("Jalankan ulang 'generate_token.py' secara manual.")
                return None        
        else:
            # Ini seharusnya tidak terjadi di app utama, hanya di generate_token.py
            st.error("Tidak ada token.json. Jalankan generate_token.py terlebih dahulu.")
            return None
        
        # Simpan token yang baru di-refresh (jika berjalan lokal)
        # Di Streamlit Cloud, ini tidak akan tersimpan permanen, tapi tidak apa-apa
        try:
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        except:
            pass # Gagal menulis file di server (diharapkan)

    return creds

@st.cache_resource
def init_gdrive_service():
    """Menginisialisasi dan mengembalikan service Google Drive."""
    creds = get_gdrive_credentials()
    if creds is None:
        return None
    service = build('drive', 'v3', credentials=creds)
    return service

# --- Fungsi Upload, Download, Delete (TIDAK BERUBAH) ---

def upload_to_gdrive(service, file_bytes, filename_in_drive):
    """Mengunggah file (dalam bytes) ke folder GDrive Anda."""
    try:
        file_metadata = {
            'name': filename_in_drive,
            'parents': [GDRIVE_FOLDER_ID] 
        }
        fh = io.BytesIO(file_bytes)
        media = MediaIoBaseUpload(fh, mimetype='application/octet-stream', resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return file.get('id')
    except Exception as e:
        st.error(f"Error saat mengupload ke GDrive: {e}")
        return None

def download_from_gdrive(service, gdrive_file_id):
    """Mengunduh file dari GDrive berdasarkan ID-nya. Mengembalikan bytes."""
    try:
        # 1. Buat permintaan (request) untuk mendapatkan media
        request = service.files().get_media(fileId=gdrive_file_id)
        
        # 2. Eksekusi permintaan. Ini akan MENGEMBALIKAN bytes.
        #    Hapus 'fh' dari sini.
        downloaded_bytes = request.execute()
        
        # 3. Kembalikan bytes yang sudah diunduh
        return downloaded_bytes
        
    except Exception as e:
        st.error(f"Error saat mengunduh dari GDrive: {e}")
        return None

def delete_file_from_gdrive(service, file_id):
    """Menghapus file secara permanen dari Google Drive."""
    try:
        service.files().delete(fileId=file_id).execute()
        return True
    except Exception as e:
        if "notFound" in str(e):
            return True
        st.error(f"Error menghapus dari GDrive: {e}")
        return False