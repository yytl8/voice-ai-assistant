from dataclasses import dataclass
from datetime import datetime, timezone
import secrets


@dataclass
class Confirmation:
    token: str
    user_id: int
    action: str
    expires_at: datetime


_pending: dict[str, Confirmation] = {}


def create(user_id: int, action: str, ttl_seconds: int = 120) -> Confirmation:
    from datetime import timedelta
    c = Confirmation(
        token=secrets.token_urlsafe(24),
        user_id=user_id,
        action=action,
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds),
    )
    _pending[c.token] = c
    return c


def consume(user_id: int, token: str, action: str) -> bool:
    c = _pending.pop(token, None)
    if not c or c.user_id != user_id or c.action != action:
        return False
    return datetime.now(timezone.utc) <= c.expires_at
