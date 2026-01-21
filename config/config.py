from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    TESTING: bool = False

    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""

    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    ALLOW_ORIGINS: list
    ALLOW_ORIGIN_REGEX: str

    API_KEY: str = ""  # Empty = protection disabled
    LOG_LEVEL: str = "INFO"

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        if self.TESTING:
            db_name = f"{self.DB_NAME}_test"
            user = self.POSTGRES_USER
            password = self.POSTGRES_PASSWORD
        else:
            db_name = self.DB_NAME
            user = self.DB_USER
            password = self.DB_PASSWORD
        return f"postgresql+asyncpg://{user}:{password}@" \
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{db_name}"


@lru_cache()
def get_settings():
    return Settings()
