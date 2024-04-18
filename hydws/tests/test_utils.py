import io

import pandas as pd
from numpy.testing import assert_equal

from hydws.utils import hydraulics_to_json, merge_hydraulics


def test_real_values_to_json():
    # Create a sample DataFrame with real value columns
    data = {
        'datetime_value': ['2021-01-01T00:00:00',
                           '2021-01-01T00:01:00',
                           '2021-01-01T00:02:00'],
        'depth': [1, 2, 3],
        'toppressure_value': [10.1, 20.2, 30.3],
        'toppressure_uncertainty': [0.1, 0.2, 0.3],
        'topflow_value': [100.01, 200.02, 300.03],
        'topflow_uncertainty': [1.0, 2.0, 3.0],
        'toptemperature_value': [100.01, 200.02, 300.03],
        'toptemperature_uncertainty': [1.0, 2.0, 3.0]
    }
    df = pd.DataFrame(data)

    # Test with default arguments
    expected_result = [
        {
            'datetime': {'value': '2021-01-01T00:00:00'},
            'depth': 1,
            'toppressure': {
                'value': 10.1, 'uncertainty': 0.1},
            'topflow': {
                'value': 100.01, 'uncertainty': 1.0},
            'toptemperature': {
                'value': 100.01, 'uncertainty': 1.0},
        },
        {
            'datetime': {'value': '2021-01-01T00:01:00'},
            'depth': 2,
            'toppressure': {
                'value': 20.2, 'uncertainty': 0.2},
            'topflow': {
                'value': 200.02, 'uncertainty': 2.0},
            'toptemperature': {
                'value': 200.02, 'uncertainty': 2.0},
        },
        {
            'datetime': {'value': '2021-01-01T00:02:00'},
            'depth': 3,
            'toppressure': {
                'value': 30.3, 'uncertainty': 0.3},
            'topflow': {
                'value': 300.03, 'uncertainty': 3.0},
            'toptemperature': {
                'value': 300.03, 'uncertainty': 3.0},
        }]

    assert_equal(hydraulics_to_json(df), expected_result)

    # Test with drop_cols argument
    expected_result = [
        {
            'depth': 1,
            'datetime': {'value': '2021-01-01T00:00:00'},
            'topflow': {
                'value': 100.01, 'uncertainty': 1.0},
            'toppressure': {
                'value': 10.1, 'uncertainty': 0.1}}, {
            'depth': 2,
            'datetime': {'value': '2021-01-01T00:01:00'},
            'topflow': {
                'value': 200.02, 'uncertainty': 2.0},
            'toppressure': {
                'value': 20.2, 'uncertainty': 0.2}}, {
            'depth': 3,
            'datetime': {'value': '2021-01-01T00:02:00'},
            'topflow': {
                'value': 300.03, 'uncertainty': 3.0},
            'toppressure': {
                'value': 30.3, 'uncertainty': 0.3}}]

    assert hydraulics_to_json(
        df,
        drop_cols=[
            'toptemperature_value',
            'toptemperature_uncertainty']) == expected_result

    # Test with empty DataFrame
    empty_df = pd.DataFrame()
    assert hydraulics_to_json(empty_df) == []


def test_merge_hydraulics_simple():
    merged = merge_hydraulics(df1, df2)
    pd.testing.assert_frame_equal(merged, result1)


def test_merge_hydraulics_gap():
    merged = merge_hydraulics(df1, df3)
    pd.testing.assert_frame_equal(merged, result2)


def test_merge_hydraulics_overlapping():
    merged = merge_hydraulics(df1, df4)
    pd.testing.assert_frame_equal(merged, result3)


def test_merge_hydraulics_large():
    merged_1 = merge_hydraulics(df1, df5, limit=300)
    merged_2 = merge_hydraulics(df1, df5, limit=299)

    pd.testing.assert_frame_equal(merged_1, result4)
    pd.testing.assert_frame_equal(merged_2, result5)


def test_merge_hydraulics_realvalues():
    merged = merge_hydraulics(df6, df7)
    pd.testing.assert_frame_equal(merged, result6)


CSV_DATA_1 = """datetime_value,toppressure_value
2021-01-01T00:00:00,1.0
2021-01-01T00:01:00,2.0
2021-01-01T00:02:00,3.0
2021-01-01T00:03:00,4.0
2021-01-01T00:04:00,5.0
2021-01-01T00:05:00,6.0
2021-01-01T00:06:00,7.0
2021-01-01T00:07:00,8.0
2021-01-01T00:08:00,9.0
2021-01-01T00:09:00,10.0
"""

CSV_DATA_2 = """datetime_value,topflow_value
2021-01-01T00:00:00,11.0
2021-01-01T00:00:30,12.0
2021-01-01T00:01:00,13.0
2021-01-01T00:01:30,14.0
2021-01-01T00:02:00,15.0
2021-01-01T00:02:30,16.0
2021-01-01T00:03:00,17.0
2021-01-01T00:03:30,18.0
2021-01-01T00:04:00,19.0
2021-01-01T00:04:30,20.0
2021-01-01T00:05:00,21.0
"""

CSV_DATA_3 = """datetime_value,topflow_value
2021-01-01T00:00:00,11.0
2021-01-01T00:00:30,12.0
2021-01-01T00:01:00,13.0
2021-01-01T00:01:30,14.0
2021-01-01T00:03:30,18.0
2021-01-01T00:04:30,20.0
2021-01-01T00:05:00,21.0
"""

CSV_DATA_4 = """datetime_value,topflow_value
2021-01-01T00:03:00,4.0
2021-01-01T00:04:00,5.0
2021-01-01T00:05:00,6.0
2021-01-01T00:06:00,7.0
2021-01-01T00:07:00,8.0
2021-01-01T00:08:00,9.0
2021-01-01T00:09:00,10.0
2021-01-01T00:10:00,1.0
2021-01-01T00:11:00,2.0
2021-01-01T00:12:00,3.0
2021-01-01T00:13:00,4.0
"""

CSV_DATA_5 = """datetime_value,topflow_value
2021-01-01T00:00:00,11.0
2021-01-01T00:05:00,12.0
2021-01-01T00:10:00,13.0
2021-01-01T00:15:00,14.0
2021-01-01T00:20:00,15.0
2021-01-01T00:25:00,16.0
2021-01-01T00:30:00,17.0
"""

CSV_DATA_6 = """
datetime_value,toppressure_value,toppressure_uncertainty,topflow_value
2021-01-01T00:00:00,1.0,0.1,11.0
2021-01-01T00:00:30,1.0,0.1,12.0
2021-01-01T00:01:00,2.0,0.2,13.0
2021-01-01T00:01:30,2.0,0.2,14.0
2021-01-01T00:02:00,3.0,0.3,15.0
2021-01-01T00:02:30,3.0,0.3,16.0
2021-01-01T00:03:00,4.0,0.4,17.0
2021-01-01T00:03:30,4.0,0.4,18.0
2021-01-01T00:04:00,5.0,0.5,19.0
2021-01-01T00:04:30,5.0,0.5,20.0
2021-01-01T00:05:00,6.0,0.6,21.0
"""

CSV_DATA_7 = """
datetime_value,toppressure_value,topflow_value,topflow_uncertainty
2021-01-01T00:00:00,1.0,11.0,1.0
2021-01-01T00:00:30,1.0,12.0,2.0
2021-01-01T00:01:00,2.0,13.0,3.0
2021-01-01T00:01:30,2.0,14.0,4.0
2021-01-01T00:05:00,3.0,15.0,5.0
2021-01-01T00:05:30,3.0,16.0,6.0
2021-01-01T00:06:00,4.0,17.0,7.0
2021-01-01T00:06:30,4.0,18.0,8.0
2021-01-01T00:07:00,5.0,19.0,9.0
2021-01-01T00:07:30,5.0,20.0,10.0
2021-01-01T00:08:00,6.0,21.0,11.0
"""

RESULT_1 = """datetime_value,toppressure_value,topflow_value
2021-01-01T00:00:00,1.0,11.0
2021-01-01T00:00:30,1.0,12.0
2021-01-01T00:01:00,2.0,13.0
2021-01-01T00:01:30,2.0,14.0
2021-01-01T00:02:00,3.0,15.0
2021-01-01T00:02:30,3.0,16.0
2021-01-01T00:03:00,4.0,17.0
2021-01-01T00:03:30,4.0,18.0
2021-01-01T00:04:00,5.0,19.0
2021-01-01T00:04:30,5.0,20.0
2021-01-01T00:05:00,6.0,21.0
2021-01-01T00:06:00,7.0,NaN
2021-01-01T00:07:00,8.0,NaN
2021-01-01T00:08:00,9.0,NaN
2021-01-01T00:09:00,10.0,NaN
"""

RESULT_2 = """datetime_value,toppressure_value,topflow_value
2021-01-01T00:00:00,1.0,11.0
2021-01-01T00:00:30,1.0,12.0
2021-01-01T00:01:00,2.0,13.0
2021-01-01T00:01:30,2.0,14.0
2021-01-01T00:02:00,3.0,NaN
2021-01-01T00:03:00,4.0,NaN
2021-01-01T00:03:30,4.0,18.0
2021-01-01T00:04:00,5.0,18.0
2021-01-01T00:04:30,5.0,20.0
2021-01-01T00:05:00,6.0,21.0
2021-01-01T00:06:00,7.0,NaN
2021-01-01T00:07:00,8.0,NaN
2021-01-01T00:08:00,9.0,NaN
2021-01-01T00:09:00,10.0,NaN
"""

RESULT_3 = """datetime_value,toppressure_value,topflow_value
2021-01-01 00:00:00,1.0,NaN
2021-01-01 00:01:00,2.0,NaN
2021-01-01 00:02:00,3.0,NaN
2021-01-01 00:03:00,4.0,4.0
2021-01-01 00:04:00,5.0,5.0
2021-01-01 00:05:00,6.0,6.0
2021-01-01 00:06:00,7.0,7.0
2021-01-01 00:07:00,8.0,8.0
2021-01-01 00:08:00,9.0,9.0
2021-01-01 00:09:00,10.0,10.0
2021-01-01 00:10:00,NaN,1.0
2021-01-01 00:11:00,NaN,2.0
2021-01-01 00:12:00,NaN,3.0
2021-01-01 00:13:00,NaN,4.0
"""

RESULT_4 = """datetime_value,toppressure_value,topflow_value
2021-01-01T00:00:00,1.0,11.0
2021-01-01T00:01:00,2.0,11.0
2021-01-01T00:02:00,3.0,11.0
2021-01-01T00:03:00,4.0,11.0
2021-01-01T00:04:00,5.0,11.0
2021-01-01T00:05:00,6.0,12.0
2021-01-01T00:06:00,7.0,12.0
2021-01-01T00:07:00,8.0,12.0
2021-01-01T00:08:00,9.0,12.0
2021-01-01T00:09:00,10.0,12.0
2021-01-01T00:10:00,NaN,13.0
2021-01-01T00:15:00,NaN,14.0
2021-01-01T00:20:00,NaN,15.0
2021-01-01T00:25:00,NaN,16.0
2021-01-01T00:30:00,NaN,17.0
"""

RESULT_5 = """datetime_value,toppressure_value,topflow_value
2021-01-01T00:00:00,1.0,11.0
2021-01-01T00:01:00,2.0,NaN
2021-01-01T00:02:00,3.0,NaN
2021-01-01T00:03:00,4.0,NaN
2021-01-01T00:04:00,5.0,NaN
2021-01-01T00:05:00,6.0,12.0
2021-01-01T00:06:00,7.0,NaN
2021-01-01T00:07:00,8.0,NaN
2021-01-01T00:08:00,9.0,NaN
2021-01-01T00:09:00,10.0,NaN
2021-01-01T00:10:00,NaN,13.0
2021-01-01T00:15:00,NaN,14.0
2021-01-01T00:20:00,NaN,15.0
2021-01-01T00:25:00,NaN,16.0
2021-01-01T00:30:00,NaN,17.0
"""

RESULT_6 = """
datetime_value,toppressure_value,topflow_value,topflow_uncertainty
2021-01-01T00:00:00,1.0,11.0,1.0
2021-01-01T00:00:30,1.0,12.0,2.0
2021-01-01T00:01:00,2.0,13.0,3.0
2021-01-01T00:01:30,2.0,14.0,4.0
2021-01-01T00:05:00,3.0,15.0,5.0
2021-01-01T00:05:30,3.0,16.0,6.0
2021-01-01T00:06:00,4.0,17.0,7.0
2021-01-01T00:06:30,4.0,18.0,8.0
2021-01-01T00:07:00,5.0,19.0,9.0
2021-01-01T00:07:30,5.0,20.0,10.0
2021-01-01T00:08:00,6.0,21.0,11.0
"""

df1 = pd.read_csv(io.StringIO(CSV_DATA_1),
                  index_col='datetime_value', parse_dates=True)
df2 = pd.read_csv(io.StringIO(CSV_DATA_2),
                  index_col='datetime_value', parse_dates=True)
df3 = pd.read_csv(io.StringIO(CSV_DATA_3),
                  index_col='datetime_value', parse_dates=True)
df4 = pd.read_csv(io.StringIO(CSV_DATA_4),
                  index_col='datetime_value', parse_dates=True)
df5 = pd.read_csv(io.StringIO(CSV_DATA_5),
                  index_col='datetime_value', parse_dates=True)
df6 = pd.read_csv(io.StringIO(CSV_DATA_6),
                  index_col='datetime_value', parse_dates=True)
df7 = pd.read_csv(io.StringIO(CSV_DATA_7),
                  index_col='datetime_value', parse_dates=True)

result1 = pd.read_csv(io.StringIO(RESULT_1),
                      index_col='datetime_value', parse_dates=True)
result2 = pd.read_csv(io.StringIO(RESULT_2),
                      index_col='datetime_value', parse_dates=True)
result3 = pd.read_csv(io.StringIO(RESULT_3),
                      index_col='datetime_value', parse_dates=True)
result4 = pd.read_csv(io.StringIO(RESULT_4),
                      index_col='datetime_value', parse_dates=True)
result5 = pd.read_csv(io.StringIO(RESULT_5),
                      index_col='datetime_value', parse_dates=True)
result6 = pd.read_csv(io.StringIO(RESULT_6),
                      index_col='datetime_value', parse_dates=True)
