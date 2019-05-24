"""
HYDWS resources.
"""

import logging

from flask_restful import Api, Resource
from sqlalchemy.orm.exc import NoResultFound
from webargs.flaskparser import use_kwargs
from marshmallow import fields

from hydws import __version__
from hydws.db import orm
from hydws.server import db, settings
from hydws.server.errors import FDSNHTTPError
from hydws.server.misc import (with_fdsnws_exception_handling, decode_publicid,
                               make_response)
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
from hydws.server.query_filters import DynamicQuery

api_v1 = Api(blueprint)


some_parser = {"maxlatitude": fields.Str(), "maxlongitude": fields.Str()}

# Mapping of columns to comparison operator and input parameter.
# [(orm column, operator, input comparison value)]
# Filter on hydraulics fields:
filter_hydraulics = [
    ('datetime', 'ge', 'starttime'),
    ('datetime', 'le', 'endtime'),
    ('toptemperature', 'ge', 'mintoptemperature'),
    ('toptemperature', 'le', 'maxtoptemperature'),
    ('bottomtemperature', 'ge', 'minbottomtemperature'),
    ('bottomtemperature', 'le', 'maxbottomtemperature'),
    ('toppressure', 'ge', 'mintoppressure'),
    ('toppressure', 'le', 'maxtoppressure'),
    ('bottompressure', 'ge', 'minbottompressure'),
    ('bottompressure', 'le', 'maxbottompressure'),
    ('topflow', 'ge', 'mintopflow'),
    ('topflow', 'le', 'maxtopflow'),
    ('bottomflow', 'ge', 'minbottomflow'),
    ('bottomflow', 'le', 'maxbottomflow'),
    ('fluiddensity', 'ge', 'minfluiddensity'),
    ('fluiddensity', 'le', 'maxfluiddensity'),
    ('fluidviscosity', 'ge', 'minfluidviscosity'),
    ('fluidviscosity', 'le', 'maxfluidviscosity'),
    ('fluidph', 'ge', 'minfluidph'),
    ('fluidph', 'le', 'maxfluidph')]

filter_boreholes = [
    ('latitude', 'ge', 'minlatitude'),
    ('latitude', 'le', 'maxlatitude'),
    ('longitude', 'ge', 'minlongitude'),
    ('longitude', 'le', 'maxlongitude')]



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

    # For some reason, if invalid query parameters are used,
    # no exception or anything is raised, even though the default
    # functionality means that an exception should be raised.
    @with_fdsnws_exception_handling(__version__)
    @use_kwargs(BoreholeListResourceSchema, locations=("query",))
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
        level = query_params.get('level')
        if level == 'borehole':
            resp = BoreholeSchema(many=True).dumps(resp)
        elif level == 'section':
            resp = BoreholeSectionSchema(many=True).dumps(resp)
        elif level == 'hydraulic':
            resp = BoreholeSectionHydraulicSampleSchema(many=True).dumps(resp)
        return make_response(resp, settings.MIMETYPE_JSON)
    

    def _process_request(self, session, borehole_id,
                         **query_params):

        if not borehole_id:
            raise ValueError(f"Invalid borehole identifier: {borehole_id!r}")


        # XXX(sarsonl) explicitly adding on tables seperately on condition
        # results in problems joining tables - outer join undefined.
        level = query_params.get('level')
        if level == 'borehole':
            query = session.query(orm.Borehole)
        if level == 'section':
            query = session.query(orm.Borehole).\
                join(orm.BoreholeSection)

            order_by_columns = [
                getattr(orm.BoreholeSection,
                        settings.HYDWS_SECTIONS_ORDER_BY)]
        elif level == 'hydraulic':
            query = session.query(orm.Borehole).\
                join(orm.BoreholeSection).\
                join(orm.HydraulicSample)

            order_by_columns = [
                getattr(orm.BoreholeSection,
                        settings.HYDWS_SECTIONS_ORDER_BY),
                getattr(orm.HydraulicSample,
                        settings.HYDWS_HYDRAULICS_ORDER_BY)]
            
        
        query = query.filter(orm.Borehole.publicid==borehole_id)
        dynamic_query = DynamicQuery(query)


        # XXX(damb): Emulate QuakeML type Epoch (though on DB level it is
        # defined as QuakeML type OpenEpoch

        # XXX(lsarson): Should there be functionality to add OR queries?
        # if so then there should have another method added to DynamicQuery

        # XXX(lsarson): Filter None first or query will fail due to type differences.
        dynamic_query.filter_query(orm.HydraulicSample, query_params,
                                   filter_hydraulics)

        # XXX(lsarson): should this be defined on the orm instead, 
        # so that if this table returned it will always be in that order?
        if level == 'sections':
            dynamic_query.order_by_query(
                orm.BoreholeSection, settings.HYDWS_SECTIONS_ORDER_BY)
        if level == 'hydraulic':
            dynamic_query.order_by_query(
                orm.BoreholeSection, settings.HYDWS_SECTIONS_ORDER_BY)
            dynamic_query.order_by_query(
                orm.HydraulicSample, settings.HYDWS_HYDRAULICS_ORDER_BY)

        if query_params.get('limit'):
            paginate_obj = dynamic_query.paginate_query(
                query_params.get('limit'), query_params.get('page'))
            # TODO(lsarson): do something with the properties
            # next_url, has_next.
            return paginate_obj.items
        else:
            return dynamic_query.return_all()


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
            filter(orm.Borehole.publicid==borehole_id).\
            filter(orm.BoreholeSection.publicid==section_id)

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

        dynamic_query.order_by_query(
            orm.BoreholeSection, settings.HYDWS_SECTIONS_ORDER_BY)
        dynamic_query.order_by_query(
            orm.HydraulicSample, settings.HYDWS_HYDRAULICS_ORDER_BY)

        if query_params.get('limit'):
            paginate_obj = dynamic_query.paginate_query(
                query_params.get('limit'), query_params.get('page'))
            # Todo(lsarson): do something with the properties
            # next_url, has_next.
            return paginate_obj.items
        else:
            return dynamic_query.return_all()


api_v1.add_resource(BoreholeListResource,
                    '{}/'.format(settings.HYDWS_PATH_BOREHOLES))
api_v1.add_resource(BoreholeHydraulicSampleListResource,
                    '{}/<borehole_id>'.format(settings.HYDWS_PATH_BOREHOLES))
api_v1.add_resource(SectionHydraulicSampleListResource,
                    '{}/<borehole_id>{}/<section_id>{}'.format(
                        settings.HYDWS_PATH_BOREHOLES,
                        settings.HYDWS_PATH_SECTIONS,
                        settings.HYDWS_PATH_HYDRAULICS))
