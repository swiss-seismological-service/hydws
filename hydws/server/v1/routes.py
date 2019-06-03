"""
HYDWS resources.
"""

import logging
from sqlalchemy import literal
from flask_restful import Api, Resource
from sqlalchemy.orm.exc import NoResultFound
from webargs.flaskparser import use_kwargs
from marshmallow import fields
from sqlalchemy.orm import subqueryload, eagerload, joinedload, contains_eager, lazyload

from hydws import __version__
from hydws.db.orm import Borehole, BoreholeSection, HydraulicSample
from hydws.server import db, settings
from hydws.server.errors import FDSNHTTPError
from hydws.server.misc import (with_fdsnws_exception_handling, decode_publicid,
                               make_response)
from hydws.server.v1 import blueprint
from hydws.server.v1.ostream.schema import (BoreholeSchema,
                                            HydraulicSampleSchema)
from hydws.server.v1.parser import (
    BoreholeHydraulicSampleListResourceSchema,
    BoreholeListResourceSchema,
    SectionHydraulicSampleListResourceSchema)

from hydws.server.query_filters import DynamicQuery
from hydws.server.strict import with_strict_args

api_v1 = Api(blueprint)

some_parser = {"maxlatitude": fields.Str(), "maxlongitude": fields.Str()}


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
    @with_strict_args(BoreholeListResourceSchema, locations=("query",))
    def get(self, **query_params):
        params_schema = BoreholeListResourceSchema()
        query_params = params_schema.dump(query_params)
        self.logger.debug(
            f"Received request: "
            f"query_params={query_params}")

        resp = self._process_request(db.session,
                                     **query_params)

        if not resp:
            self._handle_nodata(query_params)

        # TODO(damb): Serialize according to query_param format=JSON|XML
        # format response

        resp = BoreholeSchema(many=True).dumps(resp)

        return make_response(resp, settings.MIMETYPE_JSON)

    def _process_request(self, session,
                         **query_params):
        
        query = session.query(Borehole)

        level = query_params.get('level')
        if level == 'section':
            query = query.options(lazyload(Borehole._sections))
        dynamic_query = DynamicQuery(query)

        # XXX(damb): Emulate QuakeML type Epoch (though on DB level it is
        # defined as QuakeML type OpenEpoch

        dynamic_query.filter_query(query_params,
                                   'borehole')
        try: 
            return dynamic_query.return_all()

        except NoResultFound:
            return None

class BoreholeHydraulicSampleListResource(ResourceBase):

    LOGGER = 'hydws.server.v1.boreholehydraulicsamplelistresource'

    @with_fdsnws_exception_handling(__version__)
    @use_kwargs(BoreholeHydraulicSampleListResourceSchema,
                locations=("query", ))
    @with_strict_args(BoreholeHydraulicSampleListResourceSchema,
                locations=("query", ))
    def get(self, borehole_id, **query_params):
        borehole_id = decode_publicid(borehole_id)
        params_schema = BoreholeListResourceSchema()
        query_params = params_schema.dump(query_params)
        self.logger.debug(
            f"Received request: borehole_id={borehole_id}, "
            f"query_params={query_params}")

        resp = self._process_request(db.session, borehole_id=borehole_id,
                                     **query_params)

        if not resp:
            self._handle_nodata(query_params)

        # TODO(damb): Serialize according to query_param format=JSON|XML
        # format response
        resp = BoreholeSchema(many=True).dumps(resp)

        return make_response(resp, settings.MIMETYPE_JSON)
    

    def _process_request(self, session, borehole_id,
                         **query_params):

        if not borehole_id:
            raise ValueError(f"Invalid borehole identifier: {borehole_id!r}")

        level = query_params.get('level')

        query = session.query(Borehole)
        if level == 'section':
            query = query.options(lazyload(Borehole._sections))

        elif level == 'hydraulic':
            query = query.options(lazyload(Borehole._sections).\
                        lazyload(BoreholeSection._hydraulics))
        
        query = query.filter(Borehole.publicid==borehole_id)

        dynamic_query = DynamicQuery(query)
        dynamic_query.filter_query(query_params,
                                   'hydraulic')

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
    @use_kwargs(SectionHydraulicSampleListResourceSchema,
                locations=("query", ))
    @with_strict_args(SectionHydraulicSampleListResourceSchema,
                locations=("query", ))
    def get(self, borehole_id, section_id, **query_params):

        borehole_id = decode_publicid(borehole_id)
        section_id = decode_publicid(section_id)
        params_schema = BoreholeListResourceSchema()
        query_params = params_schema.dump(query_params)
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

        boreholesection_filter = session.query(Borehole).\
            options(lazyload(Borehole._sections)).\
            filter(Borehole.publicid == borehole_id).\
            filter(BoreholeSection.publicid == section_id)

        section_exists = session.query(literal(True)).\
            filter(boreholesection_filter.exists()).scalar()

        if not section_exists:
            raise ValueError("Borehole Section is not a child of Borehole.")

        # Join required to filter on publicid, lazyload required for
        # schema relationships.
        query = session.query(HydraulicSample).\
            options(lazyload(HydraulicSample._section)).\
            join(BoreholeSection)

        query = query.filter(BoreholeSection.publicid==section_id)

        dynamic_query = DynamicQuery(query)

        dynamic_query.filter_query(query_params,
                                   'hydraulic')

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
