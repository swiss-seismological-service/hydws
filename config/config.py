from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    POSTGRES_HOST: str
    POSTGRES_PORT: str

    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    ALLOW_ORIGINS: list
    ALLOW_ORIGIN_REGEX: str

    API_KEY: str = ""  # Empty = protection disabled

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:" \
            f"{self.DB_PASSWORD}@" \
            f"{self.POSTGRES_HOST}:" \
            f"{self.POSTGRES_PORT}/{self.DB_NAME}"


@lru_cache()
def get_settings():
    return Settings()
