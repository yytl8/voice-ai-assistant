from typing import Any
from .schemas import CutListRequest, PriceInput
from .service import MOneService

mone = MOneService()


def definitions() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "name": "mone_search_customer",
            "description": "ابحث عن عميل في نظام M-One AI.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
        {
            "type": "function",
            "name": "mone_get_project",
            "description": "اجلب مشروعاً من M-One AI بواسطة معرف المشروع.",
            "parameters": {
                "type": "object",
                "properties": {"project_id": {"type": "string"}},
                "required": ["project_id"],
            },
        },
        {
            "type": "function",
            "name": "mone_calculate_price",
            "description": "احسب السعر عبر M-One Pricing Engine.",
            "parameters": {
                "type": "object",
                "properties": {
                    "material": {"type": "number"},
                    "labor": {"type": "number"},
                    "hardware": {"type": "number"},
                    "transport": {"type": "number"},
                    "profit_margin": {"type": "number"},
                    "currency": {"type": "string"},
                },
                "required": ["material", "labor", "hardware", "transport", "profit_margin"],
            },
        },
        {
            "type": "function",
            "name": "mone_cutlist_estimate",
            "description": "أرسل قائمة التقطيع إلى M-One CutList/Manufacturing Engine.",
            "parameters": {
                "type": "object",
                "properties": {
                    "parts": {"type": "array", "items": {"type": "object"}},
                    "sheet": {"type": "object"},
                    "kerf_mm": {"type": "number"},
                },
                "required": ["parts"],
            },
        },
        {
            "type": "function",
            "name": "mone_reverse_engineer_image",
            "description": "حلل صورة أثاث عبر M-One Pipeline للحصول على نتيجة الهندسة العكسية.",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_base64": {"type": "string"},
                    "filename": {"type": "string"},
                },
                "required": ["image_base64"],
            },
        },
    ]


async def execute(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "mone_search_customer":
        return await mone.search_customer(arguments["query"])

    if name == "mone_get_project":
        return await mone.get_project(arguments["project_id"])

    if name == "mone_calculate_price":
        return await mone.calculate_price(PriceInput(**arguments))

    if name == "mone_cutlist_estimate":
        return await mone.optimize_cutlist(CutListRequest(**arguments))

    if name == "mone_reverse_engineer_image":
        return await mone.run_pipeline(
            arguments["image_base64"],
            arguments.get("filename", "image.jpg"),
        )

    raise ValueError(f"Unknown M-One tool: {name}")
