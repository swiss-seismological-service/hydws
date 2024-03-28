import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from hydws.datamodel.orm import BoreholeSection, HydraulicSample


def real_values_to_json(df: pd.DataFrame, drop_cols: list[str] = None) -> str:
    df = df.drop(drop_cols, axis=1) if drop_cols else df
    df = df.dropna(axis=1, how='all')

    realvalues = ['_value',
                  '_uncertainty',
                  '_loweruncertainty',
                  '_upperuncertainty',
                  '_confidencelevel']

    not_real_cols = [col for col in df.columns if not
                     any(rv in col for rv in realvalues)]

    df_not_real = df[not_real_cols] if not_real_cols else None

    df = df.drop(not_real_cols, axis=1) if not_real_cols else df

    df.columns = pd.MultiIndex.from_tuples(
        [tuple(col.split('_')) for col in df.columns],
        names=['Names', 'Values'])

    df = df.stack(level=1, future_stack=True)

    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(
            df['datetime']).dt.strftime('%Y-%m-%dT%H:%M:%S')

    if df_not_real is not None:
        result = df.groupby(level=0) \
            .apply(lambda x: x.droplevel(0).to_dict()
                   | df_not_real.loc[x.name].to_dict()) \
            .to_json(orient='records')
    else:
        result = df.groupby(level=0) \
            .apply(lambda x: x.droplevel(0).to_dict()) \
            .to_json(orient='records')
    return result


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
