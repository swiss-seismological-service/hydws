import json
import os
from copy import deepcopy

import pytest


@pytest.mark.anyio
async def test_post(test_client):
    response = await test_client.post("/hydws/v1/boreholes",
                                      json=data_2)
    assert response.status_code == 200

    response = await test_client.post("/hydws/v1/boreholes",
                                      json=data_1)
    assert response.status_code == 200

    response = await test_client.get(f'/hydws/v1/boreholes/{data["publicid"]}',
                                     params={'level': 'hydraulic'})
    assert response.status_code == 200

    assert response.json()['sections'][0]['hydraulics'] == \
        data_1['sections'][0]['hydraulics']

    response = await test_client.delete(
        f"/hydws/v1/boreholes/{data['publicid']}")
    assert response.status_code == 204

    response = await test_client.get("/hydws/v1/boreholes")

    assert response.status_code == 404


@pytest.mark.anyio
async def test_merge(test_client):
    response = await test_client.post("/hydws/v1/boreholes",
                                      json=data_1,
                                      params={'merge': True})
    assert response.status_code == 200

    response = await test_client.post("/hydws/v1/boreholes",
                                      json=data_2,
                                      params={'merge': True})
    assert response.status_code == 200

    response = await test_client.get(f'/hydws/v1/boreholes/{data["publicid"]}',
                                     params={'level': 'hydraulic'})

    assert response.json()['sections'][0]['hydraulics'] == \
        data_3['sections'][0]['hydraulics']

    response = await test_client.delete(
        f"/hydws/v1/boreholes/{data['publicid']}")

    assert response.status_code == 204

    response = await test_client.get("/hydws/v1/boreholes")

    assert response.status_code == 404


dirname = os.path.dirname(os.path.abspath(__file__))

HYDRAULICS_1 = [
    {
        "datetime": {"value": "2021-01-01T00:00:00"},
        "toppressure": {"value": 1.0},
    },
    {
        "datetime": {"value": "2021-01-01T00:03:00"},
        "toppressure": {"value": 4.0},
    },
    {
        "datetime": {"value": "2021-01-01T00:04:00"},
        "toppressure": {"value": 5.0},
    },
    {
        "datetime": {"value": "2021-01-01T00:05:00"},
        "toppressure": {"value": 6.0},
    },
    {
        "datetime": {"value": "2021-01-01T00:06:00"},
        "toppressure": {"value": 7.0},
    },
    {
        "datetime": {"value": "2021-01-01T00:07:00"},
        "toppressure": {"value": 8.0},
    },
    {
        "datetime": {"value": "2021-01-01T00:08:00"},
        "toppressure": {"value": 9.0},
    },
    {
        "datetime": {"value": "2021-01-01T00:09:00"},
        "toppressure": {"value": 10.0},
    }
]

HYDRAULICS_2 = [
    {
        "datetime": {"value": "2021-01-01T00:00:00"},
        "topflow": {"value": 1.0}
    },
    {
        "datetime": {"value": "2021-01-01T00:00:30"},
        "topflow": {"value": 1.5}
    },
    {
        "datetime": {"value": "2021-01-01T00:01:00"},
        "topflow": {"value": 2.0}
    },
    {
        "datetime": {"value": "2021-01-01T00:01:30"},
        "topflow": {"value": 2.5}
    },
    {
        "datetime": {"value": "2021-01-01T00:02:00"},
        "topflow": {"value": 3.0}
    },
    {
        "datetime": {"value": "2021-01-01T00:02:30"},
        "topflow": {"value": 3.5}
    },
    {
        "datetime": {"value": "2021-01-01T00:03:00"},
        "topflow": {"value": 4.0}
    },
    {
        "datetime": {"value": "2021-01-01T00:03:30"},
        "topflow": {"value": 4.5}
    },
    {
        "datetime": {"value": "2021-01-01T00:04:00"},
        "topflow": {"value": 5.0}
    },
    {
        "datetime": {"value": "2021-01-01T00:04:30"},
        "topflow": {"value": 5.5}
    },
    {
        "datetime": {"value": "2021-01-01T00:05:00"},
        "topflow": {"value": 6.0}
    }
]

HYDRAULICS_3 = [
    {'datetime': {'value': '2021-01-01T00:00:00'},
     'topflow': {'value': 1.0},
     'toppressure': {'value': 1.0}},
    {'datetime': {'value': '2021-01-01T00:00:30'},
     'topflow': {'value': 1.5}},
    {'datetime': {'value': '2021-01-01T00:01:00'},
     'topflow': {'value': 2.0}},
    {'datetime': {'value': '2021-01-01T00:01:30'},
     'topflow': {'value': 2.5}},
    {'datetime': {'value': '2021-01-01T00:02:00'},
     'topflow': {'value': 3.0}},
    {'datetime': {'value': '2021-01-01T00:02:30'},
     'topflow': {'value': 3.5}},
    {'datetime': {'value': '2021-01-01T00:03:00'},
     'topflow': {'value': 4.0},
     'toppressure': {'value': 4.0}},
    {'datetime': {'value': '2021-01-01T00:03:30'},
     'topflow': {'value': 4.5},
     'toppressure': {'value': 4.0}},
    {'datetime': {'value': '2021-01-01T00:04:00'},
     'topflow': {'value': 5.0},
     'toppressure': {'value': 5.0}},
    {'datetime': {'value': '2021-01-01T00:04:30'},
     'topflow': {'value': 5.5},
     'toppressure': {'value': 5.0}},
    {'datetime': {'value': '2021-01-01T00:05:00'},
     'topflow': {'value': 6.0},
     'toppressure': {'value': 6.0}},
    {'datetime': {'value': '2021-01-01T00:06:00'},
     'toppressure': {'value': 7.0}},
    {'datetime': {'value': '2021-01-01T00:07:00'},
     'toppressure': {'value': 8.0}},
    {'datetime': {'value': '2021-01-01T00:08:00'},
     'toppressure': {'value': 9.0}},
    {'datetime': {'value': '2021-01-01T00:09:00'},
     'toppressure': {'value': 10.0}}]


with open(os.path.join(dirname, 'data.json'), 'r') as file:
    data = json.load(file)

data_1 = deepcopy(data)
data_1['sections'][0]['hydraulics'] = HYDRAULICS_1

data_2 = deepcopy(data)
data_2['sections'][0]['hydraulics'] = HYDRAULICS_2

data_3 = deepcopy(data)
data_3['sections'][0]['hydraulics'] = HYDRAULICS_3
