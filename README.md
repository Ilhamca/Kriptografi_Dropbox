# Kriptografi — Streamlit Demo

A crypto-dropbox based system utilizing firebase database and google drive.

Requires 3 credential files:


How to install:
Step 1: 3 .JSON files


credentials.json

    * Open google cloud console, and make a new project.
    
    * Activate Firestore API
    
    * Create Service Account with Editor role
    
    * Download .JSON key and change the name to credentials.json


client_secret.json
    
    * With same google cloud project, activate Google Drive API
    
    * Open Credentials -> Create Credetials -> OAuth client ID"
    
    * Choose "Desktop app".
    
    * Download .JSON file and change the name into client_secret.json


token.json

    * Run generate_token.py, and sign in with account the project


Step 2: Google Drive Folder

    * Open google drive folder, and create a new folder with any names

    * Share the folder to either bot email from credentials.json or account that you choose to run in token.json


Step 3: Installation
    * Install all library in requirement.txt


Step 4: Run Application
    * run with command streamlit run main.py

