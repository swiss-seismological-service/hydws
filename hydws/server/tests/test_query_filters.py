# Copyright (C) 2019, ETH Zurich - Swiss Seismological Service SED
"""
Well related test facilities.
"""

import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm.exc import NoResultFound
from hydws.server import query_filters as qf


class MockQuery(object):
    """Mock session.query"""

    def __init__(self, query_text):
        self.val = query_text

    def filter(self, filt):
        self.val += str(filt)
        return self

    def paginate(self, page, limit, error_flag):
        pass

class MockColumn(object):
    """Mock sqlalchemy.Column"""
    def __init__(self):
        self.mock_attr = 'mock_attr'

    def mock_method(self, val):
        return val

class MockClass(object):
    """Mock orm class containing 'column'"""

    mock_column = MockColumn()

    def mock_method(self):
        pass

class MockClassUnderscore(object):
    """Mock orm class containing method with single underscore."""

    def mock_method_(self):
        pass

class MockClassDoubleUnderscore(object):
    """Mock orm class containing method with double underscores."""

    def __mock_method__(self):
        pass

class MockParams(object):
    """Mock query parameters to filter query on."""

    def get(self, param_name):
        return param_name


@patch.object(qf, 'Borehole', new=MockClass)
class DynamicQueryTestCase(unittest.TestCase):

    def test_operator_attr_exception(self):
        """Exception raised when no method exists in class."""
        dyn_f = qf.DynamicQuery(MagicMock())
        op = 'invalid_method'
        with self.assertRaises(Exception):
            dyn_f.operator_attr(MockClass(), op)

    def test_operator_attr_return(self):
        """Assert that <method> in class used."""
        dyn_f = qf.DynamicQuery(MagicMock())
        op = 'mock_method'
        self.assertEqual(dyn_f.operator_attr(MockClass(), op), op)

    def test_operator_attr_underscore(self):
        """Assert that <method>_ with underscores used."""
        dyn_f = qf.DynamicQuery(MagicMock())
        op = 'mock_method'
        existing_op = 'mock_method_'
        self.assertEqual(dyn_f.operator_attr(MockClassUnderscore(), op),
                         existing_op)

    def test_operator_attr_double_underscore(self):
        """Assert that __<method>__ with underscores used."""
        dyn_f = qf.DynamicQuery(MagicMock())
        op = 'mock_method'
        existing_op = '__mock_method__'
        self.assertEqual(dyn_f.operator_attr(MockClassDoubleUnderscore(), op),
                         existing_op)

    @patch.object(qf.DynamicQuery, 'operator_attr')
    def test_filter_query_return(self, mock_operator_attr):
        """Return mock query with one filter applied."""
        query_str = 'query'
        filter_str = '_mock_filter_value'
        expected_final_query = query_str + filter_str
        mock_operator_attr.return_value = "mock_method"

        # Set values (column obj, method on column obj, value used in filter)
        qf.FILTER_BOREHOLES = [('mock_column', 'mock_method', filter_str)]

        dyn_f = qf.DynamicQuery(MockQuery(query_str))
        dyn_f.filter_level(MockParams(), 'borehole')

        self.assertEqual(dyn_f.query.val, expected_final_query)

    @patch.object(qf.DynamicQuery, 'operator_attr')
    def test_filter_multi_query_return(self, mock_operator_attr):
        """Return mock query with >1 filter applied."""
        query_str = 'query'
        filter_str = '_mock_filter_value'
        filter_str2 = 'second_value'
        expected_final_query = query_str + filter_str + filter_str2

        qf.FILTER_BOREHOLES = [('mock_column', 'mock_method', filter_str),
                               ('mock_column', 'mock_method', filter_str2)]

        mock_operator_attr.return_value = "mock_method"
        dyn_f = qf.DynamicQuery(MockQuery(query_str))
        dyn_f.filter_level(MockParams(), 'borehole')

        self.assertEqual(dyn_f.query.val, expected_final_query)

    def test_filter_query_invalid_method(self):
        """Raise Exception in case of non-existent method on column obj.
        """
        dyn_f = qf.DynamicQuery(MockQuery('query'))
        qf.FILTER_BOREHOLES = [('mock_column', 'invalid_method',
                                '_mock_filter_value')]

        with self.assertRaises(Exception):
            dyn_f.filter_level(MockParams(), 'borehole')

    def test_filter_query_invalid_level(self):
        """Raise Exception in case of level not handled.
        """
        dyn_f = qf.DynamicQuery(MockQuery('query'))
        qf.FILTER_BOREHOLES = [('mock_column', 'invalid_method',
                                '_mock_filter_value')]

        with self.assertRaises(Exception):
            dyn_f.filter_level(MockParams(), 'unhandled_level')

    def test_format_results_query(self):
        """Check format_results called with correct params."""
        mock_query = MagicMock()
        dyn_f = qf.DynamicQuery(mock_query)
        limit=10
        dyn_f.format_results(limit=limit)

        mock_query.limit.assert_called_with(limit)
        self.assertFalse(mock_query.offset.called)
        self.assertFalse(mock_query.order_by.called)

    def test_return_all(self):
        """Check return_all() called with correct params."""
        mock_query = MagicMock()
        dyn_f = qf.DynamicQuery(mock_query)
        return_val = dyn_f.return_all()
        self.assertEqual(return_val, mock_query.all())

    def test_return_none(self):
        """Check None returned."""
        mock_query = MagicMock()
        dyn_f = qf.DynamicQuery(mock_query)
        mock_query.all.side_effect = NoResultFound
        return_val = dyn_f.return_all()
        self.assertEqual(return_val, None)
