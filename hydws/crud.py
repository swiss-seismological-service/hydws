from datetime import datetime
from typing import List, Optional

import pandas as pd
from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session, contains_eager, defer, joinedload

from hydws.datamodel.orm import Borehole, BoreholeSection, HydraulicSample
from hydws.utils import update_section_epoch


def read_boreholes(db: Session,
                   starttime: Optional[datetime] = None,
                   endtime: Optional[datetime] = None,
                   minlatitude: Optional[float] = None,
                   maxlatitude: Optional[float] = None,
                   minlongitude: Optional[float] = None,
                   maxlongitude: Optional[float] = None) -> List[Borehole]:

    statement = select(Borehole).options(joinedload(Borehole.sections))

    if starttime or endtime:
        statement = statement.join(BoreholeSection)
    if starttime:
        statement = statement.where(BoreholeSection.endtime >= starttime)
    if endtime:
        statement = statement.where(BoreholeSection.starttime <= endtime)
    if minlongitude:
        statement = statement.where(Borehole.longitude_value >= minlongitude)
    if maxlongitude:
        statement = statement.where(Borehole.longitude_value <= maxlongitude)
    if minlatitude:
        statement = statement.where(Borehole.latitude_value >= minlatitude)
    if maxlatitude:
        statement = statement.where(Borehole.latitude_value <= maxlatitude)

    return db.execute(statement).unique().scalars().all()


def read_borehole(borehole_id: str,
                  db: Session,
                  sections: bool = False,
                  starttime: datetime = None,
                  endtime: datetime = None) -> Borehole:

    statement = select(Borehole).where(Borehole.publicid == borehole_id)

    if sections:
        statement = statement.outerjoin(BoreholeSection) \
            .options(contains_eager(Borehole.sections))

        if starttime:
            statement = statement.where(BoreholeSection.endtime > starttime)
        if endtime:
            statement = statement.where(BoreholeSection.starttime < endtime)

    return db.execute(statement).unique().scalar_one_or_none()


def delete_borehole(publicid: str, db: Session):
    stmt = delete(Borehole).where(Borehole.publicid == publicid)
    deleted = db.execute(stmt)
    db.commit()
    return deleted.rowcount


def create_borehole(borehole: dict, db: Session):
    borehole_db = read_borehole(borehole['publicid'], db)

    sections = borehole.pop('sections', None)

    if borehole_db:
        for key, value in borehole.items():
            setattr(borehole_db, key, value)
    else:
        borehole_db = Borehole(**borehole)
        db.add(borehole_db)

    db.commit()

    if sections:
        for section in sections:
            create_section(section, borehole_db._oid, db)

    return borehole_db


def read_sections(db: Session) -> List[BoreholeSection]:
    statement = select(Borehole)
    return db.execute(statement).unique().scalars().all()


def read_section(section_id: str, db: Session):
    statement = select(BoreholeSection)
    statement = statement.where(
        BoreholeSection.publicid == section_id)
    return db.execute(statement).scalar_one_or_none()


def create_section(section: dict,
                   borehole_oid: int,
                   db: Session):

    section_db = read_section(section['publicid'], db)

    section = update_section_epoch(section_db,
                                   section, db)

    hydraulics = section.pop('hydraulics', None)

    if section_db:
        for key, value in section.items():
            setattr(section_db, key, value)
    else:
        section_db = BoreholeSection(**section, _borehole_oid=borehole_oid)
        db.add(section_db)

    db.commit()

    if hydraulics:
        create_hydraulics(hydraulics, section_db._oid, db)

    return section_db


def read_hydraulics(section_id: str,
                    db: Session,
                    starttime: datetime = None,
                    endtime: datetime = None) -> List[HydraulicSample]:

    statement = select(HydraulicSample) \
        .where(HydraulicSample._boreholesection_oid == BoreholeSection._oid)\
        .where(BoreholeSection.publicid == section_id)\

    if starttime:
        statement = statement.where(
            HydraulicSample.datetime_value >= starttime)
    if endtime:
        statement = statement.where(
            HydraulicSample.datetime_value <= endtime)

    return db.execute(statement).unique().scalars().all()


def read_hydraulics_df(
        section_id: str,
        db: Session,
        starttime: datetime = None,
        endtime: datetime = None,
        defer_cols: list = None) -> List[HydraulicSample]:

    statement = select(HydraulicSample) \
        .join(BoreholeSection) \
        .where(BoreholeSection.publicid == section_id)

    if defer_cols:
        statement = statement.options(*[defer(col) for col in defer_cols])

    if starttime:
        statement = statement.where(
            HydraulicSample.datetime_value >= starttime)
    if endtime:
        statement = statement.where(
            HydraulicSample.datetime_value <= endtime)

    return pd.read_sql(statement, db.get_bind())


def create_hydraulics(
        hydraulics: List[dict],
        section_oid: int,
        db: Session):

    datetimes = [h['datetime_value'] for h in hydraulics]
    start = min(datetimes)
    end = max(datetimes)

    statement = delete(HydraulicSample) \
        .where(HydraulicSample._boreholesection_oid == section_oid) \
        .where(HydraulicSample.datetime_value > start) \
        .where(HydraulicSample.datetime_value < end) \
        .execution_options(synchronize_session=False)

    db.execute(statement)

    db.execute(insert(HydraulicSample).values(_boreholesection_oid=section_oid),
               hydraulics)
    db.commit()
