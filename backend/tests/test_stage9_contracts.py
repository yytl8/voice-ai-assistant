import asyncio
from app.security.rbac import can_use_tool
from app.security.policy import requires_confirmation, sanitize_audit_arguments

def test_rbac_and_confirmation():
    assert can_use_tool("worker", "mone_cutlist_estimate")
    assert not can_use_tool("worker", "mone_approve_price")
    assert requires_confirmation("mone_approve_price", {})
    assert not requires_confirmation("mone_search_customer", {})

def test_audit_redaction():
    data = sanitize_audit_arguments({"customer": "A", "token": "secret"})
    assert data["token"] == "[REDACTED]"

def test_rate_limit_memory():
    from app.rate_limit import allow
    async def run():
        assert await allow("test-stage9", 1, 60)
        assert not await allow("test-stage9", 1, 60)
    asyncio.run(run())
