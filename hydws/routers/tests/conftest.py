import pytest
from httpx import ASGITransport, AsyncClient

from hydws.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return 'asyncio'


@pytest.fixture(scope="session")
async def test_client():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test") as client:
        yield client
