from __future__ import annotations
import secrets
from .realtime_state import state

async def issue(session_id: str, tool_name: str, arguments: dict, ttl: int = 120) -> str:
    token = secrets.token_urlsafe(24)
    await state.set(
        f"confirm:{token}",
        {"session_id": session_id, "tool_name": tool_name, "arguments": arguments},
        ttl=ttl,
    )
    return token

async def consume(token: str, session_id: str, tool_name: str):
    key = f"confirm:{token}"
    value = await state.get(key)
    if not value or value["session_id"] != session_id or value["tool_name"] != tool_name:
        return None
    await state.delete(key)
    return value
