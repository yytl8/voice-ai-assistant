from __future__ import annotations

from .rbac import SENSITIVE_TOOLS

def requires_confirmation(tool_name: str, arguments: dict) -> bool:
    if tool_name in SENSITIVE_TOOLS:
        return True
    # Pricing is read-only in the current M-One integration.
    # Any future mutation must explicitly enter SENSITIVE_TOOLS.
    return False

def sanitize_audit_arguments(arguments: dict) -> dict:
    secret_keys = {"token", "password", "api_key", "authorization", "client_secret"}
    return {k: ("[REDACTED]" if k.lower() in secret_keys else v) for k, v in arguments.items()}
