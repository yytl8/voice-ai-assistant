from sqlalchemy import text
async def check_database(db):
    await db.execute(text("SELECT 1")); return True
async def check_redis(state):
    if not state.redis: return {"ok":True,"mode":"memory-fallback"}
    await state.redis.ping(); return {"ok":True,"mode":"redis"}
