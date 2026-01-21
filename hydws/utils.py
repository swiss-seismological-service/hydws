from typing import Annotated

import numpy as np
import pandas as pd
from fastapi import Header, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from config.config import get_settings
from hydws.datamodel.orm import BoreholeSection, HydraulicSample


def hydraulics_to_json(
        df: pd.DataFrame,
        drop_cols: list[str] = None) -> list[dict]:
    """
    Convert a hydraulic dataframe to a list of dictionaries,
    including nested RealValues.

    :param df: The hydraulic dataframe.
    :param drop_cols: The columns to drop.
    :return: The list of dictionaries.
    """
    # do some data cleaning
    df = df.drop(drop_cols, axis=1) if drop_cols else df
    df = df.dropna(axis=1, how='all')

    if df.empty:
        return []

    if 'datetime_value' not in df.columns:
        df = df.reset_index()

    try:
        df = df.sort_values(by='datetime_value')
        df['datetime_value'] = pd.to_datetime(
            df['datetime_value']).dt.strftime('%Y-%m-%dT%H:%M:%S')
    except BaseException:
        raise ValueError('datetime_value column not found hydraulic samples.')

    # convert to nested dict by splitting column names which have a "_"
    mylist = []
    for row in df.itertuples(index=False):
        result = {}
        for key, value in row._asdict().items():
            if value != value:
                continue
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
    """
    Update the starttime and endtime of a section based on the new data.

    :param section_db: The existing section.
    :param section_new: The new section data.
    :param db: The database session.
    """
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


def flattened_hydraulics_to_df(data: dict | pd.DataFrame) -> pd.DataFrame:
    """
    Set index, drop columns, and sort the hydraulic dataframe.

    :param data: The hydraulic data.
    :return: The formatted dataframe.
    """

    if isinstance(data, list):
        data = pd.DataFrame.from_records(data)

    data.set_index('datetime_value', inplace=True, drop=True)
    data.drop(columns=['_oid', '_boreholesection_oid'],
              inplace=True,
              errors='ignore')
    data = data.mask(
        data.eq('None')).dropna(how='all', axis=1)
    data = data.sort_index()
    return data


def overwrite_hydraulic_columns(existing: pd.DataFrame, new: pd.DataFrame):
    """
    Remove columns from the existing dataframe that are present in the new one.

    :param existing: The existing hydraulic dataframe.
    :param new: The new hydraulic dataframe.
    :return: The existing dataframe with the columns removed.
    """
    existing_columns = set(col.split('_')[0] for col in existing.columns)
    new_columns = set(col.split('_')[0] for col in new.columns)

    to_delete = list(existing_columns.intersection(new_columns))
    if to_delete:
        return existing.drop(
            existing.filter(regex='|'.join(to_delete)).columns, axis=1)
    else:
        return existing


def merge_hydraulics(existing, new, limit=60):
    """
    Merge two hydraulic dataframes, filling gaps up to a certain limit.

    :param existing: The existing hydraulic dataframe.
    :param new: The new hydraulic dataframe.
    :param limit: The maximum gap to fill in seconds.
    :return: The merged dataframe.
    """
    existing = overwrite_hydraulic_columns(existing, new)

    if existing.empty:
        return new

    df = existing.merge(
        new,
        how='outer',
        left_index=True,
        right_index=True)

    # depending on the replaced columns, some rows may be all NaN
    df.dropna(how='all', axis=0, inplace=True)

    # +0.1 to avoid rounding errors
    jd_max_gap_fill = (limit + 0.1) / (3600 * 24)

    # forward fill gaps up to jd_max_gap_fill
    df['jd'] = df.index.to_julian_date()
    for col in df.columns:
        df['ffill'] = df[col].ffill()
        df['jd_nan'] = np.where(~df[col].isna(),
                                df['jd'],
                                np.nan)
        df['jd_gap'] = df['jd_nan'].bfill() - df['jd_nan'].ffill()
        df[col] = np.where(df['jd_gap'] <= jd_max_gap_fill,
                           df['ffill'],
                           np.nan)
    df = df.drop(columns=['ffill', 'jd', 'jd_nan', 'jd_gap'])

    return df


def verify_api_key(x_api_key: Annotated[str | None, Header()] = None):
    """
    Verify the API key from the X-API-Key header.
    If API_KEY is not set in config, protection is disabled.
    """
    settings = get_settings()
    if not settings.API_KEY:
        return  # Protection disabled
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=401, detail="Invalid or missing API key")
