import asyncio
from app.ai import build_ai_router
class S:
    ai_api_key=""; ai_base_url="https://api.openai.com/v1"; openai_chat_model="gpt-4.1-mini"
    anthropic_api_key=""; anthropic_base_url="https://api.anthropic.com"; anthropic_model="claude"
    gemini_api_key=""; gemini_base_url="https://generativelanguage.googleapis.com/v1beta"; gemini_model="gemini"
    groq_api_key=""; groq_base_url="https://api.groq.com/openai/v1"; groq_model="llama"
    openrouter_api_key=""; openrouter_base_url="https://openrouter.ai/api/v1"; openrouter_model="openrouter/free"
    openrouter_site_url=""; openrouter_site_name="Voice AI Assistant"
def test_no_ai_key_still_works():
    router=build_ai_router(S())
    assert "demo" in {m["alias"] for m in router.available_models()}
    result=asyncio.run(router.chat([{"role":"user","content":"مرحبا"}],"auto"))
    assert result.provider=="demo"
