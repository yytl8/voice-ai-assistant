import json
import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .observability import configure
configure()

from .auth import create_access_token, current_user, hash_password, verify_password
from .db import get_db
from .memory import get_memories_for_user, save_memory_for_user, delete_memory_for_user
from .models import AuditLog, User
from .rate_limit import rate_limit
from .schemas import LoginRequest, MemoryRequest, RegisterRequest, TokenResponse, ToolRequest
from .settings import settings
from .tools import execute_tool, realtime_tools, tool_risk
from .agent import all_tool_definitions, execute_agent_tool
from .mone.integration import get_mone_client
from .confirmations import create as create_confirmation, consume as consume_confirmation
from .conversation import create as create_conversation, get as get_conversation, list_for_user, add_message
from .realtime_session import create as create_realtime_session, close as close_realtime_session
from .conversation_agent import realtime_session_config, handle_tool
from .media import validate_image

app = FastAPI(title="Voice AI Assistant API", version="0.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_guard(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > settings.max_request_body_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Request body too large")
    await rate_limit(request)
    return await call_next(request)



@app.get("/api/mone/health")
async def mone_health(user: User = Depends(current_user)):
    if not settings.mone_api_url:
        return {"configured": False, "status": "disabled"}
    try:
        return {"configured": True, "status": "ok", "upstream": await get_mone_client().health()}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/confirmations")
async def request_confirmation(
    action: str,
    user: User = Depends(current_user),
):
    c = create_confirmation(user.id, action)
    return {
        "confirmation_token": c.token,
        "action": c.action,
        "expires_at": c.expires_at.isoformat(),
        "message": "اطلب تأكيداً صريحاً من المستخدم قبل تنفيذ العملية الحساسة.",
    }


@app.post("/api/confirmations/consume")
async def use_confirmation(
    action: str,
    token: str,
    user: User = Depends(current_user),
):
    if not consume_confirmation(user.id, token, action):
        raise HTTPException(status_code=403, detail="Invalid or expired confirmation")
    return {"confirmed": True, "action": action}


@app.post("/api/conversations")
async def create_conversation_api(
    title: str = "محادثة جديدة",
    user: User = Depends(current_user),
):
    item = create_conversation(user.id, title)
    return {
        "id": item.id,
        "title": item.title,
        "created_at": item.created_at.isoformat(),
    }


@app.get("/api/conversations")
async def list_conversations_api(user: User = Depends(current_user)):
    return [
        {
            "id": x.id,
            "title": x.title,
            "created_at": x.created_at.isoformat(),
            "updated_at": x.updated_at.isoformat(),
            "message_count": len(x.messages),
        }
        for x in list_for_user(user.id)
    ]


@app.get("/api/conversations/{conversation_id}")
async def get_conversation_api(
    conversation_id: str,
    user: User = Depends(current_user),
):
    item = get_conversation(user.id, conversation_id)
    if not item:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {
        "id": item.id,
        "title": item.title,
        "messages": item.messages,
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat(),
    }


@app.post("/api/conversations/{conversation_id}/messages")
async def add_conversation_message_api(
    conversation_id: str,
    role: str,
    content: str,
    user: User = Depends(current_user),
):
    if role not in {"user", "assistant", "system"}:
        raise HTTPException(status_code=400, detail="Invalid role")
    try:
        item = add_message(user.id, conversation_id, role, content)
    except KeyError:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"conversation_id": item.id, "message_count": len(item.messages)}


@app.post("/api/realtime/sessions")
async def create_realtime_session_api(
    conversation_id: str,
    user: User = Depends(current_user),
):
    if not get_conversation(user.id, conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return realtime_session_config(user.id, conversation_id)


@app.delete("/api/realtime/sessions/{session_id}")
async def close_realtime_session_api(
    session_id: str,
    user: User = Depends(current_user),
):
    if not close_realtime_session(user.id, session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"closed": True}


@app.post("/api/realtime/tool")
async def realtime_tool_api(
    conversation_id: str,
    name: str,
    arguments: dict,
    user: User = Depends(current_user),
):
    if not get_conversation(user.id, conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    role = getattr(user, "role", "viewer")
    if not can_use_tool(role, name):
        raise HTTPException(status_code=403, detail="Tool not permitted for this role")
    if not await rate_allow(f"user:{user.id}:tool", settings.tool_rate_limit_per_minute, 60):
        raise HTTPException(status_code=429, detail="Tool rate limit exceeded")
    if requires_confirmation(name, arguments):
        return {
            "requires_confirmation": True,
            "tool_name": name,
            "arguments": sanitize_audit_arguments(arguments),
            "message": "هذه العملية تحتاج تأكيداً صريحاً قبل التنفيذ."
        }
    try:
        return await handle_tool(user.id, conversation_id, name, arguments)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/media/image")
async def prepare_image_api(
    image_base64: str,
    content_type: str = "image/jpeg",
    user: User = Depends(current_user),
):
    try:
        return validate_image(image_base64, content_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc



@app.get("/metrics")
async def metrics_api(user: User = Depends(current_user)):
    return {"metrics": snapshot()}


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "microphone=(self), camera=(self)"
    return response

@app.get("/ready")
async def readiness():
    missing=validate_production()
    if missing: return {"ready":False,"missing_configuration":missing}
    try:
        async for db in get_db():
            db_ok=await check_database(db)
            redis_ok=await check_redis(state)
            return {"ready":bool(db_ok and redis_ok),"database":db_ok,"redis":redis_ok}
    except Exception:
        return {"ready":False,"database":False,"redis":False}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "voice-ai-assistant", "stage": 4}


@app.post("/api/auth/register", response_model=TokenResponse)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    email = payload.email.lower().strip()
    existing = await db.scalar(select(User).where(User.email == email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name.strip(),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        expires_in=settings.access_token_minutes * 60,
        user={"id": user.id, "email": user.email, "display_name": user.display_name},
    )


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    email = payload.email.lower().strip()
    user = await db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    token = create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        expires_in=settings.access_token_minutes * 60,
        user={"id": user.id, "email": user.email, "display_name": user.display_name},
    )


@app.get("/api/auth/me")
async def me(user: User = Depends(current_user)):
    return {"id": user.id, "email": user.email, "display_name": user.display_name}


@app.get("/api/tools")
async def list_tools(user: User = Depends(current_user)):
    return {"tools": all_tool_definitions()}


@app.post("/api/tools/execute")
async def run_tool(
    payload: ToolRequest,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        risk = "read" if payload.name.startswith("mone_") else tool_risk(payload.name)
        if risk not in {"low", "read"}:
            raise HTTPException(status_code=403, detail="This tool requires explicit approval")

        result = await execute_agent_tool(payload.name, payload.arguments)

        db.add(AuditLog(
            user_id=user.id,
            action="tool.execute",
            tool_name=payload.name,
            success=True,
            metadata_json=json.dumps({"risk": risk, "arguments": payload.arguments}, ensure_ascii=False)[:5000],
        ))
        await db.commit()
        return {"ok": True, "name": payload.name, "result": result}
    except HTTPException:
        raise
    except (ValueError, KeyError, TypeError) as exc:
        db.add(AuditLog(
            user_id=user.id, action="tool.execute", tool_name=payload.name,
            success=False, metadata_json=str(exc)[:1000],
        ))
        await db.commit()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/memory")
async def read_memory(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    return {"memories": await get_memories_for_user(db, user.id)}


@app.post("/api/memory")
async def write_memory(payload: MemoryRequest, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await save_memory_for_user(db, user.id, payload.key.strip(), payload.value)
    await db.commit()
    return {"ok": True}


@app.delete("/api/memory/{key}")
async def remove_memory(key: str, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await delete_memory_for_user(db, user.id, key)
    await db.commit()
    return {"ok": True}


@app.post("/api/realtime/session")
async def realtime_session(
    request: Request,
    user: User = Depends(current_user),
):
    if not settings.ai_api_key:
        raise HTTPException(status_code=503, detail="AI_API_KEY is not configured")

    sdp = (await request.body()).decode("utf-8", errors="replace").strip()
    if not sdp:
        raise HTTPException(status_code=400, detail="Missing SDP offer")

    session = {
        "type": "realtime",
        "model": settings.ai_model,
        "audio": {"output": {"voice": settings.voice_name}},
        "instructions": settings.system_instructions,
        "tools": all_tool_definitions(),
        "tool_choice": "auto",
    }

    url = settings.ai_base_url.rstrip("/") + "/realtime/calls"
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                url,
                headers={"Authorization": f"Bearer {settings.ai_api_key}"},
                files={
                    "sdp": ("offer.sdp", sdp, "application/sdp"),
                    "session": (None, json.dumps(session, ensure_ascii=False), "application/json"),
                },
            )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Realtime upstream error: {exc}") from exc

    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text[:2000])

    return {"sdp": response.text, "user_id": user.id}
