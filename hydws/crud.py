from datetime import datetime
from sqlalchemy.orm import Session, joinedload, contains_eager
from sqlalchemy import select, update, delete  # noqa
from typing import List, Union

from hydws.datamodel.orm import Borehole, BoreholeSection, HydraulicSample


def read_boreholes(db: Session) -> List[Borehole]:
    statement = select(Borehole).options(joinedload(Borehole._sections))
    return db.execute(statement).unique().scalars().all()


def read_borehole(borehole_id: str, db: Session) -> Borehole:
    statement = select(Borehole).where(Borehole.publicid == borehole_id)
    return db.execute(statement).scalar_one_or_none()


def read_borehole_level(
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
        statement = statement.outerjoin(BoreholeSection)
        level_options = contains_eager(Borehole._sections)
        # compare if epoch has overlap, counterintuitive query
        time_query_start = BoreholeSection.endtime
        time_query_end = BoreholeSection.starttime
    if level == 'hydraulic':
        statement = statement.outerjoin(HydraulicSample)
        level_options = level_options.contains_eager(
            BoreholeSection._hydraulics)
        time_query_start = HydraulicSample.datetime_value
        time_query_end = HydraulicSample.datetime_value

    if level_options:
        statement = statement.options(level_options)

    statement = statement.where(Borehole.publicid == borehole_id)

    if starttime:
        statement = statement.where(time_query_start > starttime)
    if endtime:
        statement = statement.where(time_query_end < endtime)

    result = db.execute(statement).unique().scalar_one_or_none()
    return result


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

    if sections:
        for section in sections:
            create_section(section, borehole_db, db, commit=False)

    db.commit()
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
                   borehole: Union[str, Borehole],
                   db: Session,
                   commit: bool = True):

    if isinstance(borehole, str):
        borehole = read_borehole(borehole, db)
    if not section:
        raise KeyError(f'Borehole with publicID {borehole} does not exist.')

    section_db = read_section(section['publicid'], db)
    hydraulics = section.pop('hydraulics', None)

    if section_db:
        for key, value in section.items():
            setattr(section_db, key, value)
    else:
        section_db = BoreholeSection(**section)
        db.add(section_db)

    if hydraulics:
        merge_hydraulics(hydraulics, section_db, db, False)

    if commit:
        db.commit()
    return section_db


def merge_hydraulics(
        hydraulics: List[dict],
        section: Union[str, BoreholeSection],
        db: Session,
        commit: bool = True):

    if isinstance(section, str):
        section = read_section(section, db)
    if not section:
        raise KeyError(f'Section with publicID {section} does not exist.')

    datetimes = [h['datetime_value'] for h in hydraulics]
    start = min(datetimes)
    end = max(datetimes)

    statement = delete(HydraulicSample) \
        .where(HydraulicSample.boreholesection_oid == BoreholeSection._oid) \
        .where(BoreholeSection.publicid == section.publicid) \
        .where(HydraulicSample.datetime_value > start)\
        .where(HydraulicSample.datetime_value < end) \
        .execution_options(synchronize_session=False)

    db.execute(statement)

    samples = [HydraulicSample(**s, _section=section) for s in hydraulics]
    db.add_all(samples)

    if commit:
        db.commit()

    return samples
