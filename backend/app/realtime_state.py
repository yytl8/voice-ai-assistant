import json
from ..settings import settings
try:
    from redis.asyncio import Redis
except Exception:
    Redis = None

class RealtimeState:
    def __init__(self):
        self.redis = Redis.from_url(settings.redis_url, decode_responses=True) if Redis and settings.redis_url else None
        self.memory = {}

    async def set(self, key, value, ttl=3600):
        if self.redis:
            await self.redis.set(key, json.dumps(value), ex=ttl)
        else:
            self.memory[key] = value

    async def get(self, key):
        if self.redis:
            raw = await self.redis.get(key)
            return json.loads(raw) if raw else None
        return self.memory.get(key)

    async def delete(self, key):
        if self.redis:
            await self.redis.delete(key)
        else:
            self.memory.pop(key, None)

state = RealtimeState()
