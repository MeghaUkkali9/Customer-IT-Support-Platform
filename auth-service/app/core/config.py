from pydantic_settings import SettingsConfigDict, BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "Auth Service"
    log_level: str = "INFO"

    postgre_sql_url: str
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800

    # Shared with every service that verifies tokens
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings():
    return Settings()
