import asyncio
import uuid
from datetime import datetime
from typing import Literal

import pandas as pd
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import ORJSONResponse, PlainTextResponse
from starlette.status import HTTP_204_NO_CONTENT

from hydws import crud
from hydws.database import DBSessionDep
from hydws.datamodel.orm import HydraulicSample
from hydws.schemas import (BoreholeJSONSchema, BoreholeSchema,
                           HydraulicSampleSchema)
from hydws.utils import hydraulics_to_json

router = APIRouter(prefix='/boreholes', tags=['boreholes'])


@router.get("",
            response_model=list[BoreholeSchema],
            response_model_exclude_none=True)
async def get_boreholes(db: DBSessionDep,
                        starttime: datetime | None = None,
                        endtime: datetime | None = None,
                        minlatitude: float | None = None,
                        maxlatitude: float | None = None,
                        minlongitude: float | None = None,
                        maxlongitude: float | None = None):
    """
    Returns a list of projects.
    """
    db_result = await crud.read_boreholes(db,
                                          starttime,
                                          endtime,
                                          minlatitude,
                                          maxlatitude,
                                          minlongitude,
                                          maxlongitude)

    if not db_result:
        raise HTTPException(status_code=404, detail="No boreholes found.")

    return db_result


async def await_section_hydraulics(section, db, **kwargs):
    defer_cols = [HydraulicSample._boreholesection_oid]
    drop_cols = ['_oid']

    section_oid = await crud.read_section_oid(section['publicid'], db)

    df = await crud.read_hydraulics_df(
        section_oid, **kwargs, defer_cols=defer_cols)

    section['hydraulics'] = hydraulics_to_json(df, drop_cols)

    return section


@router.get("/{borehole_id}",
            response_model=BoreholeSchema,
            response_model_exclude_none=True)
async def get_borehole(borehole_id: uuid.UUID,
                       db: DBSessionDep,
                       level: str | None = 'section',
                       starttime: datetime | None = None,
                       endtime: datetime | None = None):
    """
    Returns a borehole.
    """
    if level == 'borehole':
        db_result = await crud.read_borehole(borehole_id, db)
    else:
        db_result = await crud.read_borehole(
            borehole_id, db, True, starttime, endtime)

    if not db_result:
        raise HTTPException(status_code=404, detail="Borehole not found.")

    borehole = BoreholeSchema.model_validate(db_result) \
        .model_dump(exclude_none=True)

    if level == 'hydraulic':
        futures = []
        for section in borehole['sections']:
            futures.append(
                await_section_hydraulics(
                    section,
                    db,
                    starttime=starttime,
                    endtime=endtime))

        borehole['sections'] = await asyncio.gather(*futures)

    return ORJSONResponse(borehole)


@router.post("",
             response_model=BoreholeSchema,
             response_model_exclude_none=True)
async def post_borehole(
        borehole: BoreholeJSONSchema,
        db: DBSessionDep):

    flattened = borehole.flat_dict(exclude_unset=True)
    result = await crud.create_borehole(flattened, db)
    return result


@router.delete("/{borehole_id}",
               status_code=HTTP_204_NO_CONTENT,
               response_class=Response)
async def delete_borehole(borehole_id: uuid.UUID,
                          db: DBSessionDep) -> None:

    deleted = await crud.delete_borehole(borehole_id, db)

    if deleted == 0:
        raise HTTPException(status_code=404, detail="No boreholes found.")


def csv_response(data) -> PlainTextResponse:
    numeric_columns = data.select_dtypes(include='number').columns
    data[numeric_columns] = data[numeric_columns].fillna(0)

    if 'datetime_value' in data.columns:
        data = data.sort_values(by='datetime_value')
        data['datetime_value'] = pd.to_datetime(
            data['datetime_value']).dt.strftime('%Y-%m-%dT%H:%M:%S')

    data = data.to_csv(index=False)
    return PlainTextResponse(data, media_type='text/csv')


@ router.get("/{borehole_id}/sections/{section_id}/hydraulics",
             response_model=list[HydraulicSampleSchema],
             response_model_exclude_none=True)
async def get_section_hydraulics(borehole_id: uuid.UUID,
                                 section_id: uuid.UUID,
                                 db: DBSessionDep,
                                 starttime: datetime | None = None,
                                 endtime: datetime | None = None,
                                 format: Literal['csv', 'json'] = 'json',
                                 ):
    """
    Returns section hydraulics.
    """

    db_borehole = await crud.read_borehole(borehole_id, db)
    if not db_borehole:
        raise HTTPException(status_code=404, detail="Borehole not found.")

    defer_cols = [HydraulicSample._oid,
                  HydraulicSample._boreholesection_oid]

    section_oid = await crud.read_section_oid(section_id, db)

    db_result_df = await crud.read_hydraulics_df(
        section_oid, starttime, endtime, defer_cols)

    db_result_df = db_result_df.dropna(axis=1, how='all').drop(columns=['_oid'])

    if format == 'csv':
        return csv_response(db_result_df)

    if db_result_df.empty:
        return []

    results = hydraulics_to_json(db_result_df)

    return ORJSONResponse(results)
