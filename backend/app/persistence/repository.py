from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from .models import ConversationRow, ConversationMessageRow, RealtimeSessionRow, AuditEventRow

async def create_conversation(db, conversation_id, user_id, title, workshop_id=None):
    row = ConversationRow(id=conversation_id, user_id=user_id, title=title)
    if hasattr(row, "workshop_id"):
        row.workshop_id = workshop_id
    db.add(row)
    await db.commit()
    return row

async def get_conversation(db, user_id, conversation_id, workshop_id=None):
    query = select(ConversationRow).options(selectinload(ConversationRow.messages)).where(
        ConversationRow.id == conversation_id,
        ConversationRow.user_id == user_id,
    )
    if workshop_id is not None and hasattr(ConversationRow, "workshop_id"):
        query = query.where(ConversationRow.workshop_id == workshop_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def list_conversations(db, user_id, workshop_id=None):
    query = select(ConversationRow).where(ConversationRow.user_id == user_id)
    if workshop_id is not None and hasattr(ConversationRow, "workshop_id"):
        query = query.where(ConversationRow.workshop_id == workshop_id)
    result = await db.execute(query.order_by(ConversationRow.updated_at.desc()))
    return list(result.scalars())

async def add_message(db, user_id, conversation_id, role, content, tool_name=None, metadata=None, workshop_id=None):
    conversation = await get_conversation(db, user_id, conversation_id, workshop_id)
    if not conversation:
        return None
    row = ConversationMessageRow(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_name=tool_name,
        metadata_json=metadata or {},
    )
    db.add(row)
    conversation.updated_at = datetime.now(timezone.utc)
    if conversation.title == "محادثة جديدة" and role == "user":
        conversation.title = content[:60] or conversation.title
    await db.commit()
    return row

async def create_realtime_session(db, session_id, user_id, conversation_id, provider_session_id=None, metadata=None):
    row = RealtimeSessionRow(
        id=session_id, user_id=user_id, conversation_id=conversation_id,
        provider_session_id=provider_session_id, metadata_json=metadata or {}
    )
    db.add(row)
    await db.commit()
    return row

async def close_realtime_session(db, user_id, session_id):
    result = await db.execute(select(RealtimeSessionRow).where(
        RealtimeSessionRow.id == session_id,
        RealtimeSessionRow.user_id == user_id,
        RealtimeSessionRow.status == "active",
    ))
    row = result.scalar_one_or_none()
    if not row:
        return False
    row.status = "closed"
    row.closed_at = datetime.now(timezone.utc)
    await db.commit()
    return True

async def audit(db, user_id, event_type, conversation_id=None, tool_name=None, metadata=None):
    row = AuditEventRow(
        user_id=user_id, conversation_id=conversation_id,
        event_type=event_type, tool_name=tool_name, metadata_json=metadata or {}
    )
    db.add(row)
    await db.commit()
    return row
