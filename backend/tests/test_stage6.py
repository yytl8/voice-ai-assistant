import asyncio
from app.mone.service import MOneService
from app.mone.schemas import PriceInput


def test_stage6_fallback_pricing_is_deterministic():
    result = asyncio.run(MOneService().calculate_price(PriceInput(
        material=100000,
        labor=30000,
        hardware=10000,
        transport=5000,
        profit_margin=0.20,
    )))
    assert result["pricing"]["total"] == 174000
    assert result["pricing"]["fallback"] is True
