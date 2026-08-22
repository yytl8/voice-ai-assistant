from __future__ import annotations

import httpx
from dataclasses import dataclass
from typing import Any

from ..settings import settings


@dataclass
class MOneAPIClient:
    """
    Production boundary for the existing M-One AI backend.

    Expected environment:
      MONE_API_URL=https://m-one-ai.onrender.com
      MONE_API_TOKEN=<service credential or internal token>

    The Voice Agent never receives this credential.
    """

    base_url: str
    token: str

    async def request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        timeout: float = 30,
    ) -> dict[str, Any]:
        url = self.base_url.rstrip("/") + "/" + path.lstrip("/")
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(method, url, headers=headers, json=json_body)

        if response.status_code >= 400:
            raise RuntimeError(
                f"M-One API returned {response.status_code}: {response.text[:1000]}"
            )

        if not response.content:
            return {}
        return response.json()

    async def health(self) -> dict[str, Any]:
        return await self.request("GET", "/health")

    async def customers(self, query: str) -> dict[str, Any]:
        # Route is intentionally configurable through MONE_CUSTOMERS_PATH.
        return await self.request(
            "GET",
            settings.mone_customers_path,
            json_body={"query": query},
        )

    async def project(self, project_id: str) -> dict[str, Any]:
        return await self.request(
            "GET",
            settings.mone_project_path.format(project_id=project_id),
        )

    async def pricing(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.request("POST", settings.mone_pricing_path, json_body=payload)

    async def cutlist(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.request("POST", settings.mone_cutlist_path, json_body=payload)

    async def pipeline(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.request("POST", settings.mone_pipeline_path, json_body=payload)


def get_mone_client() -> MOneAPIClient:
    return MOneAPIClient(
        base_url=settings.mone_api_url,
        token=settings.mone_api_token,
    )
