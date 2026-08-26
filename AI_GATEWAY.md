# AI Gateway

The backend now exposes a provider-agnostic AI Gateway.

## Endpoints

- `GET /api/ai/models` — configured model aliases.
- `GET /api/ai/providers` — provider/model availability without exposing secrets.
- `POST /api/ai/chat` — authenticated chat with ordered fallback.

## Supported providers

- OpenAI: `provider-specific API keys (GEMINI_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY, etc.)`
- Anthropic/Claude: `ANTHROPIC_API_KEY`
- Google Gemini: `GEMINI_API_KEY`
- Groq: `GROQ_API_KEY`
- OpenRouter: `OPENROUTER_API_KEY`

## Render configuration

Recommended free-first configuration:

```env
GROQ_API_KEY=...
OPENROUTER_API_KEY=...
```

Optional:

```env
provider-specific API keys (GEMINI_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY, etc.)=...
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
```

The OpenRouter default alias is `openrouter-free`, using the model `openrouter/free`.
The Groq default alias is `groq`.

## Fallback example

```json
{
  "model": "openrouter-free",
  "fallback": ["groq", "gemini", "primary"],
  "messages": [
    {"role": "system", "content": "أنت مساعد عربي."},
    {"role": "user", "content": "مرحبا"}
  ]
}
```

API keys are server-side only and are never returned by the provider endpoints.


## Automatic provider selection

The frontend now defaults to `auto` mode. The backend uses this order among
providers that are actually configured:

1. `groq`
2. `openrouter-free`
3. `gemini`
4. `primary` (OpenAI)
5. `claude`

A failed provider is skipped automatically and the next configured provider
is attempted. No API key is exposed to the browser.

Use `model: "auto"` in `POST /api/ai/chat` to activate this behavior.
