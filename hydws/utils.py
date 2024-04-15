import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from hydws.datamodel.orm import BoreholeSection, HydraulicSample


def hydraulics_to_json(df: pd.DataFrame, drop_cols: list[str] = None) -> str:

    # do some data cleaning
    df = df.drop(drop_cols, axis=1) if drop_cols else df
    df = df.dropna(axis=1, how='all')

    numeric_columns = df.select_dtypes(include='number').columns
    df[numeric_columns] = df[numeric_columns].fillna(0)

    if 'datetime_value' in df.columns:
        df = df.sort_values(by='datetime_value')
        df['datetime_value'] = pd.to_datetime(
            df['datetime_value']).dt.strftime('%Y-%m-%dT%H:%M:%S')

    # convert to nested dict by splitting column names which have a "_"
    mylist = []
    for row in df.itertuples(index=False):
        result = {}
        for key, value in row._asdict().items():
            if '_' not in key:
                result[key] = value
                continue
            parts = key.split('_')
            current = result
            for part in parts[:-1]:
                current = current.setdefault(part, {})
            current[parts[-1]] = value

        mylist.append(result)

    return mylist


async def update_section_epoch(
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
                min_db = await db.execute(
                    select(func.min(
                        HydraulicSample.datetime_value)).where(
                        HydraulicSample._boreholesection_oid
                        == section_db._oid))
                min_db = min_db.scalar()
                section_new['starttime'] = min(start_new, min_db or start_new)
        if end_new:
            if end_new > section_db.endtime:
                section_new['endtime'] = end_new
            else:
                max_db = await db.execute(
                    select(func.max(
                        HydraulicSample.datetime_value)).where(
                        HydraulicSample._boreholesection_oid
                        == section_db._oid))
                max_db = max_db.scalar()
                section_new['endtime'] = max(end_new, max_db or end_new)
    return section_new
