from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .providers import (
    AIProvider,
    AIResponse,
    AnthropicProvider,
    GeminiProvider,
    OpenAIProvider,
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

    if settings.ai_api_key:
        router.register_provider(
            "openai",
            OpenAIProvider(
                api_key=settings.ai_api_key,
                base_url=settings.ai_base_url,
            ),
        )

        router.register_model(
            "primary",
            "openai",
            settings.openai_chat_model,
        )

    if settings.anthropic_api_key:
        router.register_provider(
            "anthropic",
            AnthropicProvider(
                api_key=settings.anthropic_api_key,
                base_url=settings.anthropic_base_url,
            ),
        )

        router.register_model(
            "claude",
            "anthropic",
            settings.anthropic_model,
        )

    if settings.gemini_api_key:
        router.register_provider(
            "gemini",
            GeminiProvider(
                api_key=settings.gemini_api_key,
                base_url=settings.gemini_base_url,
            ),
        )

        router.register_model(
            "gemini",
            "gemini",
            settings.gemini_model,
        )

    return router
