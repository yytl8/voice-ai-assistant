def test_realtime_client_must_use_backend_proxy():
    from pathlib import Path
    p = Path(__file__).parents[2] / "frontend" / "app" / "realtime-client.ts"
    s = p.read_text()
    assert "https://api.openai.com/v1/realtime/calls" not in s
    assert "fetch(`/api/realtime/session`" in s


def test_voice_assistant_must_use_backend_proxy():
    from pathlib import Path
    p = Path(__file__).parents[2] / "frontend" / "app" / "voice-assistant.tsx"
    s = p.read_text()
    assert "${API_URL}/api/realtime/session" in s
    assert "https://api.openai.com/v1/realtime/calls" not in s
