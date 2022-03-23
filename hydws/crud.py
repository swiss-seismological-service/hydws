from datetime import datetime
from operator import attrgetter
from sqlalchemy.orm import Session, joinedload, contains_eager
from sqlalchemy import select, update, delete  # noqa
from typing import List

from hydws.datamodel.orm import Borehole, BoreholeSection, HydraulicSample


def read_boreholes(db: Session) -> List[Borehole]:
    statement = select(Borehole).options(joinedload(Borehole._sections))
    result = db.execute(statement).unique().all()
    return [r[0] for r in result]


def read_borehole(
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
    statement = statement.where(
        Borehole.publicid == borehole_id)

    if starttime:
        statement = statement.where(time_query_start > starttime)
    if endtime:
        statement = statement.where(time_query_end < endtime)

    result = db.execute(statement).unique().scalar_one_or_none()
    return result


def create_borehole(borehole: dict, db: Session):
    borehole_db = read_borehole(borehole['publicid'], db, level='borehole')

    sections = borehole.pop('sections', None)

    if borehole_db:
        # statement = update(Borehole).where(
        #     Borehole.publicid == borehole['publicid']).values(
        #     **borehole)
        # db.execute(statement)
        for key, value in borehole.items():
            setattr(borehole_db, key, value)
    else:
        borehole_db = Borehole(**borehole)
        db.add(borehole_db)

    if sections:
        for section in sections:
            s = create_section(section, db, commit=False)
            borehole_db._sections.append(s)

    db.commit()
    db.refresh(borehole_db)
    return borehole_db


def read_section(section_id: str, db: Session):
    statement = select(BoreholeSection)
    statement = statement.where(
        BoreholeSection.publicid == section_id)
    result = db.execute(statement).unique().scalar_one_or_none()
    return result


def create_section(section: dict, db: Session, commit: bool = True):
    section_db = read_section(section['publicid'], db)

    hydraulics = section.pop('hydraulics', None)

    if section_db:
        for key, value in section.items():
            setattr(section_db, key, value)
    else:
        section_db = BoreholeSection(**section)
        db.add(section_db)

    if hydraulics:
        merge_hydraulics(hydraulics, section_db, db)

    if commit:
        db.commit()
        db.refresh(section_db)
    return section_db


def merge_hydraulics(
        hydraulics: List[dict],
        section: BoreholeSection,
        db: Session,
        commit: bool = True):

    datetimes = [h['datetime_value'] for h in hydraulics]
    start = min(datetimes)
    end = max(datetimes)
    import time

    now = time.perf_counter()
    statement = delete(HydraulicSample) \
        .where(HydraulicSample.boreholesection_oid == BoreholeSection._oid) \
        .where(BoreholeSection.publicid == section.publicid) \
        .where(HydraulicSample.datetime_value > start)\
        .where(HydraulicSample.datetime_value < end) \
        .execution_options(synchronize_session='fetch')

    d = db.execute(statement)
    then = time.perf_counter()
    print(d.rowcount)
    print(then - now)

    # for sample in hydraulics:
    #     sample['_section'] = section
    # db.bulk_insert_mappings(HydraulicSample, hydraulics)

    samples = [HydraulicSample(**s) for s in hydraulics]
    for s in samples:
        s._section = section

    db.add_all(samples)

    if commit:
        db.commit()

    return samples
