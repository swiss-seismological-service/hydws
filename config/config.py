from pydantic import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    POSTGRES_SERVER: str
    PGPORT: str

    APP_DB_USER: str
    APP_DB_PASSWORD: str
    APP_DB_NAME: str

    HYDWS_PREFIX: str = 'm_'

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
