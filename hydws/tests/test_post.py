import json
import os
from copy import deepcopy

from config.config import get_settings

AUTH_HEADERS = {"X-API-Key": get_settings().API_KEY}


async def test_post(test_client):
    response = await test_client.post("/hydws/v1/boreholes",
                                      json=data_2,
                                      headers=AUTH_HEADERS)
    assert response.status_code == 200

    response = await test_client.post("/hydws/v1/boreholes",
                                      json=data_1,
                                      headers=AUTH_HEADERS)
    assert response.status_code == 200

    response = await test_client.get(f'/hydws/v1/boreholes/{data["publicid"]}',
                                     params={'level': 'hydraulic'})
    assert response.status_code == 200

    assert response.json()['sections'][0]['hydraulics'] == \
        data_1['sections'][0]['hydraulics']

    response = await test_client.delete(
        f"/hydws/v1/boreholes/{data['publicid']}",
        headers=AUTH_HEADERS)
    assert response.status_code == 204

    response = await test_client.get("/hydws/v1/boreholes")

    assert response.status_code == 404


async def test_merge(test_client):
    response = await test_client.post("/hydws/v1/boreholes",
                                      json=data_1,
                                      params={'merge': True},
                                      headers=AUTH_HEADERS)
    assert response.status_code == 200

    response = await test_client.post("/hydws/v1/boreholes",
                                      json=data_2,
                                      params={'merge': True},
                                      headers=AUTH_HEADERS)
    assert response.status_code == 200

    response = await test_client.get(f'/hydws/v1/boreholes/{data["publicid"]}',
                                     params={'level': 'hydraulic'})

    assert response.json()['sections'][0]['hydraulics'] == \
        data_3['sections'][0]['hydraulics']

    response = await test_client.delete(
        f"/hydws/v1/boreholes/{data['publicid']}",
        headers=AUTH_HEADERS)

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


async def test_delete_section_hydraulics(test_client):
    response = await test_client.post("/hydws/v1/boreholes",
                                      json=data_1,
                                      headers=AUTH_HEADERS)
    assert response.status_code == 200

    borehole_id = data["publicid"]
    section_id = data["sections"][0]["publicid"]

    response = await test_client.get(
        f'/hydws/v1/boreholes/{borehole_id}/sections/{section_id}/hydraulics')
    assert response.status_code == 200
    assert len(response.json()) == 8

    response = await test_client.delete(
        f"/hydws/v1/boreholes/{borehole_id}/sections/{section_id}/hydraulics",
        params={
            'starttime': '2021-01-01T00:00:00',
            'endtime': '2021-01-01T00:05:00'
        },
        headers=AUTH_HEADERS)
    assert response.status_code == 204

    response = await test_client.get(
        f'/hydws/v1/boreholes/{borehole_id}/sections/{section_id}/hydraulics')
    assert response.status_code == 200
    remaining = response.json()
    assert len(remaining) == 4
    for h in remaining:
        assert h['datetime']['value'] >= '2021-01-01T00:06:00'

    response = await test_client.delete(
        f"/hydws/v1/boreholes/{borehole_id}/sections/{section_id}/hydraulics",
        headers=AUTH_HEADERS)
    assert response.status_code == 204

    response = await test_client.get(
        f'/hydws/v1/boreholes/{borehole_id}/sections/{section_id}/hydraulics')
    assert response.status_code == 200
    assert response.json() == []

    response = await test_client.delete(
        f"/hydws/v1/boreholes/{borehole_id}",
        headers=AUTH_HEADERS)
    assert response.status_code == 204


async def test_delete_section_hydraulics_not_found(test_client):
    fake_borehole_id = "00000000-0000-0000-0000-000000000000"
    fake_section_id = "00000000-0000-0000-0000-000000000001"

    response = await test_client.delete(
        f"/hydws/v1/boreholes/{fake_borehole_id}/"
        f"sections/{fake_section_id}/hydraulics",
        headers=AUTH_HEADERS)
    assert response.status_code == 404
    assert response.json()["detail"] == "Borehole not found."

    response = await test_client.post("/hydws/v1/boreholes",
                                      json=data_1,
                                      headers=AUTH_HEADERS)
    assert response.status_code == 200

    borehole_id = data["publicid"]

    response = await test_client.delete(
        f"/hydws/v1/boreholes/{borehole_id}"
        f"/sections/{fake_section_id}/hydraulics",
        headers=AUTH_HEADERS)
    assert response.status_code == 404
    assert response.json()["detail"] == "Section not found."

    response = await test_client.delete(
        f"/hydws/v1/boreholes/{borehole_id}",
        headers=AUTH_HEADERS)
    assert response.status_code == 204
