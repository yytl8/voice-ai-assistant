from .settings import settings


def validate_production():
    if settings.app_env.lower() != "production":
        return []

    required = {
        "DATABASE_URL": settings.database_url,
        "AI_API_KEY": settings.ai_api_key,
    }

    if settings.jwt_secret == "CHANGE_ME_IN_PRODUCTION":
        required["JWT_SECRET"] = ""

    return [key for key, value in required.items() if not value]
