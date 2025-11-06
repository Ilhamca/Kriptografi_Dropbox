# generate_token.py
import os
import json
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
            if not os.path.exists('client_secret.json'):
                print("❌ File 'client_secret.json' tidak ditemukan!")
                print("📥 Download dari Google Cloud Console → APIs & Services → Credentials")
                return
            
            # Muat client_secret.json
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            # Jalankan server lokal untuk menangani alur otentikasi
            creds = flow.run_local_server(port=0)
        
        # Simpan kredensial untuk proses berikutnya
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    print("✅ File 'token.json' berhasil dibuat!")
    
    # Generate format .env
    token_dict = json.loads(creds.to_json())
    print("\n📋 Copy baris ini ke file .env Anda:")
    print(f"GDRIVE_TOKEN_JSON='{json.dumps(token_dict)}'")
    
    print("\n💡 Untuk Streamlit Cloud, tambahkan ke Secrets dengan format:")
    print('GDRIVE_TOKEN_JSON = """')
    print(json.dumps(token_dict, indent=2))
    print('"""')

if __name__ == '__main__':
    main()