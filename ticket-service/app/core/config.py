from pydantic_settings import SettingsConfigDict, BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "Ticket Service"
    app_version: str = ""
    log_level:str = "INFO"
    
    postgre_sql_url: str
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800

    # Must match auth-service, which signs the tokens
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")
    
@lru_cache
def get_settings():
    return Settings()
    