from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class AIResponse:
    provider: str
    model: str
    content: str
    raw: dict[str, Any] | None = None


class AIProvider:
    name = "base"

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str,
        **kwargs: Any,
    ) -> AIResponse:
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    name = "openai"

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str,
        **kwargs: Any,
    ) -> AIResponse:
        payload = {
            "model": model,
            "messages": messages,
            **kwargs,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

        response.raise_for_status()
        data = response.json()

        return AIResponse(
            provider=self.name,
            model=model,
            content=data["choices"][0]["message"]["content"],
            raw=data,
        )


class AnthropicProvider(AIProvider):
    name = "anthropic"

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.anthropic.com",
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str,
        **kwargs: Any,
    ) -> AIResponse:
        system_messages = [
            message["content"]
            for message in messages
            if message.get("role") == "system"
        ]

        chat_messages = [
            message
            for message in messages
            if message.get("role") != "system"
        ]

        payload = {
            "model": model,
            "max_tokens": kwargs.pop("max_tokens", 2048),
            "messages": chat_messages,
            **kwargs,
        }

        if system_messages:
            payload["system"] = "\n\n".join(system_messages)

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

        response.raise_for_status()
        data = response.json()

        content = "".join(
            block.get("text", "")
            for block in data.get("content", [])
            if block.get("type") == "text"
        )

        return AIResponse(
            provider=self.name,
            model=model,
            content=content,
            raw=data,
        )


class GeminiProvider(AIProvider):
    name = "gemini"

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str,
        **kwargs: Any,
    ) -> AIResponse:
        contents = []

        for message in messages:
            role = message.get("role", "user")

            if role == "system":
                continue

            if role == "assistant":
                role = "model"

            contents.append(
                {
                    "role": role,
                    "parts": [{"text": message.get("content", "")}],
                }
            )

        payload: dict[str, Any] = {"contents": contents}

        if kwargs:
            payload["generationConfig"] = kwargs

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/models/{model}:generateContent",
                params={"key": self.api_key},
                json=payload,
            )

        response.raise_for_status()
        data = response.json()

        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError("Gemini returned no candidates")

        parts = candidates[0].get("content", {}).get("parts", [])
        content = "".join(
            part.get("text", "")
            for part in parts
            if isinstance(part, dict)
        )

        return AIResponse(
            provider=self.name,
            model=model,
            content=content,
            raw=data,
        )


class OpenAICompatibleProvider(AIProvider):
    """Provider for OpenAI-compatible APIs such as Groq and OpenRouter."""

    def __init__(
        self,
        name: str,
        api_key: str,
        base_url: str,
        extra_headers: dict[str, str] | None = None,
    ):
        self.name = name
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.extra_headers = extra_headers or {}

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str,
        **kwargs: Any,
    ) -> AIResponse:
        payload = {"model": model, "messages": messages, **kwargs}
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            **self.extra_headers,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )

        response.raise_for_status()
        data = response.json()
        choices = data.get("choices") or []
        if not choices:
            raise RuntimeError(f"{self.name} returned no choices")

        message = choices[0].get("message") or {}
        content = message.get("content", "")
        if not isinstance(content, str):
            content = str(content)

        return AIResponse(
            provider=self.name,
            model=model,
            content=content,
            raw=data,
        )


class GroqProvider(OpenAICompatibleProvider):
    name = "groq"

    def __init__(self, api_key: str, base_url: str = "https://api.groq.com/openai/v1"):
        super().__init__("groq", api_key, base_url)


class OpenRouterProvider(OpenAICompatibleProvider):
    name = "openrouter"

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://openrouter.ai/api/v1",
        site_url: str = "",
        site_name: str = "Voice AI Assistant",
    ):
        extra = {}
        if site_url:
            extra["HTTP-Referer"] = site_url
        if site_name:
            extra["X-Title"] = site_name
        super().__init__("openrouter", api_key, base_url, extra)
