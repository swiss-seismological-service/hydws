import json
import os

import pytest
from httpx import ASGITransport, AsyncClient

from hydws.main import app

dirname = os.path.dirname(os.path.abspath(__file__))

HYDRAULICS_1 = [
    {
        "datetime_value": "2021-01-01T00:00:00",
        "toppressure": {"value": 1.0},
        "topflow": {"value": 1.0}
    },
    {
        "datetime_value": "2021-01-01T01:00:00",
        "toppressure": {"value": 2.0},
        "topflow": {"value": 2.0}
    },
    {
        "datetime_value": "2021-01-01T02:00:00",
        "toppressure": {"value": 3.0},
        "topflow": {"value": 3.0}
    },
    {
        "datetime_value": "2021-01-01T03:00:00",
        "toppressure": {"value": 4.0},
        "topflow": {"value": 4.0}
    },
    {
        "datetime_value": "2021-01-01T04:00:00",
        "toppressure": {"value": 5.0},
        "topflow": {"value": 5.0}
    },
    {
        "datetime_value": "2021-01-01T05:00:00",
        "toppressure": {"value": 6.0},
        "topflow": {"value": 6.0}
    },
    {
        "datetime_value": "2021-01-01T06:00:00",
        "toppressure": {"value": 7.0},
        "topflow": {"value": 7.0}
    },
    {
        "datetime_value": "2021-01-01T07:00:00",
        "toppressure": {"value": 8.0},
        "topflow": {"value": 8.0}
    },
    {
        "datetime_value": "2021-01-01T08:00:00",
        "toppressure": {"value": 9.0},
        "topflow": {"value": 9.0}
    },
    {
        "datetime_value": "2021-01-01T09:00:00",
        "toppressure": {"value": 10.0},
        "topflow": {"value": 10.0}
    }
]

HYDRAULICS_2 = [
    {
        "datetime_value": "2021-01-01T00:00:00",
        "toppressure": {"value": 1.0},
        "topflow": {"value": 1.0}
    },
    {
        "datetime_value": "2021-01-01T00:30:00",
        "toppressure": {"value": 1.5},
        "topflow": {"value": 1.5}
    },
    {
        "datetime_value": "2021-01-01T01:00:00",
        "toppressure": {"value": 2.0},
        "topflow": {"value": 2.0}
    },
    {
        "datetime_value": "2021-01-01T01:30:00",
        "toppressure": {"value": 2.5},
        "topflow": {"value": 2.5}
    },
    {
        "datetime_value": "2021-01-01T02:00:00",
        "toppressure": {"value": 3.0},
        "topflow": {"value": 3.0}
    },
    {
        "datetime_value": "2021-01-01T02:30:00",
        "toppressure": {"value": 3.5},
        "topflow": {"value": 3.5}
    },
    {
        "datetime_value": "2021-01-01T03:00:00",
        "toppressure": {"value": 4.0},
        "topflow": {"value": 4.0}
    },
    {
        "datetime_value": "2021-01-01T03:30:00",
        "toppressure": {"value": 4.5},
        "topflow": {"value": 4.5}
    },
    {
        "datetime_value": "2021-01-01T04:00:00",
        "toppressure": {"value": 5.0},
        "topflow": {"value": 5.0}
    },
    {
        "datetime_value": "2021-01-01T04:30:00",
        "toppressure": {"value": 5.5},
        "topflow": {"value": 5.5}
    },
    {
        "datetime_value": "2021-01-01T05:00:00",
        "toppressure": {"value": 6.0},
        "topflow": {"value": 6.0}
    }
]


@pytest.mark.anyio
async def test_merge():
    with open(os.path.join(dirname, 'data.json'), 'r') as file:
        data = json.load(file)

    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test") as client:
        response = await client.post("/hydws/v1/boreholes", json=data)
        assert response.status_code == 200

        response = await client.delete(
            f"/hydws/v1/boreholes/{data['publicid']}")
        assert response.status_code == 204
