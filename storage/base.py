from abc import ABC, abstractmethod
from typing import Any

class BaseStorage(ABC):
    @abstractmethod
    def upload_email(self, data: bytes, filename: str) -> str:
        """
        Uploads an email to storage.
        
        Args:
            data: The raw bytes of the email.
            filename: The target filename (key).
            
        Returns:
            The storage key/path of the uploaded file.
        """
        pass
