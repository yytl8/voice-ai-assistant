from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import secrets


@dataclass
class RealtimeSession:
    id: str
    user_id: int
    conversation_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    active: bool = True
    metadata: dict = field(default_factory=dict)


_sessions: dict[str, RealtimeSession] = {}


def create(user_id: int, conversation_id: str, metadata: dict | None = None) -> RealtimeSession:
    sid = "rt_" + secrets.token_urlsafe(18)
    item = RealtimeSession(
        id=sid,
        user_id=user_id,
        conversation_id=conversation_id,
        metadata=metadata or {},
    )
    _sessions[sid] = item
    return item


def get(user_id: int, session_id: str) -> RealtimeSession | None:
    item = _sessions.get(session_id)
    if not item or item.user_id != user_id or not item.active:
        return None
    return item


def close(user_id: int, session_id: str) -> bool:
    item = get(user_id, session_id)
    if not item:
        return False
    item.active = False
    return True
