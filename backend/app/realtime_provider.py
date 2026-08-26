import httpx
from .settings import settings


async def create_ephemeral_session(*, instructions, tools):
    api_key = getattr(settings, "realtime_api_key", "") or settings.ai_api_key
    base_url = getattr(settings, "realtime_base_url", "") or settings.ai_base_url
    if not api_key:
        raise RuntimeError("Realtime voice provider is not configured")
    payload = {
        "model": getattr(settings, "realtime_model", "") or settings.ai_model,
        "voice": getattr(settings, "realtime_voice", "") or settings.voice_name,
        "instructions": instructions,
        "tools": tools,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    url = f"{base_url.rstrip('/')}/realtime/sessions"
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(url, headers=headers, json=payload)
    if response.status_code >= 400:
        raise RuntimeError(f"Realtime provider returned {response.status_code}: {response.text[:1000]}")
    data = response.json()
    secret = data.get("client_secret")
    if isinstance(secret, dict):
        secret = secret.get("value")
    if not secret:
        raise RuntimeError("Realtime provider did not return a client secret")
    return {"client_secret": secret, "provider_session_id": data.get("id") or data.get("session_id"), "expires_at": data.get("expires_at")}
