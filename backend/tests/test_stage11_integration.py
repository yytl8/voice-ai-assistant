import asyncio

from app.agent_runtime import AgentRuntime
from app.confirmation import issue, consume
from app.realtime_resume import append, after

def test_agent_runtime_confirmation():
    async def execute(name, args):
        return {"ok": True}
    async def run():
        runtime = AgentRuntime(execute)
        denied = await runtime.execute(role="worker", tool_name="mone_approve_price", arguments={})
        assert denied.requires_confirmation
        assert denied.result["requires_confirmation"]
        allowed = await runtime.execute(role="manager", tool_name="mone_search_customer", arguments={"q":"A"})
        assert allowed.result["ok"]
    asyncio.run(run())

def test_confirmation_is_one_time_and_scoped():
    async def run():
        token = await issue("session-A", "mone_approve_price", {"amount": 10})
        value = await consume(token, "session-A", "mone_approve_price")
        assert value["arguments"]["amount"] == 10
        assert await consume(token, "session-A", "mone_approve_price") is None
    asyncio.run(run())

def test_resume_cursor():
    async def run():
        await append("session-test", 1, {"type":"a"})
        await append("session-test", 2, {"type":"b"})
        events = await after("session-test", 1)
        assert [x["sequence"] for x in events] == [2]
    asyncio.run(run())
