from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .providers import (
    AIProvider,
    AIResponse,
    AnthropicProvider,
    GeminiProvider,
    OpenAIProvider,
    GroqProvider,
    OpenRouterProvider,
    DemoProvider,
)


@dataclass(frozen=True)
class ModelConfig:
    provider: str
    model: str


class AIRouter:
    """Provider-agnostic chat router with ordered fallback support."""

    def __init__(self) -> None:
        self.providers: dict[str, AIProvider] = {}
        self.models: dict[str, ModelConfig] = {}

    def register_provider(self, name: str, provider: AIProvider) -> None:
        self.providers[name] = provider

    def register_model(
        self,
        alias: str,
        provider: str,
        model: str,
    ) -> None:
        if provider not in self.providers:
            raise ValueError(
                f"Cannot register model '{alias}': "
                f"provider '{provider}' is not configured"
            )

        self.models[alias] = ModelConfig(
            provider=provider,
            model=model,
        )

    def available_models(self) -> list[dict[str, str]]:
        return [
            {
                "alias": alias,
                "provider": config.provider,
                "model": config.model,
            }
            for alias, config in self.models.items()
        ]

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str,
        fallback: list[str] | None = None,
        **kwargs: Any,
    ) -> AIResponse:
        # "auto" is intentionally deterministic: prefer free/low-cost
        # providers first, then paid providers as a final fallback.
        if model == "auto":
            preferred = [
                "groq",
                "openrouter-free",
                "gemini",
                "primary",
                "claude",
                "demo",
            ]
            candidates = [alias for alias in preferred if alias in self.models]
        else:
            candidates = [model]

        for fallback_model in fallback or []:
            if fallback_model not in candidates:
                candidates.append(fallback_model)

        if not candidates:
            raise RuntimeError("No AI model candidates configured")

        last_error: Exception | None = None

        for alias in candidates:
            config = self.models.get(alias)

            if not config:
                last_error = ValueError(
                    f"Unknown AI model alias: {alias}"
                )
                continue

            provider = self.providers.get(config.provider)

            if not provider:
                last_error = RuntimeError(
                    f"AI provider is not configured: {config.provider}"
                )
                continue

            try:
                return await provider.chat(
                    messages=messages,
                    model=config.model,
                    **kwargs,
                )
            except Exception as exc:
                last_error = exc

        raise RuntimeError(
            "All requested AI providers failed"
        ) from last_error


def build_ai_router(settings) -> AIRouter:
    router = AIRouter()

    router.register_provider("demo", DemoProvider())
    router.register_model("demo", "demo", "demo")

    # OpenAI
    if settings.ai_api_key:
        router.register_provider(
            "openai",
            OpenAIProvider(
                api_key=settings.ai_api_key,
                base_url=settings.ai_base_url,
            ),
        )
        router.register_model("primary", "openai", settings.openai_chat_model)

    # Anthropic / Claude
    if settings.anthropic_api_key:
        router.register_provider(
            "anthropic",
            AnthropicProvider(
                api_key=settings.anthropic_api_key,
                base_url=settings.anthropic_base_url,
            ),
        )
        router.register_model("claude", "anthropic", settings.anthropic_model)

    # Google Gemini
    if settings.gemini_api_key:
        router.register_provider(
            "gemini",
            GeminiProvider(
                api_key=settings.gemini_api_key,
                base_url=settings.gemini_base_url,
            ),
        )
        router.register_model("gemini", "gemini", settings.gemini_model)

    # Groq: fast, OpenAI-compatible API
    if settings.groq_api_key:
        router.register_provider(
            "groq",
            GroqProvider(
                api_key=settings.groq_api_key,
                base_url=settings.groq_base_url,
            ),
        )
        router.register_model("groq", "groq", settings.groq_model)

    # OpenRouter: one gateway for many models, including free-model routing
    if settings.openrouter_api_key:
        router.register_provider(
            "openrouter",
            OpenRouterProvider(
                api_key=settings.openrouter_api_key,
                base_url=settings.openrouter_base_url,
                site_url=settings.openrouter_site_url,
                site_name=settings.openrouter_site_name,
            ),
        )
        router.register_model(
            "openrouter-free",
            "openrouter",
            settings.openrouter_model,
        )

    return router

