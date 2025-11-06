# Setup Guide - Secure Digital Dropbox

## Untuk Development Lokal

### 1. Clone Repository
```bash
git clone https://github.com/Ilhamca/Kriptografi_Dropbox.git
cd Kriptografi_Dropbox
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Firebase Credentials

1. Buka [Firebase Console](https://console.firebase.google.com/)
2. Pilih project Anda
3. Project Settings → Service Accounts → Generate New Private Key
4. Download file JSON tersebut
5. Copy seluruh isi file JSON (format sebagai satu baris)

### 4. Setup Google Drive API

1. Buka [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Google Drive API
3. Credentials → Create Credentials → OAuth 2.0 Client ID
4. Download `client_secret.json` dan simpan di root project
5. Jalankan script untuk generate token:
```bash
python src/generate_token.py
```
6. Browser akan terbuka, login dengan Google account Anda
7. Script akan membuat `token.json` dan menampilkan format untuk .env

### 5. Buat File .env

1. Copy file `.env.example` menjadi `.env`:
```bash
copy .env.example .env
```

2. Edit file `.env` dan isi dengan credentials Anda:
```
FIREBASE_CREDENTIALS={"type":"service_account","project_id":"...","private_key":"..."}
GDRIVE_TOKEN_JSON={"token":"...","refresh_token":"..."}
```

### 6. Jalankan Aplikasi
```bash
streamlit run main.py
```

---

## Untuk Deploy ke Streamlit Cloud

### 1. Push ke GitHub
Pastikan `.env`, `token.json`, `client_secret.json`, dan `credentials.json` **TIDAK** ter-commit (sudah ada di `.gitignore`)

### 2. Deploy di Streamlit Cloud
1. Buka [share.streamlit.io](https://share.streamlit.io)
2. Connect repository GitHub Anda
3. Pilih branch: `main`
4. Main file path: `main.py`

### 3. Tambahkan Secrets
Di Streamlit Cloud dashboard → Settings → Secrets, tambahkan:

```toml
FIREBASE_CREDENTIALS = """
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
"""

GDRIVE_TOKEN_JSON = """
{
  "token": "...",
  "refresh_token": "...",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "...",
  "client_secret": "...",
  "scopes": ["https://www.googleapis.com/auth/drive"]
}
"""
```

### 4. Save & Deploy
Klik "Save" dan aplikasi akan restart dengan secrets yang baru.

---

## Troubleshooting

### Error: "Firebase credentials tidak ditemukan"
- Pastikan `FIREBASE_CREDENTIALS` ada di `.env` (lokal) atau Streamlit Secrets (cloud)
- Pastikan format JSON valid (tanpa newline di dalam string kecuali di private_key)

### Error: "Google Drive credentials tidak valid"
- Jalankan ulang `python src/generate_token.py`
- Copy output ke `.env` atau Streamlit Secrets
- Pastikan format JSON valid

### Token expired
- Script akan otomatis refresh token jika refresh_token tersedia
- Jika gagal, generate ulang dengan `python src/generate_token.py`

---

## File Structure
```
Kriptografi_Dropbox/
├── .env                    # Credentials lokal (JANGAN commit!)
├── .env.example           # Template untuk .env
├── .gitignore             # File yang diabaikan git
├── requirements.txt       # Dependencies Python
├── main.py               # Entry point aplikasi
├── SETUP.md              # Guide ini
└── src/
    ├── firebase_utils.py  # Firebase operations
    ├── google_utils.py    # Google Drive operations
    ├── crypto_utils.py    # Encryption/decryption
    ├── generate_token.py  # Script generate Google token
    └── app/
        ├── login.py
        ├── registration.py
        └── dashboard.py
```

---

## Security Notes

⚠️ **PENTING:**
- Jangan pernah commit `.env`, `token.json`, `client_secret.json`, atau `credentials.json` ke git
- Jangan share credentials di public
- Gunakan secrets management untuk production (Streamlit Cloud Secrets, AWS Secrets Manager, etc)
- Rotate credentials secara berkala

---

## Support

Jika ada masalah, buka issue di [GitHub](https://github.com/Ilhamca/Kriptografi_Dropbox/issues)
