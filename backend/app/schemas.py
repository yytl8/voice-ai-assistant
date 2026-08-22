from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(default="مستخدم", min_length=1, max_length=120)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class ToolRequest(BaseModel):
    name: str
    arguments: dict = Field(default_factory=dict)


class MemoryRequest(BaseModel):
    key: str = Field(min_length=1, max_length=120)
    value: str = Field(max_length=10000)
