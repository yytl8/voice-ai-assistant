from __future__ import annotations
import json

def normalize_event(event: dict) -> dict:
    event_type = event.get("type", "unknown")
    return {
        "type": event_type,
        "event_id": event.get("event_id") or event.get("id"),
        "sequence": event.get("sequence"),
        "payload": event,
    }

def tool_event(name: str, call_id: str, arguments: dict) -> dict:
    return {
        "type": "tool.call",
        "event_id": call_id,
        "tool_name": name,
        "arguments": arguments,
    }

def tool_result(call_id: str, result: dict) -> dict:
    return {
        "type": "tool.result",
        "event_id": call_id,
        "result": result,
    }
