"""Unit testing for hydws.server.v1.routes.py."""
import unittest
import base64

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
    def test_borehole_list_get(self, mock_response, mock_oschema, mock_schema, mock_process_request):
        # Mock the query parameters.
        mock_schema.return_value.dump.return_value = {'f': 10}
        routes.db = self.db
        mock_dumps = mock_oschema.return_value.dumps
        mock_dumps.return_value = MagicMock()
        with self.client as c:
            response = c.get('/v1/boreholes?')
            mock_process_request.assert_called_with(self.db.session, f=10)
            self.assertTrue(mock_oschema.called)
            self.assertTrue(mock_dumps.called)
            self.assertTrue(mock_response.called)

    @patch.object(routes.BoreholeHydraulicSampleListResource, '_process_request')
    @patch.object(routes, 'BoreholeHydraulicSampleListResourceSchema')
    @patch.object(routes, 'BoreholeSchema')
    @patch.object(routes, 'make_response')
    def test_borehole_hydraulic_list_get(self, mock_response, mock_oschema, mock_schema, mock_process_request):
        # Mock the query parameters.
        mock_schema.return_value.dump.return_value = {'f': 10}
        routes.db = self.db
        mock_dumps = mock_oschema.return_value.dumps
        mock_dumps.return_value = MagicMock()
        with self.client as c:
            response = c.get('/v1/boreholes/{}?'.format(bh1_publicid_encoded))
            self.assertTrue(mock_process_request.called)
            mock_process_request.assert_called_with(self.db.session, borehole_id=bh1_publicid, f=10)
            self.assertTrue(mock_oschema.called)
            self.assertTrue(mock_dumps.called)
            self.assertTrue(mock_response.called)



    @patch.object(routes.SectionHydraulicSampleListResource, '_process_request')
    @patch.object(routes, 'SectionHydraulicSampleListResourceSchema')
    @patch.object(routes, 'HydraulicSampleSchema')
    @patch.object(routes, 'make_response')
    def test_hydraulic_list_get(self, mock_response, mock_oschema, mock_schema, mock_process_request):
        # Mock the query parameters.
        mock_schema.return_value.dump.return_value = {'f': 10}
        routes.db = self.db
        mock_dumps = mock_oschema.return_value.dumps
        mock_dumps.return_value = MagicMock()
        with self.client as c:
            response = c.get('/v1/boreholes/{}/sections/{}/hydraulics?'.format(bh1_publicid_encoded,
                sec1_publicid_encoded))
            print(response)
            self.assertTrue(mock_process_request.called)
            mock_process_request.assert_called_with(self.db.session,
                borehole_id=bh1_publicid,
                section_id=sec1_publicid, f=10)
            self.assertTrue(mock_oschema.called)
            self.assertTrue(mock_dumps.called)
            self.assertTrue(mock_response.called)


@patch.object(routes, 'BoreholeSchema')
@patch.object(routes, 'make_response')
@patch.object(routes, 'BoreholeSection')
@patch.object(routes.DynamicQuery, 'filter_query')
@patch.object(routes, 'lazyload')
class BoreholeProcessRequestTestcase(unittest.TestCase):
    """
    Test cases for the _process_request fucntions within
    routes.BoreholeListResource class.

    """
    def test_borehole_list_process_request(
            self, mock_lazyload, mock_dynamicquery, mock_sec,
            mock_response, mock_oschema):
        params = {'level': 'section'}
        bhlr = routes.BoreholeListResource()
        session = MagicMock()
        returnval = bhlr._process_request(session, **params)

        #session.query.assert_called_with(mock_sec)
        #mock_lazyload.assert_called_with(mock_sec._borehole)
        #mock_dynamicquery.assert_called_with(params, 'borehole')

    def test_borehole_list_process_request_borehole(
            self, mock_lazyload, mock_dynamicquery, mock_borehole,
            mock_response, mock_oschema):
        params = {'level': 'borehole'}
        bhlr = routes.BoreholeListResource()
        session = MagicMock()
        returnval = bhlr._process_request(session, **params)

        #session.query.assert_called_with(mock_borehole)
        #self.assertFalse(mock_lazyload.called)
        #mock_dynamicquery.assert_called_with(params, 'borehole')

@patch.object(routes.BoreholeHydraulicSampleListResource, '_hydraulicsample_oids')
@patch.object(routes.BoreholeHydraulicSampleListResource, '_boreholesection_oids')
@patch.object(routes, 'BoreholeSchema')
@patch.object(routes, 'make_response')
@patch.object(routes, 'Borehole')
@patch.object(routes, 'DynamicQuery')
@patch.object(routes.BoreholeHydraulicSampleListResource, '_query_with_sections')
@patch.object(routes.BoreholeHydraulicSampleListResource, '_query_with_sections_and_hydraulics')
class BoreholeHydraulicProcessRequestTestCase(unittest.TestCase):
    """
    Test cases for the _process_request fucntions within
    routes.BoreholeHydraulicSampleListResource class.

    """
    def test_borehole_hyd_section_process_request(
            self, mock_querysections, mock_queryhydraulics, mock_dynamicquery, mock_borehole,
            mock_response, mock_oschema, mock_sec_ids, mock_hyd_ids):
        params = {'level': 'section'}
        bhlr = routes.BoreholeHydraulicSampleListResource()
        session = MagicMock()
        returnval = bhlr._process_request(session, bh1_publicid_encoded, **params)

        mock_sec_ids.assert_called_with("")
        #mock_lazyload.assert_called_with(mock_borehole._sections)
        #mock_dynamicquery.return_value.filter_level.assert_called_with(params, 'hydraulic')
        #self.assertTrue(mock_dynamicquery.return_value.return_all.called)

    def test_borehole_hyd_section_process_request(
            self, mock_querysections, mock_queryhydraulics,  mock_dynamicquery, mock_borehole,
            mock_response, mock_oschema, mock_sec, mock_hyd):
        params = {'level': 'hydraulic'}
        bhlr = routes.BoreholeHydraulicSampleListResource()
        session = MagicMock()
        returnval = bhlr._process_request(session, bh1_publicid_encoded, **params)

        #session.query.assert_called_with(mock_hyd)
        #mock_lazyload.assert_has_calls([call(mock_hyd._section),
        #    call(mock_lazyload(mock_sec._borehole)),
        #    call(mock_sec._borehole)])
        #mock_lazyload.assert_called_with(mock_borehole._sections)
        #mock_dynamicquery.return_value.filter_level.assert_called_with(params, 'hydraulic')
        #self.assertTrue(mock_dynamicquery.return_value.return_all.called)





@patch.object(routes, 'BoreholeSchema')
@patch.object(routes, 'make_response')
@patch.object(routes, 'HydraulicSample')
@patch.object(routes, 'BoreholeSection')
@patch.object(routes, 'DynamicQuery')
@patch.object(routes, 'lazyload')
@patch.object(routes.SectionHydraulicSampleListResource,
              '_section_in_borehole')
class SectionHydraulicProcessRequestTestcase(unittest.TestCase):
    """
    Test cases for the _process_request fucntions within
    routes.SectionHydraulicSampleListResource class.

    """
    def test_borehole_hyd_process_request_limit(
            self, mock_in_borehole, mock_lazyload, mock_dynamicquery,
            mock_boreholesection, mock_hydsample, mock_response,
            mock_oschema):
        params = {}
        mock_in_borehole.return_value = True
        bhlr = routes.SectionHydraulicSampleListResource()
        session = MagicMock()
        returnval = bhlr._process_request(session, bh1_publicid_encoded, sec1_publicid_encoded, **params)

        #session.query.assert_called_with(mock_hydsample)
        #session.query.return_value.options.return_value.join.assert_called_with(mock_boreholesection)
        #mock_lazyload.assert_called_with(mock_hydsample._section)
        #mock_dynamicquery.return_value.filter_level.assert_called_with(params, 'hydraulic')


    def test_borehole_hyd_section_process_request(
            self, mock_in_borehole, mock_lazyload, mock_dynamicquery,
            mock_boreholesection, mock_hydsample, mock_response,
            mock_oschema):
        params = {'limit': 10}
        mock_in_borehole.return_value = True
        bhlr = routes.SectionHydraulicSampleListResource()
        session = MagicMock()
        returnval = bhlr._process_request(session, bh1_publicid_encoded, sec1_publicid_encoded, **params)

        #mock_dynamicquery.return_value.format_results.assert_called_with(limit=10, offset=None, order_by=mock_hydsample.datetime_value)

    def test_borehole_hyd_process_request_raises(
            self, mock_in_borehole, mock_lazyload, mock_dynamicquery,
            mock_boreholesection, mock_hydsample, mock_response,
            mock_oschema):
        params = {}
        mock_in_borehole.return_value = False
        bhlr = routes.SectionHydraulicSampleListResource()
        session = MagicMock()
        with self.assertRaises(ValueError):
            bhlr._process_request(session, 'borehole_publicid', 'section_publicid', **params)

if __name__ == '__main__':
    unittest.main()
