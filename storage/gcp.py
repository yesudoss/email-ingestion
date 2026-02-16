from storage.base import BaseStorage

class GCPStorage(BaseStorage):
    def upload_email(self, data: bytes, filename: str) -> str:
        raise NotImplementedError("GCP storage is not yet implemented.")
