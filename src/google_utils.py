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
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Scope ini HARUS SAMA dengan yang ada di generate_token.py
SCOPES = ['https://www.googleapis.com/auth/drive']

# ID Folder GDrive Anda (dari langkah sebelumnya)
GDRIVE_FOLDER_ID = "1_zseYdyiQFYh3PjkINm8-edDx1DwOmCh" # <-- GANTI DENGAN ID FOLDER ANDA

def get_gdrive_credentials():
    """Memuat kredensial dari st.secrets atau environment variable."""
    creds = None
    
    # PRIORITAS 1: Streamlit Secrets (untuk Cloud)
    try:
        if "GDRIVE_TOKEN_JSON" in st.secrets:
            token_json_str = st.secrets["GDRIVE_TOKEN_JSON"]
            token_dict = json.loads(token_json_str) if isinstance(token_json_str, str) else token_json_str
            creds = Credentials.from_authorized_user_info(token_dict, SCOPES)
    except Exception:
        pass  # Secrets tidak tersedia, lanjut ke prioritas berikutnya
    
    # PRIORITAS 2: Environment Variable (untuk lokal .env)
    if creds is None and os.getenv("GDRIVE_TOKEN_JSON"):
        try:
            token_json_str = os.getenv("GDRIVE_TOKEN_JSON")
            token_dict = json.loads(token_json_str)
            creds = Credentials.from_authorized_user_info(token_dict, SCOPES)
        except Exception as e:
            st.error(f"❌ Error parsing .env GDrive token: {e}")
            return None
    
    # PRIORITAS 3: File lokal (backwards compatibility)
    if creds is None and os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception as e:
            st.error(f"❌ Error loading token.json: {e}")
            return None
    
    # Jika tidak ada kredensial
    if creds is None:
        st.error("❌ Google Drive credentials tidak ditemukan!")
        st.info("💡 Jalankan `python src/generate_token.py` untuk membuat token baru, lalu tambahkan ke .env")
        return None
    
    # Refresh jika expired
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            st.success("✅ Token berhasil di-refresh")
        except Exception as e:
            st.error(f"❌ Gagal refresh token: {e}")
            return None
    
    # Validasi final
    if not creds.valid:
        st.error("❌ Google Drive credentials tidak valid!")
        st.info("💡 Jalankan `python src/generate_token.py` untuk membuat token baru")
        return None
    
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