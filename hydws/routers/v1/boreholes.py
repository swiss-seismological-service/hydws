import base64
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from starlette.status import HTTP_204_NO_CONTENT

from hydws import crud
from hydws.dependencies import get_db
from hydws.schemas import BoreholeSchema, HydraulicSampleSchema

router = APIRouter(prefix='/boreholes', tags=['boreholes'])


@router.get("/",
            response_model=List[BoreholeSchema],
            response_model_exclude_none=True)
async def get_boreholes(db: Session = Depends(get_db),
                        starttime: Optional[datetime] = None,
                        endtime: Optional[datetime] = None,
                        minlatitude: Optional[float] = None,
                        maxlatitude: Optional[float] = None,
                        minlongitude: Optional[float] = None,
                        maxlongitude: Optional[float] = None):
    """
    Returns a list of projects.
    """
    db_result = crud.read_boreholes(
        db,
        starttime,
        endtime,
        minlatitude,
        maxlatitude,
        minlongitude,
        maxlongitude)

    if not db_result:
        raise HTTPException(status_code=404, detail="No boreholes found.")
    return db_result


@router.get("/{borehole_id}",
            response_model=BoreholeSchema,
            response_model_exclude_none=True)
async def get_borehole(borehole_id: str,
                       db: Session = Depends(get_db),
                       level: Optional[str] = 'section',
                       starttime: Optional[datetime] = None,
                       endtime: Optional[datetime] = None):
    """
    Returns a borehole.
    """
    try:
        borehole_id = uuid.UUID(borehole_id, version=4)
    except ValueError:
        raise HTTPException(status_code=400,
                            detail="Borehole ID is not valid UUID.")

    if level == 'borehole':
        db_result = crud.read_borehole(borehole_id, db)
    if level == 'section':
        db_result = crud.read_borehole_sections(
            borehole_id, db, starttime, endtime)

    # TODO: LEVEL HYDRAULICS

    if not db_result:
        raise HTTPException(status_code=404, detail="Borehole not found.")

    return db_result


@router.post("/",
             response_model=BoreholeSchema,
             response_model_exclude_none=True)
async def post_borehole(
        borehole: BoreholeSchema, db: Session = Depends(get_db)):
    try:
        result = crud.create_borehole(
            borehole.flat_dict(exclude_unset=True), db)
    except KeyError as k:
        raise HTTPException(status_code=404, detail=str(k))
    except ValueError as v:
        raise HTTPException(status_code=422, detail=str(v))
    except BaseException as e:
        raise HTTPException(status_code=500, detail=str(e))

    return result


@router.delete("/{borehole_id}",
               status_code=HTTP_204_NO_CONTENT,
               response_class=Response)
async def delete_borehole(borehole_id: str,
                          db: Session = Depends(get_db)) -> None:
    try:
        borehole_id = uuid.UUID(borehole_id, version=4)
    except ValueError:
        raise HTTPException(status_code=400,
                            detail="Borehole ID is not valid UUID.")

    deleted = crud.delete_borehole(borehole_id, db)

    if deleted == 0:
        raise HTTPException(status_code=404, detail="No boreholes found.")


@router.get("/{borehole_id}/sections/{section_id}/hydraulics",
            response_model=List[HydraulicSampleSchema],
            response_model_exclude_none=True)
async def get_section_hydraulics(borehole_id: str,
                                 section_id: str,
                                 db: Session = Depends(get_db),
                                 starttime: Optional[datetime] = None,
                                 endtime: Optional[datetime] = None):
    """
    Returns a section.
    """
    try:
        borehole_id = base64.b64decode(borehole_id).decode("utf-8")
    except BaseException:
        raise HTTPException(status_code=400,
                            detail="Borehole ID is not valid Base 64.")
    db_borehole = crud.read_borehole(borehole_id, db)
    if not db_borehole:
        raise HTTPException(status_code=404, detail="Borehole not found.")

    try:
        section_id = base64.b64decode(section_id).decode("utf-8")
    except BaseException:
        raise HTTPException(status_code=400,
                            detail="Section ID is not valid Base 64.")
    db_result = crud.read_hydraulics(section_id, db, starttime, endtime)

    if not db_result:
        raise HTTPException(status_code=404,
                            detail="No hydraulics that match the criteria.")

    return db_result
