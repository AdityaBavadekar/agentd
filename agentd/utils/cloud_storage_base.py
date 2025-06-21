from abc import ABC, abstractmethod
from typing import List, Optional

import dotenv

dotenv.load_dotenv()


class CloudStorage(ABC):
    """
    Abstract base class for cloud storage services.
    """

    @abstractmethod
    def upload_file(self, local_path: str, remote_path: str) -> None:
        """
        Upload a file to cloud storage.

        Args:
            local_path: Local file path.
            remote_path: Destination path in cloud.
        """
        pass

    @abstractmethod
    def download_file(self, remote_path: str, local_path: str) -> None:
        """
        Download a file from cloud storage.

        Args:
            remote_path: Path in cloud.
            local_path: Destination local file path.
        """
        pass

    @abstractmethod
    def delete_file(self, remote_path: str) -> None:
        """
        Delete a file from cloud storage.

        Args:
            remote_path: Path in cloud.
        """
        pass

    @abstractmethod
    def list_files(self, prefix: Optional[str] = None) -> List[str]:
        """
        List files in cloud storage.

        Args:
            prefix: Optional prefix to filter files.
        Returns:
            List of file paths.
        """
        pass

    @abstractmethod
    def get_file_url(self, remote_path: str) -> str:
        """
        Get the public URL of a file in cloud storage.

        Args:
            remote_path: Path in cloud.
        Returns:
            Public URL of the file.
        """
        pass
