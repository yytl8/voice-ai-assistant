from typing import Any
from .mone.tools import definitions as mone_definitions, execute as execute_mone
from .tools import realtime_tools, execute_tool

def all_tool_definitions():
    return realtime_tools() + mone_definitions()

async def execute_agent_tool(name: str, arguments: dict[str, Any]):
    if name.startswith("mone_"):
        return await execute_mone(name, arguments)
    return execute_tool(name, arguments)
