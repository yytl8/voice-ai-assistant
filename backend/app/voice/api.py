from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.voice.gateway import voice_gateway

router = APIRouter(prefix="/api/voice", tags=["voice"])


class SynthesizeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)
    voice: str | None = None
    model: str | None = None


@router.get("/providers")
async def voice_providers():
    return voice_gateway.providers()


@router.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    language: str | None = Form(default=None),
):
    try:
        audio = await file.read()
        if not audio:
            raise HTTPException(status_code=400, detail="الملف الصوتي فارغ")
        if len(audio) > 25 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="الملف الصوتي أكبر من الحد المسموح")
        return await voice_gateway.transcribe(
            audio,
            filename=file.filename or "audio.webm",
            content_type=file.content_type or "audio/webm",
            language=language,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail="تعذر تحويل الصوت إلى نص") from exc


@router.post("/synthesize")
async def synthesize(payload: SynthesizeRequest):
    try:
        result = await voice_gateway.synthesize(
            payload.text, voice=payload.voice, model=payload.model
        )
        return Response(
            content=result.content,
            media_type=result.content_type,
            headers={"X-AI-Voice-Provider": result.provider},
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail="تعذر إنشاء الصوت") from exc
