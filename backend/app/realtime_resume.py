from __future__ import annotations
from .realtime_state import state

def key(session_id: str) -> str:
    return f"rt:events:{session_id}"

async def append(session_id: str, sequence: int, event: dict, ttl: int = 3600):
    data = await state.get(key(session_id)) or {"events": [], "last_sequence": 0}
    data["events"].append({"sequence": sequence, "event": event})
    data["last_sequence"] = max(data["last_sequence"], sequence)
    data["events"] = data["events"][-500:]
    await state.set(key(session_id), data, ttl=ttl)
    return sequence

async def after(session_id: str, sequence: int):
    data = await state.get(key(session_id)) or {"events": []}
    return [item for item in data["events"] if item["sequence"] > sequence]

async def last_sequence(session_id: str) -> int:
    data = await state.get(key(session_id)) or {"last_sequence": 0}
    return int(data.get("last_sequence", 0))
