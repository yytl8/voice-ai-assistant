from .settings import settings
def validate_production():
    if settings.environment.lower()!="production": return []
    vals={"DATABASE_URL":settings.database_url,"REDIS_URL":settings.redis_url,
          "MONE_API_URL":settings.mone_api_url,
          "MONE_API_TOKEN":settings.mone_api_token}
    return [k for k,v in vals.items() if not v]
