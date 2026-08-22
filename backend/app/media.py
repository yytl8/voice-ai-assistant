from __future__ import annotations

import base64
import binascii
import secrets


ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
MAX_IMAGE_BYTES = 12 * 1024 * 1024


def validate_image(data_base64: str, content_type: str) -> dict:
    if content_type not in ALLOWED_TYPES:
        raise ValueError("Unsupported image type")

    try:
        raw = base64.b64decode(data_base64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Invalid base64 image") from exc

    if not raw or len(raw) > MAX_IMAGE_BYTES:
        raise ValueError("Image exceeds the 12 MB limit")

    return {
        "attachment_id": "att_" + secrets.token_urlsafe(12),
        "content_type": content_type,
        "size_bytes": len(raw),
        "image_base64": data_base64,
    }
