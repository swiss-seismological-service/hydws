from datetime import datetime
from sqlalchemy.orm import Session, joinedload, contains_eager
from sqlalchemy import select
from typing import List

from hydws.datamodel.orm import Borehole, BoreholeSection, HydraulicSample


def get_boreholes(db: Session) -> List[Borehole]:
    statement = select(Borehole).options(joinedload(Borehole._sections))
    result = db.execute(statement).unique().all()
    return [r[0] for r in result]


def get_borehole_hydraulics(
        borehole_id: str,
        db: Session,
        level: str = 'section',
        starttime: datetime = None,
        endtime: datetime = None) -> Borehole:

    level_options = None
    time_query_start = None
    time_query_end = None

    statement = select(Borehole)

    if level != 'borehole':  # section or hydraulic
        statement = statement.join(BoreholeSection)
        level_options = contains_eager(Borehole._sections)
        # compare if epoch has overlap, counterintuitive query
        time_query_start = BoreholeSection.endtime
        time_query_end = BoreholeSection.starttime
    if level == 'hydraulic':
        statement = statement.join(HydraulicSample)
        level_options = level_options.contains_eager(
            BoreholeSection._hydraulics)
        time_query_start = HydraulicSample.datetime_value
        time_query_end = HydraulicSample.datetime_value

    if level_options:
        statement = statement.options(level_options)
    statement = statement.where(
        Borehole.publicid == borehole_id)

    if starttime:
        statement = statement.where(time_query_start > starttime)
    if endtime:
        statement = statement.where(time_query_end < endtime)

    result = db.execute(statement).scalars().unique().one_or_none()

    return result
