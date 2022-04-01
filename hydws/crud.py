from datetime import datetime
from sqlalchemy.orm import Session, joinedload, contains_eager
from sqlalchemy import select, delete
from sqlalchemy.sql import func
from typing import List, Optional, Union

from hydws.datamodel.orm import Borehole, BoreholeSection, HydraulicSample


def read_boreholes(db: Session,
                   starttime: Optional[datetime] = None,
                   endtime: Optional[datetime] = None,
                   minlatitude: Optional[float] = None,
                   maxlatitude: Optional[float] = None,
                   minlongitude: Optional[float] = None,
                   maxlongitude: Optional[float] = None) -> List[Borehole]:

    statement = select(Borehole).options(joinedload(Borehole._sections))

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


def update_section_epoch(
        section_db: BoreholeSection,
        section_new: dict,
        db: Session) -> None:

    start_new = section_new.get('starttime', None)
    end_new = section_new.get('endtime', None)
    hydraulics = section_new.get('hydraulics', None)

    if hydraulics:
        datetimes = [h['datetime_value'] for h in section_new['hydraulics']]
        min_hyd = min(datetimes)
        max_hyd = max(datetimes)
        start_new = min(min_hyd, start_new or min_hyd)
        end_new = max(max_hyd, end_new or max_hyd)

    if not section_db:
        if not start_new or not end_new:
            raise ValueError('Sections without hydraulics attached must have'
                             ' starttime and endtime defined.')
        else:
            section_new['starttime'] = start_new
            section_new['endtime'] = end_new
    else:
        if start_new:
            if start_new < section_db.starttime:
                section_new['starttime'] = start_new
            else:
                min_db = db.execute(
                    select(func.min(
                        HydraulicSample.datetime_value)).where(
                        HydraulicSample.boreholesection_oid
                        == section_db._oid)).scalar()
                print(min_db)
                print(start_new)
                section_new['starttime'] = min(start_new, min_db)
        if end_new:
            if end_new > section_db.endtime:
                section_new['endtime'] = end_new
            else:
                max_db = db.execute(
                    select(func.max(
                        HydraulicSample.datetime_value)).where(
                        HydraulicSample.boreholesection_oid
                        == section_db._oid)).scalar()
                print(max_db)
                print(end_new)
                section_new['endtime'] = max(end_new, max_db)


def create_section(section: dict,
                   borehole: Union[str, Borehole],
                   db: Session,
                   commit: bool = True):

    if isinstance(borehole, str):
        borehole = read_borehole(borehole, db)
    if not borehole:
        raise KeyError(f'Borehole with publicID {borehole} does not exist.')

    section_db = read_section(section['publicid'], db)
    update_section_epoch(section_db,
                         section, db)

    hydraulics = section.pop('hydraulics', None)

    if section_db:
        for key, value in section.items():
            setattr(section_db, key, value)
    else:
        section_db = BoreholeSection(**section, _borehole=borehole)
        db.add(section_db)

    if hydraulics:
        create_hydraulics(hydraulics, section_db, db, False)

    if commit:
        db.commit()
    return section_db


def read_hydraulics(
        section_id: str,
        db: Session,
        starttime: datetime = None,
        endtime: datetime = None) -> List[HydraulicSample]:

    statement = select(HydraulicSample) \
        .where(HydraulicSample.boreholesection_oid == BoreholeSection._oid)\
        .where(BoreholeSection.publicid == section_id)\

    if starttime:
        statement = statement.where(
            HydraulicSample.datetime_value >= starttime)
    if endtime:
        statement = statement.where(
            HydraulicSample.datetime_value <= endtime)

    return db.execute(statement).unique().scalars().all()


def create_hydraulics(
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
    import time
    now = time.perf_counter()
    statement = delete(HydraulicSample) \
        .where(HydraulicSample.boreholesection_oid == BoreholeSection._oid) \
        .where(BoreholeSection.publicid == section.publicid) \
        .where(HydraulicSample.datetime_value > start) \
        .where(HydraulicSample.datetime_value < end) \
        .execution_options(synchronize_session=False)

    db.execute(statement)

    after = time.perf_counter()
    print(after - now)

    samples = [HydraulicSample(**s, _section=section) for s in hydraulics]
    db.add_all(samples)

    if commit:
        db.commit()

    return samples
