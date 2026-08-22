from .security.rbac import can_use_tool
from .security.policy import requires_confirmation,sanitize_audit_arguments
from .tool_registry import is_registered
class AgentRuntime:
    def __init__(self,execute_tool): self.execute_tool=execute_tool
    async def execute(self,role,tool_name,arguments):
        if not is_registered(tool_name): return {"error":"unknown_tool"}
        if not can_use_tool(role,tool_name): return {"error":"tool_not_permitted"}
        if requires_confirmation(tool_name,arguments):
            return {"requires_confirmation":True,"tool_name":tool_name,
                    "arguments":sanitize_audit_arguments(arguments)}
        return await self.execute_tool(tool_name,arguments)
