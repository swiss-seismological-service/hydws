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
                               make_response)
from hydws.server.v1 import blueprint
from hydws.server.v1.ostream.schema import BoreholeSchema
from hydws.server.v1.parser import BoreholeHydraulicDataListResourceSchema


api_v1 = Api(blueprint)


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

    def get(self):
        pass


class BoreholeResource(ResourceBase):

    def get(self, borehole_id):
        pass

class FilterQuery(object):
    def __init__(self, query):
        self.query = query

    def _filter_query(self, query_name, orm_tablename, orm_paramname, filter_op):

        #operator_methods = {'egt': 'egt_query_filter',
        #        'elt': 'elt_query_filter',
        #        'eq': 'eq_query_filter',
        #        'neq': 'neq_query_filter'}     
        
        query_param = query_params.get(query_name)
        if query_param:
            orm_methodname = getattr(orm, orm_tablename)
            orm_param = getattr(orm_methodname, prm_paramname)

             try:
                 #getattr(self, operator_methods[filter_op])(orm_param, query_param)
                 
                 getattr(self, filter_op)(orm_param, query_param)
            except:
                raise ValueError('No filter method exists for: {}'.format(filter_op))
            #if filter_op == 'egt':
            #    self.egt_query_filter(orm_param, query_parameter)
            #elif filter_op == 'elt':
            #    self.elt_query_filter(orm_param, query_parameter)
            #elif filter_op == 'eq':
            #    self.eq_query_filter(orm_param, query_parameter)
            #elif filter_op == 'neq':
            #    self.neq_query_filter(orm_param, query_parameter)
            #else:
            #    raise ValueError('No filter method exists for: {}'.format(filter_op))



    def egt_query_filter(self, orn_param, query_param):
            query = self.query.filter(orm_param >= query_param)   


    def elt_query_filter(self, query_name, orm_tablename, orm_paramname, filter_op):
            query = self.query.filter(orm_param <= query_param)   


    def eq_query_filter(self, query_name, orm_tablename, orm_paramname, filter_op):
            query = self.query.filter(orm_param == query_param)   
            

    def neq_query_filter(self, query_name, orm_tablename, orm_paramname, filter_op):
            query = self.query.filter(orm_param != query_param)   


class BoreholeHydraulicDataListResource(ResourceBase):

    LOGGER = 'hydws.server.v1.boreholehydraulicdatalistresource'

    @with_fdsnws_exception_handling(__version__)
    @use_kwargs(BoreholeHydraulicDataListResourceSchema(),
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
        resp = BoreholeSchema().dumps(resp)

        return make_response(resp, settings.MIMETYPE_JSON)

    def _process_request(self, session, borehole_id=None, section_id=None,
                         **query_params):

        if not borehole_id:
            raise ValueError(f"Invalid borehole identifier: {borehole_id!r}")

        query = session.query(orm.Borehole).\
            join(orm.BoreholeSection).\
            join(orm.HydraulicSample).\
            filter(orm.Borehole.m_publicid==borehole_id)

        filter_statement = FilterQuery(query)

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

        # TODO(damb): Add additional filter criteria
        
        


        try:
            return query.\
                order_by(orm.BoreholeSection.m_starttime).\
                order_by(orm.HydraulicSample.m_datetime_value).\
                one()
        except NoResultFound:
            return None


class SectionHydraulicDataListResource(ResourceBase):

    def get(self, borehole_id, section_id):
        pass


# TODO(damb):
# Add resources to API

api_v1.add_resource(BoreholeHydraulicDataListResource,
                    '{}/<borehole_id>'.format(settings.HYDWS_PATH_BOREHOLES))
