import os
from datetime import timedelta
from typing import List, Optional

from google.cloud import storage

from .cloud_storage_base import CloudStorage

DEFAULT_EXPIRATION_MINUTES = 30


class GCPStorage(CloudStorage):
    """
    Google Cloud Storage implementation of CloudStorage interface.
    """

    def __init__(self, bucket_name: str = None):
        if not bucket_name:
            bucket_name = os.getenv("BUCKET_NAME", None)
            if not bucket_name:
                raise ValueError("BUCKET_NAME environment variable is not set.")

        self.bucket_name = bucket_name

        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name=bucket_name)

    def log(self, message: str) -> None:
        """
        Log messages to the console boldly
        """
        print(f"====== [STORAGE] {message} ======")

    def upload_file(self, local_path: str, remote_path: str) -> None:
        self.log("UPLOADING FILE")
        blob = self.bucket.blob(remote_path)
        blob.upload_from_filename(local_path)
        print(f"[#] Uploaded {local_path} to {remote_path}")
        self.log("UPLOAD COMPLETED")

    def download_file(self, remote_path: str, local_path: str) -> None:
        self.log("DOWNLOADING FILE")
        blob = self.bucket.blob(remote_path)
        if local_path.count("/") > 1:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
        blob.download_to_filename(local_path)
        print(f"[#] Downloaded {remote_path} to {local_path}")
        self.log("DOWNLOAD COMPLETED")

    def delete_file(self, remote_path: str) -> None:
        self.log("DELETING FILE")
        blob = self.bucket.blob(remote_path)
        blob.delete()
        print(f"[#] Deleted {remote_path}")
        self.log("DELETE COMPLETED")

    def list_files(self, prefix: Optional[str] = None) -> List[str]:
        self.log("LISTING FILES")
        blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)
        self.log("LISTING FILES COMPLETED")
        return [blob.name for blob in blobs]

    def get_file_url(self, remote_path):
        blob = self.bucket.blob(remote_path)
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=DEFAULT_EXPIRATION_MINUTES),
            method="GET",
        )
        return url
