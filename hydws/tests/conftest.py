import os
import subprocess

import asyncpg
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from config import get_settings
from hydws.database import sessionmanager
from hydws.main import app

pytest_plugins = ['anyio']


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def setup_test_database():
    settings = get_settings()
    db_name = f"{settings.DB_NAME}_test"

    conn = await asyncpg.connect(
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        port=int(settings.POSTGRES_PORT),
        database='postgres'
    )
    await conn.execute(f'DROP DATABASE IF EXISTS {db_name}')
    await conn.execute(f'CREATE DATABASE {db_name}')
    await conn.close()

    env = os.environ.copy()
    env['TESTING'] = '1'
    subprocess.run(["alembic", "upgrade", "head"], check=True, env=env)

    async with sessionmanager.connect() as conn:
        await conn.execute(text(
            "CALL generate_partitioned_tables('2021-01-01', '2021-01-02')"
        ))
        await conn.commit()

    yield

    if sessionmanager._engine is not None:
        await sessionmanager.close()


@pytest.fixture
async def test_client(setup_test_database):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
