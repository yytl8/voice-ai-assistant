from __future__ import annotations

import time
from collections import defaultdict

from fastapi import HTTPException, Request

from .realtime_state import state
from .settings import settings

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


async def rate_limit(request: Request) -> None:
    """Global per-client request rate limiter used by the request middleware."""
    forwarded_for = request.headers.get("x-forwarded-for")

    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    elif request.client:
        client_ip = request.client.host
    else:
        client_ip = "unknown"

    key = f"ip:{client_ip}"

    if not await allow(key, settings.rate_limit_per_minute, 60):
        raise HTTPException(status_code=429, detail="Too many requests")
