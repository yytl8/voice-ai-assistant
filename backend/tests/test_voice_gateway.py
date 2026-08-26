from app.voice.gateway import VoiceGateway


def test_provider_lists_are_safe(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    monkeypatch.delenv("ELEVENLABS_VOICE_ID", raising=False)
    g = VoiceGateway()
    assert g.providers() == {"stt": [], "tts": []}
