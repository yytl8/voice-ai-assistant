# Voice Gateway

Endpoints:

- GET `/api/voice/providers`
- POST `/api/voice/transcribe` (multipart `file`, optional `language`)
- POST `/api/voice/synthesize` (JSON `{text, voice?, model?}`)

STT fallback:
1. Groq Whisper (`GROQ_API_KEY`)
2. OpenAI transcription (`OPENAI_API_KEY`)

TTS fallback:
1. ElevenLabs (`ELEVENLABS_API_KEY` + `ELEVENLABS_VOICE_ID`)
2. OpenAI TTS (`OPENAI_API_KEY`)

Recommended Render variables:

```env
GROQ_API_KEY=...
OPENAI_API_KEY=...
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=...
GROQ_STT_MODEL=whisper-large-v3-turbo
OPENAI_STT_MODEL=gpt-4o-mini-transcribe
OPENAI_TTS_MODEL=gpt-4o-mini-tts
OPENAI_TTS_VOICE=alloy
ELEVENLABS_MODEL=eleven_multilingual_v2
VOICE_PROVIDER_TIMEOUT=30
```

The browser never receives provider API keys. Provider failures are logged by provider name/type only.
