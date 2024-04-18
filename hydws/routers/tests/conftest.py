import pytest
from httpx import ASGITransport, AsyncClient

from hydws.database import sessionmanager
from hydws.datamodel.base import ORMBase
from hydws.main import app


@pytest.fixture(scope="session", autouse=True)
async def init():
    if sessionmanager._engine:
        async with sessionmanager.connect() as con:
            await con.run_sync(ORMBase.metadata.create_all)

    yield

    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()


@pytest.fixture(scope="session")
def anyio_backend():
    return 'asyncio'


@pytest.fixture(scope="session")
async def test_client():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test") as client:
        yield client
