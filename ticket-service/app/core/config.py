from pydantic_settings import SettingsConfigDict, BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = ""
    app_version: str = ""
    log_level:str = "INFO"
    postgre_sql_url: str = ""
    model_config = SettingsConfigDict(env_file="../.env", ignored_types="mode")
    
@lru_cache
def get_settings():
    return Settings()
    