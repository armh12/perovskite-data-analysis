import os

from dotenv import load_dotenv
from google.oauth2 import service_account

load_dotenv()

def google_credentials() -> service_account.Credentials:
    json_credentials_path = os.environ.get("GOOGLE_CREDENTIALS_PATH")
    credentials = service_account.Credentials.from_service_account_file(
        json_credentials_path,
        scopes=['https://www.googleapis.com/auth/drive'],
    )
    return credentials
