from __future__ import annotations
from uuid import uuid4
from .persistence.service import (
    create_conversation, get_conversation, list_conversations, add_message
)

async def new_conversation(db, user, title="محادثة جديدة"):
    cid = f"conv_{uuid4().hex}"
    workshop_id = getattr(user, "workshop_id", None)
    return await create_conversation(db, cid, user.id, title, workshop_id)

async def conversation_detail(db, user, conversation_id):
    return await get_conversation(
        db, user.id, conversation_id, getattr(user, "workshop_id", None)
    )

async def conversation_list(db, user):
    return await list_conversations(
        db, user.id, getattr(user, "workshop_id", None)
    )

async def append_user_message(db, user, conversation_id, content):
    return await add_message(
        db, user.id, conversation_id, "user", content,
        workshop_id=getattr(user, "workshop_id", None)
    )

async def append_assistant_message(db, user, conversation_id, content, metadata=None):
    return await add_message(
        db, user.id, conversation_id, "assistant", content, metadata=metadata,
        workshop_id=getattr(user, "workshop_id", None)
    )
