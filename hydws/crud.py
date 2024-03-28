from datetime import datetime
from typing import List, Optional

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import defer, joinedload

from hydws.database import pandas_read_sql
from hydws.datamodel.orm import Borehole, BoreholeSection, HydraulicSample
from hydws.utils import update_section_epoch


async def read_boreholes(db: AsyncSession,
                         starttime: Optional[datetime] = None,
                         endtime: Optional[datetime] = None,
                         minlatitude: Optional[float] = None,
                         maxlatitude: Optional[float] = None,
                         minlongitude: Optional[float] = None,
                         maxlongitude: Optional[float] = None) \
        -> List[Borehole]:

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

    result = await db.execute(statement)

    return result.scalars().unique().all()


async def read_borehole(borehole_id: str,
                        db: AsyncSession,
                        sections: bool = False,
                        starttime: datetime = None,
                        endtime: datetime = None) -> Borehole:

    statement = select(Borehole).where(Borehole.publicid == str(borehole_id))

    if sections:
        statement = statement.join(BoreholeSection) \
            .options(joinedload(Borehole.sections))
        if starttime:
            statement = statement.where(BoreholeSection.endtime > starttime)
        if endtime:
            statement = statement.where(BoreholeSection.starttime < endtime)

    result = await db.execute(statement)

    return result.scalar()


def delete_borehole(publicid: str, db: AsyncSession):
    stmt = delete(Borehole).where(Borehole.publicid == publicid)
    deleted = db.execute(stmt)
    db.commit()
    return deleted.rowcount


async def create_borehole(borehole: dict, db: AsyncSession):
    sections = borehole.pop('sections', None)

    borehole_db = await read_borehole(borehole['publicid'], db)

    if borehole_db:
        for key, value in borehole.items():
            setattr(borehole_db, key, value)
    else:
        borehole_db = Borehole(**borehole)
        db.add(borehole_db)

    await db.flush()

    if sections:
        for section in sections:
            await create_section(section, borehole_db._oid, db)
    else:
        await db.commit()

    return borehole_db


async def read_sections(db: AsyncSession) -> List[BoreholeSection]:

    statement = select(Borehole)
    result = await db.execute(statement)

    return result.unique().scalars()


async def read_section(section_id: str, db: AsyncSession):

    statement = select(BoreholeSection)
    statement = statement.where(
        BoreholeSection.publicid == section_id)
    result = await db.execute(statement)

    return result.scalar_one_or_none()


async def create_section(section: dict,
                         borehole_oid: int,
                         db: AsyncSession):

    section_db = await read_section(section['publicid'], db)

    section = await update_section_epoch(section_db,
                                         section, db)

    hydraulics = section.pop('hydraulics', None)

    if section_db:
        for key, value in section.items():
            setattr(section_db, key, value)
    else:
        section_db = BoreholeSection(**section, _borehole_oid=borehole_oid)
        db.add(section_db)

    await db.flush()

    if hydraulics:
        await create_hydraulics(hydraulics, section_db._oid, db)
    else:
        await db.commit()

    return section_db


async def read_hydraulics_df(section_id: str,
                             starttime: datetime = None,
                             endtime: datetime = None,
                             defer_cols: list = None) -> List[HydraulicSample]:

    statement = select(HydraulicSample) \
        .outerjoin(BoreholeSection) \
        .where(BoreholeSection.publicid == section_id)

    if defer_cols:
        statement = statement.options(*[defer(col) for col in defer_cols])

    if starttime:
        statement = statement.where(
            HydraulicSample.datetime_value >= starttime)
    if endtime:
        statement = statement.where(
            HydraulicSample.datetime_value <= endtime)

    return await pandas_read_sql(statement)


async def create_hydraulics(
        hydraulics: List[dict],
        section_oid: int,
        db: AsyncSession):

    datetimes = [h['datetime_value'] for h in hydraulics]
    start = min(datetimes)
    end = max(datetimes)

    statement = delete(HydraulicSample) \
        .where(HydraulicSample._boreholesection_oid == section_oid) \
        .where(HydraulicSample.datetime_value > start) \
        .where(HydraulicSample.datetime_value < end) \
        .execution_options(synchronize_session=False)

    await db.execute(statement)

    await db.execute(insert(HydraulicSample)
                     .values(_boreholesection_oid=section_oid),
                     hydraulics)
    await db.commit()
