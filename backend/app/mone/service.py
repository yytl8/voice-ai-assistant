from dataclasses import dataclass
from math import ceil
from typing import Any

from .schemas import Customer, Project, PriceInput, CutListRequest
from .integration import get_mone_client
from ..settings import settings


@dataclass
class MOneService:
    async def search_customer(self, query: str) -> dict[str, Any]:
        if settings.mone_api_url:
            return await get_mone_client().customers(query)

        sample = [
            Customer(id="CUST-001", name="أحمد محمد"),
            Customer(id="CUST-002", name="محمد علي"),
        ]
        q = query.strip().lower()
        return {"customers": [x.model_dump() for x in sample if q in x.name.lower() or q in x.id.lower()]}

    async def get_project(self, project_id: str) -> dict[str, Any]:
        if settings.mone_api_url:
            return await get_mone_client().project(project_id)

        return {"project": Project(
            id=project_id, customer_id="CUST-001", name="مشروع تجريبي"
        ).model_dump()}

    async def calculate_price(self, data: PriceInput) -> dict[str, Any]:
        if settings.mone_api_url:
            return await get_mone_client().pricing(data.model_dump())

        subtotal = data.material + data.labor + data.hardware + data.transport
        profit = subtotal * data.profit_margin
        return {
            "pricing": {
                "currency": data.currency,
                "subtotal": round(subtotal, 2),
                "profit": round(profit, 2),
                "total": round(subtotal + profit, 2),
                "fallback": True,
            }
        }

    async def optimize_cutlist(self, request: CutListRequest) -> dict[str, Any]:
        if settings.mone_api_url:
            return await get_mone_client().cutlist(request.model_dump())

        sheet_area = request.sheet.length_mm * request.sheet.width_mm
        total_area = sum(p.length_mm * p.width_mm * p.quantity for p in request.parts)
        sheets = max(1, ceil(total_area / sheet_area))
        return {
            "cutlist": {
                "estimated_sheets": sheets,
                "sheet": request.sheet.model_dump(),
                "fallback": True,
                "warning": "Fallback estimate; connect M-One Manufacturing Engine for production nesting.",
            }
        }

    async def run_pipeline(self, image_base64: str, filename: str = "image.jpg") -> dict[str, Any]:
        if not settings.mone_api_url:
            raise RuntimeError("MONE_API_URL is not configured")
        return await get_mone_client().pipeline({
            "image_base64": image_base64,
            "filename": filename,
        })
