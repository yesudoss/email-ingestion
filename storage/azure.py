from storage.base import BaseStorage

class AzureStorage(BaseStorage):
    def upload_email(self, data: bytes, filename: str) -> str:
        raise NotImplementedError("Azure storage is not yet implemented.")
