import json
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    max_attachment_bytes: int = 12 * 1024 * 1024
    log_level: str = "INFO"
    # Deprecated alias kept only so old deployments that still set ALLOWED_ORIGINS
    # don't crash. The middleware uses `cors_origins`, not this field.
    allowed_origins: str = ""
    redis_url: str = ""
    environment: str = "development"
    app_env: str = "development"
    database_url: str = "postgresql+asyncpg://voice:voice@localhost:5432/voice_ai"
    ai_base_url: str = "https://api.openai.com/v1"
    ai_api_key: str = ""
    attachment_dir: str = "/tmp/voice-ai-attachments"
    rate_limit_per_minute: int = 60
    tool_rate_limit_per_minute: int = 30
    ai_model: str = "gpt-realtime-2.1"
    # Realtime model remains separate from the normal chat model.
    openai_chat_model: str = "gpt-4.1-mini"

    # Optional secondary AI providers.
    anthropic_api_key: str = ""
    anthropic_base_url: str = "https://api.anthropic.com"
    anthropic_model: str = "claude-sonnet-4-20250514"

    gemini_api_key: str = ""
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    gemini_model: str = "gemini-2.5-flash"
    voice_name: str = "marin"

    jwt_secret: str = "CHANGE_ME_IN_PRODUCTION"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60
    refresh_token_days: int = 30

    # `NoDecode` stops pydantic-settings from running its own `json.loads()`
    # on the raw env var before our validator ever sees it. Without this,
    # a blank CORS_ORIGINS="" makes pydantic-settings itself raise
    # `json.decoder.JSONDecodeError: Expecting value: line 1 column 1
    # (char 0)` -> `SettingsError`, crashing the whole app at import time
    # before `_parse_cors_origins` below ever runs. This is exactly the
    # crash seen in the Render logs.
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000"]
    max_request_body_mb: int = 15

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_cors_origins(cls, value):
        """Accept a JSON array, a comma-separated string, a real list
        (non-env sources), or an empty/unset value -- without ever crashing
        app startup. A malformed CORS setting should degrade to "no extra
        origins allowed", not take the whole API down.
        """
        if value is None:
            return ["http://localhost:3000"]
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return ["http://localhost:3000"]
            if stripped.startswith("["):
                try:
                    parsed = json.loads(stripped)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if str(item).strip()]
                except json.JSONDecodeError:
                    pass
            # Fall back to comma-separated origins, e.g.
            # "https://a.com,https://b.com"
            return [origin.strip() for origin in stripped.split(",") if origin.strip()]
        return value

    mone_api_url: str = ""
    mone_api_token: str = ""
    mone_customers_path: str = "/api/v1/customers"
    mone_project_path: str = "/api/v1/projects/{project_id}"
    mone_pricing_path: str = "/api/v1/pricing/calculate"
    mone_cutlist_path: str = "/api/v1/cutlists"
    mone_pipeline_path: str = "/api/v1/pipeline/run"

    system_instructions: str = (
        "أنت مساعد صوتي عربي طبيعي وسريع. تحدث بالعربية بوضوح واختصار. "
        "استخدم الأدوات عند الحاجة، ولا تخترع نتائجها. "
        "لا تنفذ عمليات مالية أو تغييرات حساسة دون طلب واضح وموافقة المستخدم. "
        "اسم المساعد: مساعد مروان."
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
