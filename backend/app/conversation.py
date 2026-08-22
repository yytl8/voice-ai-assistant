from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import secrets


@dataclass
class Conversation:
    id: str
    user_id: int
    title: str = "محادثة جديدة"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    messages: list[dict[str, Any]] = field(default_factory=list)


_conversations: dict[str, Conversation] = {}


def create(user_id: int, title: str = "محادثة جديدة") -> Conversation:
    cid = "conv_" + secrets.token_urlsafe(16)
    item = Conversation(id=cid, user_id=user_id, title=title)
    _conversations[cid] = item
    return item


def get(user_id: int, conversation_id: str) -> Conversation | None:
    item = _conversations.get(conversation_id)
    if not item or item.user_id != user_id:
        return None
    return item


def add_message(
    user_id: int,
    conversation_id: str,
    role: str,
    content: str,
    *,
    tool_name: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Conversation:
    item = get(user_id, conversation_id)
    if not item:
        raise KeyError("conversation_not_found")

    item.messages.append({
        "role": role,
        "content": content,
        "tool_name": tool_name,
        "metadata": metadata or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    item.updated_at = datetime.now(timezone.utc)
    if item.title == "محادثة جديدة" and role == "user":
        item.title = content[:60] or item.title
    return item


def list_for_user(user_id: int) -> list[Conversation]:
    return sorted(
        (x for x in _conversations.values() if x.user_id == user_id),
        key=lambda x: x.updated_at,
        reverse=True,
    )
