"""
HYDWS resources.
"""

import logging

from flask_restful import Api, Resource
from sqlalchemy.orm.exc import NoResultFound
from webargs.flaskparser import use_kwargs

from hydws import __version__
from hydws.db import orm
from hydws.server import db, settings
from hydws.server.errors import FDSNHTTPError
from hydws.server.misc import (with_fdsnws_exception_handling, decode_publicid,
                               make_response, DynamicQuery)
from hydws.server.v1 import blueprint
from hydws.server.v1.ostream.schema import (BoreholeSchema,
                                            BoreholeSectionSchema,
                                            BoreholeSectionHydraulicSampleSchema,
                                            SectionHydraulicSampleSchema,
                                            HydraulicSampleSchema)
from hydws.server.v1.parser import (
    BoreholeHydraulicSampleListResourceSchema,
    BoreholeListResourceSchema,
    SectionHydraulicSampleListResourceSchema)

api_v1 = Api(blueprint)


# Mapping of columns to comparison operator and input parameter.
# [(orm column, operator, input comparison value)]
# Filter on hydraulics fields:
filter_hydraulics = [
    ('m_datetime', 'ge', 'starttime'),
    ('m_datetime', 'le', 'endtime'),
    ('m_toptemperature', 'ge', 'mintoptemperature'),
    ('m_toptemperature', 'le', 'maxtoptemperature'),
    ('m_bottomtemperature', 'ge', 'minbottomtemperature'),
    ('m_bottomtemperature', 'le', 'maxbottomtemperature'),
    ('m_toppressure', 'ge', 'mintoppressure'),
    ('m_toppressure', 'le', 'maxtoppressure'),
    ('m_bottompressure', 'ge', 'minbottompressure'),
    ('m_bottompressure', 'le', 'maxbottompressure'),
    ('m_topflow', 'ge', 'mintopflow'),
    ('m_topflow', 'le', 'maxtopflow'),
    ('m_bottomflow', 'ge', 'minbottomflow'),
    ('m_bottomflow', 'le', 'maxbottomflow'),
    ('m_fluiddensity', 'ge', 'minfluiddensity'),
    ('m_fluiddensity', 'le', 'maxfluiddensity'),
    ('m_fluidviscosity', 'ge', 'minfluidviscosity'),
    ('m_fluidviscosity', 'le', 'maxfluidviscosity'),
    ('m_fluidph', 'ge', 'minfluidph'),
    ('m_fluidph', 'le', 'maxfluidph')]

filter_boreholes = [
    ('m_latitude', 'ge', 'minlatitude'),
    ('m_latitude', 'le', 'maxlatitude'),
    ('m_longitude', 'ge', 'minlongitude'),
    ('m_longitude', 'le', 'maxlongitude')]

class ResourceBase(Resource):

    LOGGER = 'hydws.server.v1.resource'

    def __init__(self, logger=None):
        super().__init__()
        self.logger = logging.getLogger(logger if logger else self.LOGGER)

    def get(self):
        """
        Template method to be implemented by HYDWS resources in order to serve
        HTTP GET requests.
        """
        raise NotImplementedError

    def _handle_nodata(self, query_params):
        """
        Handle an empty query result

        :param dict query_params: Dict of query parameters

        :raises: :py:class:`FDSNHTTPError`
        """
        raise FDSNHTTPError.create(
            int(query_params.get(
                'nodata',
                settings.FDSN_DEFAULT_NO_CONTENT_ERROR_CODE)))

    def _process_request(self, borehole_id=None, section_id=None,
                         **query_params):
        """
        Template method intended to process a request

        :param borehole_id: Borehole publicid
        :type borehole_id: str or None
        :param section_id: Borehole section publicid
        :type section_id: str or None
        """
        raise NotImplementedError


class BoreholeListResource(ResourceBase):

    LOGGER = 'hydws.server.v1.boreholelistresource'

    @with_fdsnws_exception_handling(__version__)
    @use_kwargs(BoreholeListResourceSchema(), locations=("query",))
    def get(self, **query_params):
        
        self.logger.debug(
            f"Received request: "
            f"query_params={query_params}")

        resp = self._process_request(db.session,
                                     **query_params)

        if not resp:
            self._handle_nodata(query_params)

        # TODO(damb): Serialize according to query_param format=JSON|XML
        # format response
        level = query_params.get('level')
        if level == 'borehole':
            resp = BoreholeSchema(many=True).dumps(resp)
        elif level == 'section':
            resp = BoreholeSectionSchema(many=True).dumps(resp)

        return make_response(resp, settings.MIMETYPE_JSON)

    def _process_request(self, session,
                         **query_params):

        
        level = query_params.get('level')
        
        query = session.query(orm.Borehole)
        if level == 'section':
            query = query.join(orm.BoreholeSection)
        dynamic_query = DynamicQuery(query)

        # XXX(damb): Emulate QuakeML type Epoch (though on DB level it is
        # defined as QuakeML type OpenEpoch

        # XXX(lsarson): Should there be functionality to add OR queries?
        # if so then there should have another method added to DynamicQuery

        # XXX(lsarson): Filter None first or query will fail due to type differences.
        dynamic_query.filter_query(orm.Borehole, query_params,
                                   filter_boreholes)
        try: 
            return dynamic_query.query.all()

        except NoResultFound:
            return None

class BoreholeHydraulicSampleListResource(ResourceBase):

    LOGGER = 'hydws.server.v1.boreholehydraulicsamplelistresource'

    @with_fdsnws_exception_handling(__version__)
    @use_kwargs(BoreholeHydraulicSampleListResourceSchema,
                locations=("query", ))
    def get(self, borehole_id, **query_params):
        borehole_id = decode_publicid(borehole_id)

        self.logger.debug(
            f"Received request: borehole_id={borehole_id}, "
            f"query_params={query_params}")

        resp = self._process_request(db.session, borehole_id=borehole_id,
                                     **query_params)

        if not resp:
            self._handle_nodata(query_params)

        # TODO(damb): Serialize according to query_param format=JSON|XML
        # format response
        print("#################### level: ", query_params.get('level'))
        level = query_params.get('level')
        if level == 'borehole':
            resp = BoreholeSchema(many=True).dumps(resp)
        elif level == 'section':
            resp = BoreholeSectionSchema(many=True).dumps(resp)
        elif level == 'hydraulics':
            resp = BoreholeHydraulicSampleSchema(many=True).dumps(resp)
        return make_response(resp, settings.MIMETYPE_JSON)
    

    def _process_request(self, session, borehole_id,
                         **query_params):

        if not borehole_id:
            raise ValueError(f"Invalid borehole identifier: {borehole_id!r}")

        level = query_params.get('level')
        query = session.query(orm.Borehole)
        if level == 'section':
            query = query.join(orm.BoreholeSection)
        elif level == 'hydraulics':
            query = query.join(orm.HydraulicsSample)
        
        query = query.filter(orm.Borehole.m_publicid==borehole_id)

        dynamic_query = DynamicQuery(query)

        # XXX(damb): Emulate QuakeML type Epoch (though on DB level it is
        # defined as QuakeML type OpenEpoch

        # XXX(lsarson): Should there be functionality to add OR queries?
        # if so then there should have another method added to DynamicQuery

        # XXX(lsarson): Filter None first or query will fail due to type differences.
        dynamic_query.filter_query(orm.HydraulicSample, query_params,
                                   filter_hydraulics)
        try: 
            return dynamic_query.query.all()

        except NoResultFound:
            return None


#class BoreholeHydraulicSampleListResource(ResourceBase):
#
#    LOGGER = 'hydws.server.v1.boreholehydraulicsamplelistresource'
#
#    @with_fdsnws_exception_handling(__version__)
#    @use_kwargs(BoreholeHydraulicSampleListResourceSchema(),
#                locations=("query", ))
#    def get(self, borehole_id, **query_params):
#        borehole_id = decode_publicid(borehole_id)
#
#        self.logger.debug(
#            f"Received request: borehole_id={borehole_id}, "
#            f"query_params={query_params}")
#
#        resp = self._process_request(db.session, borehole_id=borehole_id,
#                                     **query_params)
#
#        if not resp:
#            self._handle_nodata(query_params)
#
#        # TODO(damb): Serialize according to query_param format=JSON|XML
#        # format response
#        resp = SectionHydraulicSampleSchema(many=True).dumps(resp)
#
#        return make_response(resp, settings.MIMETYPE_JSON)
#    
#
#    def _process_request(self, session, borehole_id=None, section_id=None,
#                         **query_params):
#
#        if not borehole_id:
#            raise ValueError(f"Invalid borehole identifier: {borehole_id!r}")
#
#        query = session.query(orm.Borehole).\
#                join(orm.BoreholeSection).\
#                join(orm.HydraulicSample).\
#            filter(orm.Borehole.m_publicid==borehole_id)
#
#        dynamic_query = DynamicQuery(query)
#
#        # XXX(damb): Emulate QuakeML type Epoch (though on DB level it is
#        # defined as QuakeML type OpenEpoch
#
#        # XXX(lsarson): Should there be functionality to add or queries?
#        # if so then there should have another method added to DynamicQuery
#
#        # XXX(lsarson): Filter None first or query will fail due to type differences.
#        dynamic_query.filter_query(orm.HydraulicSample, query_params,
#                                   filter_hydraulics)
#
#        try:
#            return dynamic_query.query.all()
#        except NoResultFound:
#            return None

class SectionHydraulicSampleListResource(ResourceBase):

    LOGGER = 'hydws.server.v1.sectionhydraulicsamplelistresource'

    @with_fdsnws_exception_handling(__version__)
    @use_kwargs(SectionHydraulicSampleListResourceSchema(),
                locations=("query", ))
    def get(self, borehole_id, section_id, **query_params):
        borehole_id = decode_publicid(borehole_id)
        section_id = decode_publicid(section_id)
        self.logger.debug(
            f"Received request: borehole_id={borehole_id}, "
            f"section_id={section_id}, "
            f"query_params={query_params}")

        resp = self._process_request(db.session, borehole_id=borehole_id,
                                     section_id=section_id, **query_params)

        if not resp:
            self._handle_nodata(query_params)

        # TODO(damb): Serialize according to query_param format=JSON|XML
        # format response
        resp = HydraulicSampleSchema(many=True).dumps(resp)

        return make_response(resp, settings.MIMETYPE_JSON)
    

    def _process_request(self, session, borehole_id=None, section_id=None,
                         **query_params):

        if not borehole_id:
            raise ValueError(f"Invalid borehole identifier: {borehole_id!r}")

        query = session.query(orm.HydraulicSample).\
                join(orm.BoreholeSection).\
                join(orm.Borehole).\
            filter(orm.Borehole.m_publicid==borehole_id).\
            filter(orm.BoreholeSection.m_publicid==section_id)

        dynamic_query = DynamicQuery(query)

        # XXX(damb): Emulate QuakeML type Epoch (though on DB level it is
        # defined as QuakeML type OpenEpoch
        starttime = query_params.get('starttime')
        if starttime:
            query = query.\
                filter((orm.BoreholeSection.m_starttime >= starttime) &  # noqa
                       (orm.BoreholeSection.m_starttime != None)).\
                filter(orm.HydraulicSample.m_datetime_value >= starttime)

        endtime = query_params.get('endtime')
        if endtime:
            query = query.\
                filter((orm.BoreholeSection.m_endtime <= endtime) |  # noqa
                       (orm.BoreholeSection.m_endtime == None)).\
                filter(orm.HydraulicSample.m_datetime_value <= endtime)

        # XXX(lsarson): Filter None first or query will fail due to type differences.
        dynamic_query.filter_query(orm.HydraulicSample, query_params,
                                   filter_hydraulics)

        try:
            return dynamic_query.query.all()
        except NoResultFound:
            return None



# TODO(damb):
# Add resources to API

api_v1.add_resource(BoreholeListResource,
                    '{}/'.format(settings.HYDWS_PATH_BOREHOLES))
api_v1.add_resource(BoreholeHydraulicSampleListResource,
                    '{}/<borehole_id>'.format(settings.HYDWS_PATH_BOREHOLES))
api_v1.add_resource(SectionHydraulicSampleListResource,
                    '{}/<borehole_id>{}/<section_id>{}'.format(
                        settings.HYDWS_PATH_BOREHOLES,
                        settings.HYDWS_PATH_SECTIONS,
                        settings.HYDWS_PATH_HYDRAULICS))
