# generate_token.py
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scope ini memberikan izin penuh ke Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    creds = None
    # File token.json menyimpan token akses dan refresh pengguna.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Jika tidak ada kredensial (valid) yang tersedia, biarkan pengguna login.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Muat client_secret.json
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            # Jalankan server lokal untuk menangani alur otentikasi
            creds = flow.run_local_server(port=0)
        
        # Simpan kredensial untuk proses berikutnya
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    print("File 'token.json' berhasil dibuat!")
    print("Anda sekarang dapat menutup tab browser dan menjalankan aplikasi Streamlit utama Anda.")

if __name__ == '__main__':
    main()