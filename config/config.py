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

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        db_name = f"{self.DB_NAME}_test" if self.TESTING else self.DB_NAME
        return f"postgresql+asyncpg://{self.DB_USER}:" \
            f"{self.DB_PASSWORD}@" \
            f"{self.POSTGRES_HOST}:" \
            f"{self.POSTGRES_PORT}/{db_name}"


@lru_cache()
def get_settings():
    return Settings()
