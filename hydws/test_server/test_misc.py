# Copyright (C) 2019, ETH Zurich - Swiss Seismological Service SED
"""
Well related test facilities.
"""

import unittest
from unittest.mock import MagicMock, patch
from hydws.server import misc

class MockQuery(object):

    def __init__(self, query_text):
        self.val = query_text

    def filter(self, filt):
        self.val += str(filt)
        return self

class MockColumn(object):
    def __init__(self):
        self.mock_attr = 'mock_attr'

    def mock_method(self, val):
        return val

class MockClass(object):

    mock_column_value = MockColumn()

    def mock_method(self):
        pass

class MockClassUnderscore(object):

    def mock_method_(self):
        pass

class MockClassDoubleUnderscore(object):

    def __mock_method__(self):
        pass

class MockParams(object):

    def get(self, param_name):
        return param_name

class DynamicQueryTestCase(unittest.TestCase):

    def test_operator_attr_exception(self):
        dyn_f = misc.DynamicQuery(MagicMock(), MagicMock())
        op = 'invalid_method'
        with self.assertRaises(Exception):
            dyn_f.operator_attr(MockClass(), op)

    def test_operator_attr_return(self):
        dyn_f = misc.DynamicQuery(MagicMock(), MagicMock())
        op = 'mock_method'
        self.assertEqual(dyn_f.operator_attr(MockClass(), op), op)

    def test_operator_attr_underscore(self):
        dyn_f = misc.DynamicQuery(MagicMock(), MagicMock())
        op = 'mock_method'
        existing_op = 'mock_method_'
        self.assertEqual(dyn_f.operator_attr(MockClassUnderscore(), op),
                         existing_op)

    def test_operator_attr_double_underscore(self):
        dyn_f = misc.DynamicQuery(MagicMock(), MagicMock())
        op = 'mock_method'
        existing_op = '__mock_method__'
        self.assertEqual(dyn_f.operator_attr(MockClassDoubleUnderscore(), op),
                         existing_op)

    @patch.object(misc.DynamicQuery, 'operator_attr')
    def test_filter_query_return(self, mock_operator_attr):
        """Return mock query with filter applied."""
        query_str = 'query'
        filter_str = '_mock_filter_value'
        expected_final_query = query_str + filter_str
        mock_operator_attr.return_value = "mock_method"
        dyn_f = misc.DynamicQuery(MockQuery(query_str), MockClass())
        dyn_f.filter_query(MockParams(),
                [('mock_column', 'mock_method', filter_str)])
        self.assertEqual(dyn_f.query.val, expected_final_query)

    @patch.object(misc.DynamicQuery, 'operator_attr')
    def test_filter_multi_query_return(self, mock_operator_attr):
        """Return mock query with >1 filter applied."""
        query_str = 'query'
        filter_str = '_mock_filter_value'
        filter_str2 = 'second_value'
        expected_final_query = query_str + filter_str + filter_str2

        mock_operator_attr.return_value = "mock_method"
        dyn_f = misc.DynamicQuery(MockQuery(query_str), MockClass())
        dyn_f.filter_query(MockParams(),
                [('mock_column', 'mock_method', filter_str),
                 ('mock_column', 'mock_method', filter_str2)])
        self.assertEqual(dyn_f.query.val, expected_final_query)

    def test_filter_query_invalid_input(self):
        dyn_f = misc.DynamicQuery(MockQuery('query'), MockClass())
        with self.assertRaises(Exception):
            dyn_f.filter_query(MockParams(),
                [('mock_column', 'mock_method',
                  '_mock_filter_value', 'extra val')])

    def test_filter_query_invalid_method(self):
        dyn_f = misc.DynamicQuery(MockQuery('query'), MockClass())
        with self.assertRaises(Exception):
            dyn_f.filter_query(MockParams(),
                [('mock_column', 'invalid_method', '_mock_filter_value')])
