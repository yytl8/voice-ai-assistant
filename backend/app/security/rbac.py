from __future__ import annotations
from enum import StrEnum

class Role(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    WORKER = "worker"
    VIEWER = "viewer"

TOOL_PERMISSIONS = {
    "mone_search_customer": {Role.OWNER, Role.ADMIN, Role.MANAGER, Role.WORKER, Role.VIEWER},
    "mone_get_project": {Role.OWNER, Role.ADMIN, Role.MANAGER, Role.WORKER, Role.VIEWER},
    "mone_calculate_price": {Role.OWNER, Role.ADMIN, Role.MANAGER},
    "mone_cutlist_estimate": {Role.OWNER, Role.ADMIN, Role.MANAGER, Role.WORKER},
    "mone_reverse_engineer_image": {Role.OWNER, Role.ADMIN, Role.MANAGER, Role.WORKER},
}

SENSITIVE_TOOLS = {
    "mone_create_project",
    "mone_update_customer",
    "mone_approve_price",
    "mone_create_manufacturing_order",
    "mone_export",
}

def can_use_tool(role: str, tool_name: str) -> bool:
    if tool_name in SENSITIVE_TOOLS:
        return role in {Role.OWNER, Role.ADMIN, Role.MANAGER}
    allowed = TOOL_PERMISSIONS.get(tool_name)
    return True if allowed is None else role in allowed
