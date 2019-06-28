"""Unit testing for hydws.server.v1.routes.py."""
import unittest
import base64
from datetime import datetime

from unittest.mock import MagicMock, patch, call

from hydws.server.v1 import routes
from hydws.server import db, create_app


bh1_publicid = 'smi:ch.ethz.sed/bh/11111111-e4a0-4692-bf29-33b5591eb799'
sec1_publicid = 'smi:ch.ethz.sed/bh/section/11111111-8d89-4f13-95e7-526ade73cc7c'

bh1_publicid_encoded = base64.b64encode(bytes(bh1_publicid, 'utf8')).decode('utf-8')
sec1_publicid_encoded = base64.b64encode(bytes(sec1_publicid, 'utf8')).decode('utf-8')


def clean_db(db):
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())


class RoutesGetTestCase(unittest.TestCase):
    """Test get methods in routes."""
    db = None

    @classmethod
    def setUpClass(cls):
        super(RoutesGetTestCase, cls).setUpClass()
        cls.app = create_app() # Add test config?
        cls.db = db
        cls.db.app = cls.app
        cls.db.create_all(app=cls.app)

    @classmethod
    def tearDownClass(cls):
        cls.db.drop_all(app=cls.app)
        super(RoutesGetTestCase, cls).tearDownClass()

    def setUp(self):
        super(RoutesGetTestCase, self).setUp()

        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        clean_db(self.db)

    def tearDown(self):
        self.db.session.rollback()
        self.app_context.pop()

        super(RoutesGetTestCase, self).tearDown()

    @patch.object(routes.BoreholeListResource, '_process_request')
    @patch.object(routes, 'BoreholeListResourceSchema')
    @patch.object(routes, 'BoreholeSchema')
    @patch.object(routes, 'make_response')
    def test_borehole_list_get_level_sec(
            self, mock_response, mock_oschema, mock_schema,
            mock_process_request):
        """Test level=section for BoreholeListResource."""

        routes.db = self.db
        with self.client as c:
            response = c.get('/hydws/v1/boreholes?maxlatitude=10&level=section')
            mock_process_request.assert_called_with(
                self.db.session, format='json', level='section',
                maxlatitude=10.0, nodata=204)
            self.assertTrue(mock_oschema.called)
            self.assertTrue(mock_response.called)

    @patch.object(routes.BoreholeListResource, '_process_request')
    @patch.object(routes, 'BoreholeListResourceSchema')
    @patch.object(routes, 'BoreholeSchema')
    @patch.object(routes, 'make_response')
    def test_borehole_list_get_level_bh(
            self, mock_response, mock_oschema, mock_schema,
            mock_process_request):
        """Test level=borehole for BoreholeListResource."""

        routes.db = self.db
        with self.client as c:
            response = c.get('/hydws/v1/boreholes?maxlatitude=10&level=borehole')
            mock_process_request.assert_called_with(
                self.db.session, format='json', level='borehole',
                maxlatitude=10.0, nodata=204)
            self.assertTrue(mock_oschema.called)
            self.assertTrue(mock_response.called)


    @patch.object(routes.BoreholeHydraulicSampleListResource,
        '_process_request')
    @patch.object(routes, 'BoreholeHydraulicSampleListResource')
    @patch.object(routes, 'BoreholeSchema')
    @patch.object(routes, 'make_response')
    def test_borehole_hydraulic_list_get_bh_level(
            self, mock_response, mock_oschema, mock_schema,
            mock_process_request):
        """Test level=borehole for BoreholeHydraulicSampleListResource."""

        routes.db = self.db
        with self.client as c:
            response = c.get('/hydws/v1/boreholes/{}?level=borehole'.\
                format(bh1_publicid_encoded))
            self.assertTrue(mock_process_request.called)
            mock_process_request.assert_called_with(
                self.db.session, borehole_id=bh1_publicid,
                format='json', level='borehole', nodata=204)
            self.assertTrue(mock_oschema.called)
            self.assertTrue(mock_response.called)

    @patch.object(routes.BoreholeHydraulicSampleListResource,
        '_process_request')
    @patch.object(routes, 'BoreholeHydraulicSampleListResourceSchema')
    @patch.object(routes, 'BoreholeSchema')
    @patch.object(routes, 'make_response')
    def test_borehole_hydraulic_list_get_sec_level(
            self, mock_response, mock_oschema, mock_schema,
            mock_process_request):
        """Test level=section for BoreholeHydraulicSampleListResource."""

        routes.db = self.db
        with self.client as c:
            response = c.get(
                '/hydws/v1/boreholes/{}?starttime=2019-01-01&level=section'.\
                    format(bh1_publicid_encoded))
            self.assertTrue(mock_process_request.called)
            mock_process_request.assert_called_with(
                self.db.session, borehole_id=bh1_publicid,
                format='json', level='section',
                starttime=datetime(2019, 1, 1), nodata=204)
            self.assertTrue(mock_oschema.called)
            self.assertTrue(mock_response.called)


    @patch.object(routes.BoreholeHydraulicSampleListResource,
        '_process_request')
    @patch.object(routes, 'BoreholeHydraulicSampleListResourceSchema')
    @patch.object(routes, 'BoreholeSchema')
    @patch.object(routes, 'make_response')
    def test_borehole_hydraulic_list_get_hyd_level(
            self, mock_response, mock_oschema, mock_schema,
            mock_process_request):
        """Test level=hydraulic for BoreholeHydraulicSampleListResource."""

        routes.db = self.db
        with self.client as c:
            response = c.get(
                '/hydws/v1/boreholes/{}?maxfluidph=10.0&level=hydraulic'.\
                    format(bh1_publicid_encoded))
            self.assertTrue(mock_process_request.called)
            mock_process_request.assert_called_with(
                self.db.session, borehole_id=bh1_publicid,
                format='json', level='hydraulic',
                maxfluidph=10., nodata=204)
            self.assertTrue(mock_oschema.called)
            self.assertTrue(mock_response.called)


    @patch.object(routes.SectionHydraulicSampleListResource, '_process_request')
    @patch.object(routes, 'SectionHydraulicSampleListResourceSchema')
    @patch.object(routes, 'HydraulicSampleSchema')
    @patch.object(routes, 'make_response')
    def test_hydraulic_list_get(self, mock_response, mock_oschema,
                                mock_schema, mock_process_request):
        """Test SectionHydraulicSampleListResource."""
        # Mock the query parameters.
        routes.db = self.db
        with self.client as c:
            response = c.get(
                '/hydws/v1/boreholes/{}/sections/{}/hydraulics?maxfluidph=10.0'.\
                    format(bh1_publicid_encoded,
                           sec1_publicid_encoded))
            self.assertTrue(mock_process_request.called)
            mock_process_request.assert_called_with(self.db.session,
                borehole_id=bh1_publicid, section_id=sec1_publicid,
                format='json', maxfluidph=10., nodata=204)
            self.assertTrue(mock_oschema.called)
            self.assertTrue(mock_response.called)


@patch.object(routes, 'boreholesection_oids')
@patch.object(routes, 'query_with_sections')
@patch.object(routes, 'Borehole')
@patch.object(routes, 'BoreholeSection')
@patch.object(routes.DynamicQuery, 'filter_level')
class BoreholeProcessRequestTestcase(unittest.TestCase):
    """
    Test cases for the _process_request fucntions within
    routes.BoreholeListResource class.

    """
    def test_borehole_list_process_request(
            self, mock_dynamicquery, mock_sec, mock_bh,
            mock_query_section, mock_sec_oids):
        params = {'level': 'section'}
        bhlr = routes.BoreholeListResource()
        session = MagicMock()
        mock_sec_oids.return_value = ['1']
        returnval = bhlr._process_request(session, **params)
        self.assertTrue(mock_sec_oids.called)
        self.assertTrue(mock_query_section.called)

        mock_dynamicquery.assert_called_with(params, 'borehole')

    def test_borehole_list_process_request_borehole(
            self, mock_dynamicquery, mock_sec, mock_bh,
            mock_query_section, mock_sec_oids):
        params = {'level': 'borehole'}
        bhlr = routes.BoreholeListResource()
        session = MagicMock()
        returnval = bhlr._process_request(session, **params)
        self.assertFalse(mock_sec_oids.called)
        self.assertFalse(mock_query_section.called)
        mock_dynamicquery.assert_called_with(params, 'borehole')

@patch.object(routes, 'hydraulicsample_oids')
@patch.object(routes, 'boreholesection_oids')
@patch.object(routes, 'make_response')
@patch.object(routes, 'Borehole')
@patch.object(routes, 'DynamicQuery')
@patch.object(routes, 'query_with_sections')
@patch.object(routes, 'query_with_sections_and_hydraulics')
class BoreholeHydraulicProcessRequestTestCase(unittest.TestCase):
    """
    Test cases for the _process_request fucntions within
    routes.BoreholeHydraulicSampleListResource class.

    """
    def test_process_request_level_section(
            self, mock_queryhydraulics, mock_querysections,
            mock_dynamicquery, mock_borehole,
            mock_response, mock_sec_ids, mock_hyd_ids):
        """
        Test level=section for BoreholeHydraulicSampleListResource
        with sections available
        """
        params = {'level': 'section'}
        bhlr = routes.BoreholeHydraulicSampleListResource()
        session = MagicMock()
        mock_sec_ids.return_value = ['1']
        mock_querysections.return_value.filter.return_value = 'query'
        returnval = bhlr._process_request(session, bh1_publicid_encoded, **params)
        self.assertTrue(mock_sec_ids.called)
        self.assertTrue(mock_querysections.called)
        self.assertFalse(mock_hyd_ids.called)
        self.assertFalse(mock_queryhydraulics.called)
        mock_dynamicquery.assert_called_with('query')
        self.assertTrue(mock_dynamicquery.return_value.return_one.called)

    def test_process_request_level_section_no_sections(
            self, mock_queryhydraulics, mock_querysections,
            mock_dynamicquery, mock_borehole,
            mock_response, mock_sec_ids, mock_hyd_ids):
        """
        Test level=section for BoreholeHydraulicSampleListResource
        with no sections available
        """
        params = {'level': 'section'}
        bhlr = routes.BoreholeHydraulicSampleListResource()
        session = MagicMock()
        mock_sec_ids.return_value = []
        returnval = bhlr._process_request(session, bh1_publicid_encoded, **params)
        self.assertTrue(mock_sec_ids.called)
        self.assertFalse(mock_querysections.called)
        self.assertFalse(mock_hyd_ids.called)
        self.assertFalse(mock_queryhydraulics.called)
        self.assertTrue(mock_dynamicquery.return_value.return_one.called)


    def test_process_request_level_hydraulic(
            self, mock_queryhydraulics, mock_querysections,
            mock_dynamicquery, mock_borehole,
            mock_response, mock_sec_ids, mock_hyd_ids):
        """
        Test level=hydraulic for BoreholeHydraulicSampleListResource
        with sections and hydraulics available
        """
        params = {'level': 'hydraulic'}
        bhlr = routes.BoreholeHydraulicSampleListResource()
        session = MagicMock()
        mock_sec_ids.return_value = ['1']
        mock_hyd_ids.return_value = ['1']
        mock_queryhydraulics.return_value.filter.return_value = 'query'
        returnval = bhlr._process_request(
            session, bh1_publicid_encoded, **params)
        self.assertTrue(mock_sec_ids.called)
        self.assertFalse(mock_querysections.called)
        self.assertTrue(mock_hyd_ids.called)
        self.assertTrue(mock_queryhydraulics.called)
        mock_dynamicquery.assert_called_with('query')
        self.assertTrue(mock_dynamicquery.return_value.return_one.called)


    def test_process_request_level_hydraulic_no_hydraulics(
            self, mock_queryhydraulics, mock_querysections,
            mock_dynamicquery, mock_borehole,
            mock_response, mock_sec_ids, mock_hyd_ids):
        """
        Test level=section for BoreholeHydraulicSampleListResource
        with sections but no hydraulics available
        """
        params = {'level': 'hydraulic'}
        bhlr = routes.BoreholeHydraulicSampleListResource()
        session = MagicMock()
        mock_sec_ids.return_value = ['1']
        mock_hyd_ids.return_value = []
        mock_querysections.return_value.filter.return_value = 'query'
        returnval = bhlr._process_request(session, bh1_publicid_encoded, **params)
        self.assertTrue(mock_sec_ids.called)
        self.assertTrue(mock_querysections.called)
        self.assertTrue(mock_hyd_ids.called)
        self.assertFalse(mock_queryhydraulics.called)
        mock_dynamicquery.assert_called_with('query')
        self.assertTrue(mock_dynamicquery.return_value.return_one.called)

@patch.object(routes, 'HydraulicSample')
@patch.object(routes, 'section_in_borehole')
@patch.object(routes, 'query_hydraulicsamples')
@patch.object(routes, 'DynamicQuery')
class SectionHydraulicProcessRequestTestcase(unittest.TestCase):
    """
    Test cases for the _process_request fucntions within
    routes.SectionHydraulicSampleListResource class.

    """
    def test_borehole_hyd_process_request_limit(
            self, mock_dynquery, mock_hydsamples, mock_in_borehole, hydsample):
        params = {}
        mock_in_borehole.return_value = ['1']
        bhlr = routes.SectionHydraulicSampleListResource()
        session = MagicMock()
        returnval = bhlr._process_request(session, bh1_publicid_encoded,
                                          sec1_publicid_encoded, **params)

        mock_dynquery.assert_called_with(mock_hydsamples())
        mock_dynquery.return_value.filter_level.assert_called_with(params, 'hydraulic')


    def test_borehole_hyd_section_process_request(
            self, mock_dynquery, mock_hydsamples, mock_in_borehole, hydsample):
        params = {'limit': 10}
        mock_in_borehole.return_value = True
        bhlr = routes.SectionHydraulicSampleListResource()
        session = MagicMock()
        returnval = bhlr._process_request(session, bh1_publicid_encoded, sec1_publicid_encoded, **params)

        mock_dynquery.return_value.format_results.assert_called_with(
            limit=10, offset=None, order_column=hydsample.datetime_value)

    def test_borehole_hyd_process_request_raises(
            self, mock_dynquery, mock_hydsamples, mock_in_borehole, hydsample):
        params = {}
        mock_in_borehole.return_value = False
        bhlr = routes.SectionHydraulicSampleListResource()
        session = MagicMock()
        with self.assertRaises(ValueError):
            bhlr._process_request(session, 'borehole_publicid', 'section_publicid', **params)


@patch.object(routes, 'DynamicQuery')
@patch.object(routes, 'lazyload')
class BoreholeSectionOIDsTestcase(unittest.TestCase):
    def test_borehole_section_oids(self, mock_lazy_load, mock_dynquery):
        session = MagicMock()
        query_params = {}
        return_val = routes.boreholesection_oids(session, **query_params)
        self.assertTrue(mock_dynquery.called)


if __name__ == '__main__':
    unittest.main()
