import os
import time
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# === CONFIG ===
dir = r"C:\Users\reich\Documents\GIT\katie\google_apis_test"
SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDENTIALS_FILE = os.path.join(dir, 'credentials.json') 
TOKEN_FILE = os.path.join(dir, 'token.json')
HTML_FILENAME = os.path.join(dir, 'example.html') 
WAIT_BEFORE_UPDATE = 0  # seconds
FOLDER_ID = '1Gc7hAc3y0yd3KJ3PTI0RCAD-1ynOeOmE'

# === STEP 1: AUTH FLOW ===
creds = None
if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())

# === STEP 2: DRIVE SERVICE ===
service = build('drive', 'v3', credentials=creds)

# === STEP 3: UPLOAD HTML FILE AND CONVERT TO GOOGLE DOC ===
now_str = datetime.now().strftime('%Y-%m-%d %H-%M')
file_metadata = {
    'name': f'My Upload: {now_str}',
    'mimeType': 'application/vnd.google-apps.document',
    'parents': [FOLDER_ID]
}
media = MediaFileUpload(HTML_FILENAME, mimetype='text/html')
uploaded_file = service.files().create(
    body=file_metadata,
    media_body=media,
    fields='id, name',
    supportsAllDrives=True
).execute()

file_id = uploaded_file['id']
print(f"Uploaded and converted file: {uploaded_file['name']} (ID: {file_id})")

# === STEP 4: WAIT BEFORE UPDATE ===
print(f"Waiting {WAIT_BEFORE_UPDATE} seconds...")
time.sleep(WAIT_BEFORE_UPDATE)

# === STEP 5: UPDATE METADATA ===
updated_metadata = {'name': f'My Upload: {now_str} - Updated'}
updated_file = service.files().update(
    fileId=file_id,
    body=updated_metadata,
    supportsAllDrives=True
).execute()
print(f"Updated file name: {updated_file['name']}")
