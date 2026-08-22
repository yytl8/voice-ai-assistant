from __future__ import annotations
import base64
from pathlib import Path
from .settings import settings

ALLOWED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}

class AttachmentStorage:
    def __init__(self):
        self.root = Path(settings.attachment_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    async def put_base64(self, attachment_id: str, data_base64: str, suffix: str) -> str:
        suffix = suffix.lower()
        if suffix not in ALLOWED_SUFFIXES:
            raise ValueError("Unsupported attachment type")
        raw = base64.b64decode(data_base64, validate=True)
        path = self.root / f"{attachment_id}{suffix}"
        path.write_bytes(raw)
        return str(path)

    async def delete(self, object_key: str) -> None:
        path = Path(object_key)
        if path.exists() and self.root in path.parents:
            path.unlink()

storage = AttachmentStorage()
