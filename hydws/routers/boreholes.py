from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List, Optional
import base64
from starlette.status import HTTP_204_NO_CONTENT

from hydws.schemas import BoreholeSchema
from hydws import crud
from hydws.dependencies import get_db

router = APIRouter(prefix='/boreholes', tags=['boreholes'])


@router.get("/",
            response_model=List[BoreholeSchema],
            response_model_exclude_none=True)
async def get_boreholes(db: Session = Depends(get_db)):
    """
    Returns a list of projects.
    """
    db_result = crud.read_boreholes(db)

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
        borehole_id = base64.b64decode(borehole_id).decode("utf-8")
    except BaseException:
        raise HTTPException(status_code=400,
                            detail="Borehole ID is not valid Base 64.")
    db_result = crud.read_borehole_level(
        borehole_id, db, level, starttime, endtime)

    if not db_result:
        raise HTTPException(status_code=404, detail="No boreholes found.")

    return db_result


@router.post("/", response_model=BoreholeSchema,
             response_model_exclude_none=True)
async def post_borehole(
        borehole: BoreholeSchema, db: Session = Depends(get_db)):
    return crud.create_borehole(
        borehole.flat_dict(exclude_unset=True), db)


@router.delete("/{borehole_id}", status_code=HTTP_204_NO_CONTENT,
               response_class=Response)
async def delete_borehole(borehole_id: str,
                          db: Session = Depends(get_db)) -> None:
    try:
        borehole_id = base64.b64decode(borehole_id).decode("utf-8")
    except BaseException:
        raise HTTPException(status_code=400,
                            detail="Borehole ID is not valid Base 64.")

    deleted = crud.delete_borehole(borehole_id, db)

    if deleted == 0:
        raise HTTPException(status_code=404, detail="No boreholes found.")
