from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    max_attachment_bytes: int = 12 * 1024 * 1024
    log_level: str = "INFO"
    allowed_origins: str = ""
    environment: str = "development"
    app_env: str = "development"
    database_url: str = "postgresql+asyncpg://voice:voice@localhost:5432/voice_ai"
    ai_base_url: str = "https://api.openai.com/v1"
    ai_api_key: str = ""
    attachment_dir: str = "/tmp/voice-ai-attachments"
    rate_limit_per_minute: int = 60
    tool_rate_limit_per_minute: int = 30
    ai_model: str = "gpt-realtime-2.1"
    voice_name: str = "marin"

    jwt_secret: str = "CHANGE_ME_IN_PRODUCTION"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60
    refresh_token_days: int = 30

    cors_origins: list[str] = ["http://localhost:3000"]
    max_request_body_mb: int = 15
    rate_limit_per_minute: int = 60

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
