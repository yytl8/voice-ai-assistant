import asyncio
from app.mone.service import MOneService
from app.mone.schemas import PriceInput, CutListRequest, CutPart

def test_mone_pricing():
    result = asyncio.run(MOneService().calculate_price(PriceInput(
        material=100000, labor=30000, hardware=10000, transport=5000, profit_margin=0.20
    )))
    assert result["total"] == 174000

def test_cutlist_sheet_size():
    result = asyncio.run(MOneService().optimize_cutlist(CutListRequest(
        parts=[CutPart(name="side", length_mm=1000, width_mm=500, quantity=2)]
    )))
    assert result["sheet"]["length_mm"] == 2440
    assert result["sheet"]["width_mm"] == 1220
    assert result["estimated_sheets"] >= 1
