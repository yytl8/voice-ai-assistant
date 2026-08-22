from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Memory


async def get_memories_for_user(db: AsyncSession, user_id: int) -> list[dict[str, str]]:
    rows = (
        await db.scalars(
            select(Memory).where(Memory.user_id == user_id).order_by(Memory.updated_at.desc()).limit(30)
        )
    ).all()
    return [{"key": x.key, "value": x.value} for x in rows]


async def save_memory_for_user(db: AsyncSession, user_id: int, key: str, value: str) -> None:
    row = await db.scalar(select(Memory).where(Memory.user_id == user_id, Memory.key == key))
    if row:
        row.value = value
    else:
        db.add(Memory(user_id=user_id, key=key, value=value))


async def delete_memory_for_user(db: AsyncSession, user_id: int, key: str) -> None:
    await db.execute(delete(Memory).where(Memory.user_id == user_id, Memory.key == key))
