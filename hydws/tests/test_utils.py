import orjson
import pandas as pd
from numpy.testing import assert_equal

from hydws.utils import real_values_to_json


def test_real_values_to_json():
    # Create a sample DataFrame with real value columns
    data = {
        'Depth': [1, 2, 3],
        'Pressure_value': [10.1, 20.2, 30.3],
        'Pressure_uncertainty': [0.1, 0.2, 0.3],
        'Temperature_value': [100.01, 200.02, 300.03],
        'Temperature_uncertainty': [1.0, 2.0, 3.0]
    }
    df = pd.DataFrame(data)

    # Test with default arguments
    expected_result = [
        {
            'Depth': 1,
            'Pressure': {
                'value': 10.1, 'uncertainty': 0.1},
            'Temperature': {
                'value': 100.01, 'uncertainty': 1.0}},
        {
            'Depth': 2,
            'Pressure': {
                'value': 20.2, 'uncertainty': 0.2},
            'Temperature': {
                'value': 200.02, 'uncertainty': 2.0}},
        {
            'Depth': 3,
            'Pressure': {
                'value': 30.3, 'uncertainty': 0.3},
            'Temperature': {
                'value': 300.03, 'uncertainty': 3.0}}]
    assert_equal(orjson.loads(real_values_to_json(df)), expected_result)

    # Test with drop_cols argument
    expected_result = [
        {'Depth': 1, 'Temperature': {'value': 100.01, 'uncertainty': 1.0}},
        {'Depth': 2, 'Temperature': {'value': 200.02, 'uncertainty': 2.0}},
        {'Depth': 3, 'Temperature': {'value': 300.03, 'uncertainty': 3.0}}
    ]
    assert orjson.loads(
        real_values_to_json(
            df,
            drop_cols=[
                'Pressure_value',
                'Pressure_uncertainty'])) == expected_result

    # Test with empty DataFrame
    empty_df = pd.DataFrame()
    assert orjson.loads(real_values_to_json(empty_df)) == []

    # Test with DataFrame containing only non-real columns
    data = {
        'Col1': [1, 2, 3],
        'Col2': [4, 5, 6]
    }
    df = pd.DataFrame(data)
    assert orjson.loads(real_values_to_json(df)) == []
