from __future__ import annotations

from typing import Any

from .agent import all_tool_definitions, execute_agent_tool
from .conversation import add_message
from .realtime_session import create as create_realtime_session


SYSTEM_PROMPT = """
أنت مساعد صوتي عربي لمشروع M-One AI.
تحدث بالعربية بصورة طبيعية ومختصرة، واسأل سؤال توضيحي واحداً عند الحاجة.
لا تخترع بيانات العملاء أو المشاريع أو نتائج التصنيع.
عند الحاجة إلى بيانات M-One استخدم الأدوات.
لا تنفذ عملية حساسة أو مالية أو تغيير بيانات بدون تأكيد صريح.
عند تحليل صورة أثاث، لا تدّعِ دقة أبعاد لا يمكن استنتاجها؛ اذكر الافتراضات.
"""


def realtime_session_config(user_id: int, conversation_id: str) -> dict[str, Any]:
    session = create_realtime_session(user_id, conversation_id)
    return {
        "session_id": session.id,
        "conversation_id": conversation_id,
        "instructions": SYSTEM_PROMPT,
        "tools": all_tool_definitions(),
        "audio": {
            "input": {"format": "pcm16", "turn_detection": "server_vad"},
            "output": {"format": "pcm16"},
        },
        "turn_handling": {
            "barge_in": True,
            "interruptible": True,
        },
    }


async def handle_tool(
    user_id: int,
    conversation_id: str,
    name: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    result = await execute_agent_tool(name, arguments)
    add_message(
        user_id,
        conversation_id,
        "tool",
        str(result),
        tool_name=name,
    )
    return result
