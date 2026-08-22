from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[[dict[str, Any]], dict[str, Any]]
    risk: str = "low"


def calculate_price(args: dict[str, Any]) -> dict[str, Any]:
    material = float(args.get("material", 0))
    labor = float(args.get("labor", 0))
    hardware = float(args.get("hardware", 0))
    transport = float(args.get("transport", 0))
    margin = float(args.get("profit_margin", 0.0))
    if margin < 0 or margin > 5:
        raise ValueError("profit_margin must be between 0 and 5")

    subtotal = material + labor + hardware + transport
    total = subtotal * (1 + margin)
    return {
        "currency": args.get("currency", "YER"),
        "subtotal": round(subtotal, 2),
        "profit_margin": margin,
        "total": round(total, 2),
    }


def convert_measurement(args: dict[str, Any]) -> dict[str, Any]:
    value = float(args["value"])
    conversion = args["conversion"].lower()
    factors = {
        "mm_to_cm": 0.1,
        "cm_to_mm": 10,
        "m_to_cm": 100,
        "cm_to_m": 0.01,
        "inch_to_mm": 25.4,
        "mm_to_inch": 1 / 25.4,
    }
    if conversion not in factors:
        raise ValueError("Unsupported conversion")
    return {
        "value": value,
        "conversion": conversion,
        "result": round(value * factors[conversion], 4),
    }


TOOLS = {
    "calculate_price": ToolSpec(
        "calculate_price",
        "احسب سعر مشروع من المادة والعمالة والإكسسوارات والنقل وهامش الربح.",
        {
            "type": "object",
            "properties": {
                "material": {"type": "number"},
                "labor": {"type": "number"},
                "hardware": {"type": "number"},
                "transport": {"type": "number"},
                "profit_margin": {"type": "number", "description": "0.20 تعني 20%"},
                "currency": {"type": "string"},
            },
            "required": ["material", "labor", "hardware", "transport", "profit_margin"],
        },
        calculate_price,
    ),
    "convert_measurement": ToolSpec(
        "convert_measurement",
        "حوّل قياسات شائعة في أعمال النجارة.",
        {
            "type": "object",
            "properties": {
                "value": {"type": "number"},
                "conversion": {
                    "type": "string",
                    "enum": ["mm_to_cm", "cm_to_mm", "m_to_cm", "cm_to_m", "inch_to_mm", "mm_to_inch"],
                },
            },
            "required": ["value", "conversion"],
        },
        convert_measurement,
    ),
}


def realtime_tools() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "name": s.name,
            "description": s.description,
            "parameters": s.parameters,
        }
        for s in TOOLS.values()
    ]


def execute_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    spec = TOOLS.get(name)
    if not spec:
        raise ValueError(f"Tool '{name}' is not allowed")
    return spec.handler(arguments)


def tool_risk(name: str) -> str:
    spec = TOOLS.get(name)
    if not spec:
        raise ValueError("Unknown tool")
    return spec.risk
