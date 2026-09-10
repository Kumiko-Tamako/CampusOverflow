from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CampusOverflow"
    debug: bool = False
    database_url: str = "postgresql+asyncpg://campus:campus@localhost:5432/campus"
    redis_url: str = "redis://localhost:6379/0"
    # JWT 签名密钥：默认仅开发用，生产必须从环境变量覆盖（.env 不入库）
    jwt_secret: str = "dev-secret-change-me-in-production"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
