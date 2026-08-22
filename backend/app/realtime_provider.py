import httpx
from ..settings import settings

async def create_ephemeral_session(*, instructions, tools):
    if not settings.ai_api_key:
        raise RuntimeError("AI_API_KEY is not configured")
    payload = {
        "model": settings.realtime_model,
        "voice": settings.realtime_voice,
        "instructions": instructions,
        "tools": tools,
    }
    headers = {"Authorization": f"Bearer {settings.ai_api_key}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(settings.realtime_session_url, headers=headers, json=payload)
    if response.status_code >= 400:
        raise RuntimeError(f"Realtime provider returned {response.status_code}: {response.text[:1000]}")
    data = response.json()
    secret = data.get("client_secret")
    if isinstance(secret, dict):
        secret = secret.get("value")
    if not secret:
        raise RuntimeError("Realtime provider did not return a client secret")
    return {"client_secret": secret, "provider_session_id": data.get("id") or data.get("session_id"), "expires_at": data.get("expires_at")}
