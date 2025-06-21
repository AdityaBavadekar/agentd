import os
from datetime import timedelta
from typing import List, Optional

from .cloud_storage_base import CloudStorage

DEFAULT_EXPIRATION_MINUTES = 30


class GCPStorage(CloudStorage):
    """
    Google Cloud Storage implementation of CloudStorage interface.
    """

    def __init__(self, bucket_name: str = None):
        if not bucket_name:
            BUCKET_NAME = os.getenv("BUCKET_NAME", None)
            if not BUCKET_NAME:
                raise ValueError("BUCKET_NAME environment variable is not set.")
            bucket_name = BUCKET_NAME

        from google.cloud import storage

        self.bucket_name = bucket_name

        # Validate environment variable for Google Cloud credentials
        if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            raise ValueError(
                "Environment variable 'GOOGLE_APPLICATION_CREDENTIALS' must be set."
            )

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


if __name__ == "__main__":
    import datetime

    CLOUD_STORAGE_BUCKET_NAME = "agentd_store1"
    gcp_storage = GCPStorage(bucket_name=CLOUD_STORAGE_BUCKET_NAME)

    # TESTING

    # ====== LIST FILES ======
    # List files in the bucket
    files = gcp_storage.list_files()
    print("======= LIST FILES ======")
    print(f"Files in bucket '{CLOUD_STORAGE_BUCKET_NAME}': {files}")
    print("=========================")

    # ====== UPLOAD FILE ======
    # Upload a file to the bucket
    local_file_path = "test_upload.txt"
    remote_file_path = "test_upload.txt"
    with open(local_file_path, "w") as f:
        f.write(
            "This is a test upload file, uploaded at " + str(datetime.datetime.now())
        )
    print("======= UPLOAD FILE ======")
    gcp_storage.upload_file(local_path=local_file_path, remote_path=remote_file_path)
    print(f"Uploaded {local_file_path} to {remote_file_path}")
    print("=========================")

    # Get a public URL for the file
    print("======= GET FILE URL ======")
    public_url = gcp_storage.get_file_url(remote_file_path)
    print(f"Public URL for the file: {public_url}")
    print("=========================")

    # # Re-list files to confirm upload
    print("======= LIST FILES ======")
    files_after_upload = gcp_storage.list_files()
    print(
        f"Files in bucket '{CLOUD_STORAGE_BUCKET_NAME}' after upload: {files_after_upload}"
    )
    print("=========================")

    # ====== DOWNLOAD FILE ======
    # Download the file from the bucket
    remote_download_path = remote_file_path
    local_download_path = "test_download.txt"
    print("======= DOWNLOAD FILE ======")
    gcp_storage.download_file(
        remote_path=remote_download_path, local_path=local_download_path
    )
    print(f"Downloaded {remote_download_path} to {local_download_path}")
    print("=========================")

    # # ====== DELETE FILE ======
    # # Delete the file from the bucket
    print("======= DELETE FILE ======")
    gcp_storage.delete_file(remote_path=remote_file_path)
    print(f"Deleted {remote_file_path}")
    print("=========================")

    # # Re-list files to confirm deletion
    files_after_deletion = gcp_storage.list_files()
    print("Files after deletion:", files_after_deletion)
    print("=========================")
