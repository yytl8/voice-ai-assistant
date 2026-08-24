# Multi-provider AI configuration

The backend supports a provider-agnostic chat API with optional fallback.

## Environment variables

```env
# Existing OpenAI / Realtime configuration
AI_API_KEY=
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-realtime-2.1

# Normal chat model for the OpenAI provider
OPENAI_CHAT_MODEL=gpt-4.1-mini

# Optional Anthropic
ANTHROPIC_API_KEY=
ANTHROPIC_BASE_URL=https://api.anthropic.com
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# Optional Google Gemini
GEMINI_API_KEY=
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
GEMINI_MODEL=gemini-2.5-flash
```

## Endpoints

- `GET /api/ai/models` — authenticated list of configured model aliases.
- `POST /api/ai/chat` — authenticated unified chat endpoint.

Example:

```json
{
  "model": "claude",
  "fallback": ["gemini", "primary"],
  "messages": [
    {"role": "system", "content": "أنت مساعد عربي دقيق."},
    {"role": "user", "content": "مرحبا"}
  ]
}
```

If the selected provider fails, aliases in `fallback` are attempted in order.

Realtime is intentionally unchanged and continues to use the existing realtime settings.
