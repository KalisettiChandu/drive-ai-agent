from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import json

SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "../credentials.json")

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

load_dotenv()


def _load_credentials():
    sa_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if sa_json:
        info = json.loads(sa_json)
        return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)

    return service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
    )


creds = _load_credentials()

service = build("drive", "v3", credentials=creds)


def search_drive(query):
    folder_id = os.getenv("DRIVE_FOLDER_ID")

    q = (query or "").strip()
    if not q:
        q = "trashed=false"
    if "trashed=" not in q:
        q = f"({q}) and trashed=false"
    if folder_id:
        q = f"({q}) and '{folder_id}' in parents"

    results = service.files().list(
        q=q,
        fields="files(id, name, mimeType, webViewLink)"
    ).execute()

    return results.get("files", [])