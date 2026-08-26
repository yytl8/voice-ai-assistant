from __future__ import annotations

import base64
import io
import logging
import os
from dataclasses import dataclass
from typing import Any

import httpx

logger = logging.getLogger(__name__)


@dataclass
class VoiceResult:
    provider: str
    content: bytes
    content_type: str
    text: str | None = None


class VoiceGateway:
    """STT/TTS gateway. Providers are attempted in configured order."""

    def __init__(self) -> None:
        self.groq_key = os.getenv("GROQ_API_KEY", "")
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.elevenlabs_key = os.getenv("ELEVENLABS_API_KEY", "")
        self.elevenlabs_voice = os.getenv("ELEVENLABS_VOICE_ID", "")
        self.timeout = float(os.getenv("VOICE_PROVIDER_TIMEOUT", "30"))

    def providers(self) -> dict[str, list[str]]:
        stt = []
        tts = []
        if self.groq_key:
            stt.append("groq")
        if self.openai_key:
            stt.append("openai")
        if self.elevenlabs_key and self.elevenlabs_voice:
            tts.append("elevenlabs")
        if self.openai_key:
            tts.append("openai")
        return {"stt": stt, "tts": tts}

    async def transcribe(self, audio: bytes, filename: str = "audio.webm",
                         content_type: str = "audio/webm", language: str | None = None) -> dict[str, Any]:
        errors: list[str] = []
        for provider in self.providers()["stt"]:
            try:
                if provider == "groq":
                    return await self._groq_stt(audio, filename, content_type, language)
                if provider == "openai":
                    return await self._openai_stt(audio, filename, content_type, language)
            except Exception as exc:
                logger.warning("STT provider %s failed: %s", provider, type(exc).__name__)
                errors.append(f"{provider}: {type(exc).__name__}")
        raise RuntimeError("All configured STT providers failed: " + ", ".join(errors))

    async def synthesize(self, text: str, voice: str | None = None,
                         model: str | None = None) -> VoiceResult:
        errors: list[str] = []
        for provider in self.providers()["tts"]:
            try:
                if provider == "elevenlabs":
                    return await self._elevenlabs_tts(text, voice)
                if provider == "openai":
                    return await self._openai_tts(text, voice, model)
            except Exception as exc:
                logger.warning("TTS provider %s failed: %s", provider, type(exc).__name__)
                errors.append(f"{provider}: {type(exc).__name__}")
        raise RuntimeError("All configured TTS providers failed: " + ", ".join(errors))

    async def _groq_stt(self, audio, filename, content_type, language):
        headers = {"Authorization": f"Bearer {self.groq_key}"}
        files = {"file": (filename, audio, content_type)}
        data = {"model": os.getenv("GROQ_STT_MODEL", "whisper-large-v3-turbo")}
        if language:
            data["language"] = language
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post("https://api.groq.com/openai/v1/audio/transcriptions",
                                  headers=headers, files=files, data=data)
            r.raise_for_status()
            payload = r.json()
        return {"provider": "groq", "text": payload.get("text", ""), "raw": payload}

    async def _openai_stt(self, audio, filename, content_type, language):
        headers = {"Authorization": f"Bearer {self.openai_key}"}
        files = {"file": (filename, audio, content_type)}
        data = {"model": os.getenv("OPENAI_STT_MODEL", "gpt-4o-mini-transcribe")}
        if language:
            data["language"] = language
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post("https://api.openai.com/v1/audio/transcriptions",
                                  headers=headers, files=files, data=data)
            r.raise_for_status()
            payload = r.json()
        return {"provider": "openai", "text": payload.get("text", ""), "raw": payload}

    async def _elevenlabs_tts(self, text, voice):
        voice_id = voice or self.elevenlabs_voice
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {"xi-api-key": self.elevenlabs_key, "Content-Type": "application/json"}
        payload = {
            "text": text,
            "model_id": os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2"),
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            return VoiceResult("elevenlabs", r.content, r.headers.get("content-type", "audio/mpeg"))

    async def _openai_tts(self, text, voice, model):
        headers = {"Authorization": f"Bearer {self.openai_key}"}
        payload = {
            "model": model or os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"),
            "voice": voice or os.getenv("OPENAI_TTS_VOICE", "alloy"),
            "input": text,
            "response_format": "mp3",
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post("https://api.openai.com/v1/audio/speech",
                                  headers=headers, json=payload)
            r.raise_for_status()
            return VoiceResult("openai", r.content, r.headers.get("content-type", "audio/mpeg"))


voice_gateway = VoiceGateway()
