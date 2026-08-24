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
