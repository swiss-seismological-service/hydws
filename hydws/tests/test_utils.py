import pandas as pd
from numpy.testing import assert_equal

from hydws.utils import hydraulics_to_json


def test_real_values_to_json():
    # Create a sample DataFrame with real value columns
    data = {
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
            'depth': 1,
            'toppressure': {
                'value': 10.1, 'uncertainty': 0.1},
            'topflow': {
                'value': 100.01, 'uncertainty': 1.0},
            'toptemperature': {
                'value': 100.01, 'uncertainty': 1.0},
        },
        {
            'depth': 2,
            'toppressure': {
                'value': 20.2, 'uncertainty': 0.2},
            'topflow': {
                'value': 200.02, 'uncertainty': 2.0},
            'toptemperature': {
                'value': 200.02, 'uncertainty': 2.0},
        },
        {
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
            'topflow': {
                'value': 100.01, 'uncertainty': 1.0},
            'toppressure': {
                'value': 10.1, 'uncertainty': 0.1}}, {
            'depth': 2,
            'topflow': {
                'value': 200.02, 'uncertainty': 2.0},
            'toppressure': {
                'value': 20.2, 'uncertainty': 0.2}}, {
            'depth': 3,
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
