import httpx
from .settings import settings
class MOneClient:
    async def call(self, tool_name, arguments):
        if not settings.mone_api_url: raise RuntimeError("MONE_API_URL is not configured")
        if not settings.mone_api_token: raise RuntimeError("MONE_API_TOKEN is not configured")
        async with httpx.AsyncClient(timeout=httpx.Timeout(30,connect=5)) as c:
            r=await c.post(
                settings.mone_api_url.rstrip("/")+"/api/v1/agent/tools/execute",
                headers={"Authorization":f"Bearer {settings.mone_api_token}","X-Agent-Source":"voice-ai-assistant"},
                json={"tool":tool_name,"arguments":arguments})
        if r.status_code>=400: raise RuntimeError(f"M-One request failed with HTTP {r.status_code}")
        return r.json()
mone_client=MOneClient()
