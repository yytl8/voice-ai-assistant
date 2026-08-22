from pydantic import BaseModel, Field

class Customer(BaseModel):
    id: str
    name: str
    phone: str | None = None

class Project(BaseModel):
    id: str
    customer_id: str
    name: str
    status: str = "active"

class PriceInput(BaseModel):
    material: float = Field(ge=0)
    labor: float = Field(ge=0)
    hardware: float = Field(ge=0)
    transport: float = Field(ge=0)
    profit_margin: float = Field(ge=0, le=5)
    currency: str = "YER"

class CutPart(BaseModel):
    name: str
    length_mm: float = Field(gt=0)
    width_mm: float = Field(gt=0)
    quantity: int = Field(gt=0)
    thickness_mm: float = Field(default=18, gt=0)

class SheetSpec(BaseModel):
    length_mm: float = 2440
    width_mm: float = 1220
    thickness_mm: float = 18

class CutListRequest(BaseModel):
    parts: list[CutPart]
    sheet: SheetSpec = SheetSpec()
    kerf_mm: float = Field(default=3, ge=0)
