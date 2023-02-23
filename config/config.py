from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    POSTGRES_HOST: str
    PGPORT: str

    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    HYDWS_PREFIX: str = 'm_'

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
