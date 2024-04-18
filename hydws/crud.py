from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import delete, func, insert, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import defer, joinedload

from hydws.database import pandas_read_sql
from hydws.datamodel.orm import Borehole, BoreholeSection, HydraulicSample
from hydws.utils import (flattened_hydraulics_to_df, merge_hydraulics,
                         update_section_epoch)


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

    statement = select(Borehole).where(Borehole.publicid == borehole_id)

    if sections:
        statement = statement.join(BoreholeSection) \
            .options(joinedload(Borehole.sections))
        if starttime:
            statement = statement.where(BoreholeSection.endtime > starttime)
        if endtime:
            statement = statement.where(BoreholeSection.starttime < endtime)

    result = await db.execute(statement)

    return result.scalar()


async def delete_borehole(publicid: str, db: AsyncSession):
    stmt = delete(Borehole).where(Borehole.publicid == publicid)
    deleted = await db.execute(stmt)
    await db.commit()
    return deleted.rowcount


async def create_borehole(borehole: dict,
                          db: AsyncSession,
                          merge: bool = False,
                          merge_limit: int = 60):
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
            await create_section(section,
                                 borehole_db._oid,
                                 db,
                                 merge,
                                 merge_limit)
    else:
        await db.commit()

    return borehole_db


async def read_section(section_id: str, db: AsyncSession):

    statement = select(BoreholeSection)
    statement = statement.where(
        BoreholeSection.publicid == section_id)
    result = await db.execute(statement)

    return result.scalar_one_or_none()


async def read_section_oid(section_id: int, db: AsyncSession):

    statement = select(BoreholeSection._oid)
    statement = statement.where(
        BoreholeSection.publicid == section_id)
    result = await db.execute(statement)

    return result.scalar_one_or_none()


async def create_section(section: dict,
                         borehole_oid: int,
                         db: AsyncSession,
                         merge: bool = False,
                         merge_limit: int = 60):

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
        await create_hydraulics(hydraulics,
                                section_db._oid,
                                db,
                                merge,
                                merge_limit)
    else:
        await db.commit()

    return section_db


async def read_hydraulics_df(section_oid: str,
                             starttime: datetime = None,
                             endtime: datetime = None,
                             defer_cols: list = None) -> List[HydraulicSample]:

    statement = select(HydraulicSample) \
        .where(HydraulicSample._boreholesection_oid == section_oid)

    if defer_cols:
        statement = statement.options(*[defer(col) for col in defer_cols])

    if starttime:
        statement = statement.where(
            HydraulicSample.datetime_value >= starttime)
    if endtime:
        statement = statement.where(
            HydraulicSample.datetime_value <= endtime)

    return await pandas_read_sql(statement)


async def create_hydraulics(hydraulics: List[dict],
                            section_oid: int,
                            db: AsyncSession,
                            merge: bool = False,
                            merge_limit: int = 60):
    """
    Create hydraulic samples in the database.

    :param hydraulics: The hydraulic samples.
    :param section_oid: The section oid.
    :param db: The database session.
    :param merge: Merge the new data with the existing data.
    :param merge_limit: The merge limit.
    """
    # get daterange of new hydraulics
    datetimes = [h['datetime_value'] for h in hydraulics]
    start = min(datetimes)
    end = max(datetimes)

    # make sure there are partitions for the required daterange
    statement = \
        "call generate_partitioned_tables (DATE '{0}', DATE '{1}');".format(
            datetime.strftime(start, '%Y-%m-%d'),
            datetime.strftime(end + timedelta(days=1), '%Y-%m-%d'))
    await db.execute(text(statement))

    # check whether there are already samples in the database for that time
    count = await db.scalar(
        select(func.count(HydraulicSample._oid))
        .where(HydraulicSample._boreholesection_oid == section_oid)
        .where(HydraulicSample.datetime_value >= start)
        .where(HydraulicSample.datetime_value <= end))

    # merge the new data with the existing data
    if merge and count > 0:
        hydraulics_old = await read_hydraulics_df(section_oid,
                                                  start,
                                                  end)

        # transform the samples to consistent dataframes
        hydraulics_old = flattened_hydraulics_to_df(hydraulics_old)
        hydraulics = flattened_hydraulics_to_df(hydraulics)

        # merge the dataframes
        hydraulics = merge_hydraulics(hydraulics_old, hydraulics, merge_limit)

        # transform the dataframe back to a list of dictionaries for insertion
        hydraulics = hydraulics.reset_index().to_dict(orient='records')

    # remove none and nan values
    hydraulics = \
        [{k: v for k, v in v1.items() if v == v and v is not None}
            for v1 in hydraulics]

    # delete the old samples
    if count > 0:
        await db.execute(
            delete(HydraulicSample)
            .where(HydraulicSample._boreholesection_oid == section_oid)
            .where(HydraulicSample.datetime_value >= start)
            .where(HydraulicSample.datetime_value <= end)
            .execution_options(synchronize_session=False))

    # insert the new samples
    await db.execute(
        insert(HydraulicSample)
        .values(_boreholesection_oid=section_oid), hydraulics)

    await db.commit()
