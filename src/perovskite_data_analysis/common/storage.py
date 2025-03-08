import io
import os
import pandas as pd
from abc import abstractmethod, ABC
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload, MediaIoBaseUpload


class FileStorage(ABC):
    @abstractmethod
    def download_file(self, filepath: str) -> bytes:
        pass

    @abstractmethod
    def upload_file(self, filepath: str) -> bytes:
        pass

    @abstractmethod
    def verify_existence(self, filepath: str) -> bool:
        pass

    @abstractmethod
    def download_dataframe(self, filepath: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def upload_dataframe(self, dataframe: pd.DataFrame, filepath: str, file_format: str) -> pd.DataFrame:
        pass


class GoogleDriveStorage(FileStorage):
    def __init__(self,
                 credentials: Credentials, ):
        self._credentials = credentials
        self._service = build('drive', 'v3', credentials=self._credentials)

    def download_file(self, filepath: str) -> bytes:
        file_id = self._get_file_id_by_path(filepath)
        if not file_id:
            raise FileNotFoundError(f"File '{filepath}' not found on Google Drive.")

        request = self._service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.seek(0)
        return fh.read()

    def upload_file(self, filepath: str) -> bytes:
        filename = os.path.basename(filepath)
        file_metadata = {'name': filename}
        media = MediaFileUpload(filepath, resumable=True)
        file = self._service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        file_id = file.get('id')
        return file_id.encode()

    def verify_existence(self, filepath: str) -> bool:
        file_id = self._get_file_id_by_path(filepath)
        return file_id is not None

    def download_dataframe(self, filepath: str) -> pd.DataFrame:
        file_bytes = self.download_file(filepath)
        ext = os.path.splitext(filepath)[1].lstrip('.').lower()
        file_format = ext

        if file_format == 'csv':
            df = pd.read_csv(io.BytesIO(file_bytes))
        elif file_format in ['xlsx', 'xls']:
            df = pd.read_excel(io.BytesIO(file_bytes))
        elif file_format == 'parquet':
            df = pd.read_parquet(io.BytesIO(file_bytes))
        else:
            raise ValueError("Unsupported file format. Use 'csv', 'xlsx', or 'parquet'.")
        return df

    # noinspection PyTypeChecker
    def upload_dataframe(self, dataframe: pd.DataFrame, filepath: str, file_format: str) -> str:
        filename = os.path.basename(filepath)
        if file_format.lower() == 'csv':
            buffer = io.StringIO()
            dataframe.to_csv(buffer, index=False)
            content = buffer.getvalue().encode('utf-8')
            mime_type = 'text/csv'
        elif file_format.lower() in ['xlsx', 'xls']:
            buffer = io.BytesIO()
            dataframe.to_excel(buffer, index=False, engine='openpyxl')
            content = buffer.getvalue()
            mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif file_format.lower() == 'parquet':
            buffer = io.BytesIO()
            dataframe.to_parquet(buffer, index=False)
            content = buffer.getvalue()
            mime_type = 'application/octet-stream'
        else:
            raise ValueError("Unsupported file format. Use 'csv', 'xlsx', or 'parquet'.")

        file_metadata = {'name': filename}
        file_buffer = io.BytesIO(content)
        media = MediaIoBaseUpload(file_buffer, mimetype=mime_type, resumable=True)
        file = self._service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        return file.get('id')

    def _get_file_id_by_path(self, filepath: str) -> str | None:
        # parts = filepath.strip('/').split('/')
        # parent_id = 'root'
        # for folder in parts[:-1]:
        #     folder_content =
        # TODO implement file id retirement by depth to folders CHECK if is single file
        raise NotImplementedError()

