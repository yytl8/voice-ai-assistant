from __future__ import annotations
import time
from collections import defaultdict
from .realtime_state import state

_memory = defaultdict(list)

async def allow(key: str, limit: int, window_seconds: int) -> bool:
    now = time.time()
    if state.redis:
        bucket = f"rl:{key}"
        current = await state.redis.incr(bucket)
        if current == 1:
            await state.redis.expire(bucket, window_seconds)
        return current <= limit

    values = [t for t in _memory[key] if t > now - window_seconds]
    if len(values) >= limit:
        _memory[key] = values
        return False
    values.append(now)
    _memory[key] = values
    return True
