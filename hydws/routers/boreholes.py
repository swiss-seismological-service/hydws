from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import base64

from hydws.schemas import BoreholeSchema
from hydws import crud
from hydws.dependencies import get_db

router = APIRouter(prefix='/boreholes', tags=['boreholes'])


@router.get("/",
            response_model=List[BoreholeSchema],
            response_model_exclude_none=True)
async def read_boreholes(db: Session = Depends(get_db)):
    """
    Returns a list of projects.
    """
    db_result = crud.get_boreholes(db)

    if not db_result:
        raise HTTPException(status_code=404, detail="No boreholes found.")
    return db_result


@router.get("/{borehole_id}",
            response_model=BoreholeSchema,
            response_model_exclude_none=True)
async def read_borehole_hydraulics(borehole_id: str,
                                   db: Session = Depends(get_db),
                                   level: Optional[str] = 'section',
                                   starttime: Optional[datetime] = None,
                                   endtime: Optional[datetime] = None):
    """
    Returns a borehole.
    """
    borehole_id = base64.b64decode(borehole_id).decode("utf-8")

    db_result = crud.get_borehole_hydraulics(
        borehole_id, db, level, starttime, endtime)

    if not db_result:
        raise HTTPException(status_code=404, detail="No boreholes found.")

    return db_result
