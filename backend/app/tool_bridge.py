from __future__ import annotations
import json
from .security.rbac import can_use_tool
from .security.policy import requires_confirmation, sanitize_audit_arguments
from .realtime_events import tool_result
from .realtime_resume import append

async def dispatch_tool_event(*, session_id, user_id, conversation_id, role, event, execute):
    name = event.get("tool_name") or event.get("name")
    call_id = event.get("event_id") or event.get("call_id")
    arguments = event.get("arguments") or {}
    if isinstance(arguments, str):
        arguments = json.loads(arguments)

    if not can_use_tool(role, name):
        result = {"error": "tool_not_permitted", "tool_name": name}
    elif requires_confirmation(name, arguments):
        result = {
            "requires_confirmation": True,
            "tool_name": name,
            "arguments": sanitize_audit_arguments(arguments),
            "message": "تحتاج هذه العملية إلى تأكيد صريح.",
        }
    else:
        try:
            result = await execute(name, arguments)
        except Exception as exc:
            result = {"error": "tool_execution_failed", "message": str(exc)}

    outgoing = tool_result(call_id, result)
    seq = await append(session_id, (await _next_sequence(session_id)), outgoing)
    return {"sequence": seq, **outgoing}

async def _next_sequence(session_id):
    from .realtime_resume import last_sequence
    return await last_sequence(session_id) + 1
