"""
.. module:: routes
    :synopsis: Contains resources for HYDWS route handling.

.. moduleauthor:: Laura Sarson <laura.sarson@sed.ethz.ch>

"""
import datetime as datetime

import logging
from sqlalchemy import literal, and_
from flask_restful import Api, Resource
from sqlalchemy.orm.exc import NoResultFound
from webargs.flaskparser import use_kwargs
from marshmallow import fields
from sqlalchemy.orm import subqueryload, eagerload, joinedload, joinedload_all, contains_eager, lazyload, aliased, selectinload

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
    @use_kwargs(BoreholeListResourceSchema, locations=("query",))
    @with_strict_args(BoreholeListResourceSchema, locations=("query",))
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

        resp = BoreholeSchema(many=True).dumps(resp)

        return make_response(resp, settings.MIMETYPE_JSON)

    def _process_request(self, session,
                         **query_params):
        
        query = session.query(Borehole)
        level = query_params.get('level')
        if level == 'section':
            query = query.options(lazyload(Borehole._sections))
        
        dynamic_query = DynamicQuery(query)

        # Use borehole level filtering.
        dynamic_query.filter_query(query_params,
                                   'borehole')
        return dynamic_query.return_all()


class BoreholeHydraulicSampleListResource(ResourceBase):

    LOGGER = 'hydws.server.v1.boreholehydraulicsamplelistresource'

    @with_fdsnws_exception_handling(__version__)
    @use_kwargs(BoreholeHydraulicSampleListResourceSchema,
                locations=("query", ))
    @with_strict_args(BoreholeHydraulicSampleListResourceSchema,
                locations=("query", ))
    def get(self, borehole_id, **query_params):
        borehole_id = decode_publicid(borehole_id)

        map_return_levels = [{'hydraulic': 'section',}]
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
    

    def _process_request(self, session, borehole_id,
                         **query_params):

        if not borehole_id:
            raise ValueError(f"Invalid borehole identifier: {borehole_id!r}")

        level = query_params.get('level')



        hyd_subquery = DynamicQuery(session.query(HydraulicSample.boreholesection_oid))
        sec_subquery = DynamicQuery(session.query(BoreholeSection.borehole_oid))
        if level in ['section', 'hydraulic']:
            sec_subquery.filter_query(query_params, 'section')

        if level == 'hydraulic':
            hyd_subquery.filter_query(query_params,
                                   'hydraulic')
        hyd_query = hyd_subquery.query.subquery(name="hyd_query")
        sec_query = sec_subquery.query.subquery(name="sec_query")
        print(sec_query)
        query = session.query(Borehole)
        if level == 'section':
            query = query.options(lazyload(Borehole._sections)).\
            join(BoreholeSection, isouter=True).options(contains_eager("_sections"))

        #TODO(sarsonl): Currently if querying at the hydraulic level, and no hydraulics
        # exist, then no result is output. Not sure why as using left outer joins.
        elif level == 'hydraulic':
            query = query.options(lazyload(Borehole._sections).\
                        lazyload(BoreholeSection._hydraulics)).\
                    join(sec_query,  Borehole._oid==sec_query.c.borehole_oid , isouter=True).\
                    join(hyd_query, sec_query.c._oid==hyd_query.c.boreholesection_oid,
                    isouter=True).\
                    options(contains_eager("_sections").\
                            contains_eager("_hydraulics"))
        
        
        query = query.filter(Borehole.publicid==borehole_id)
        dynamic_query = DynamicQuery(query)

        
        
        
        #if level in ['section', 'hydraulic']:
        #    dynamic_query.filter_query(query_params, 'section')
        #if level == 'hydraulic':
        #   dynamic_query.filter_query(query_params,
        #                           'hydraulic')
        print(dynamic_query.query)
        if query_params.get('limit'):
            paginate_obj = dynamic_query.paginate_query(
                query_params.get('limit'), query_params.get('page'))
            # TODO(lsarson): do something with the properties
            # next_url, has_next.
            return paginate_obj.items
        else:
            return dynamic_query.return_one()


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
    
    def _section_in_borehole(self, query, borehole_id, section_id):
        boreholesection_filter = query(Borehole).\
            options(lazyload(Borehole._sections)).\
            filter(Borehole.publicid == borehole_id).\
            filter(BoreholeSection.publicid == section_id)

        section_exists = query(literal(True)).\
            filter(boreholesection_filter.exists()).scalar()

        return section_exists

    def _process_request(self, session, borehole_id=None, section_id=None,
                         **query_params):
        if not borehole_id or not section_id:
            raise ValueError(f"Invalid borehole or section identifier: "
                             "{borehole_id!r} {section_id!r}")

        section_exists = self._section_in_borehole(session.query,
                                                   borehole_id, section_id)

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
                    '{}'.format(settings.HYDWS_PATH_BOREHOLES))
api_v1.add_resource(BoreholeHydraulicSampleListResource,
                    '{}/<borehole_id>'.format(settings.HYDWS_PATH_BOREHOLES))
api_v1.add_resource(SectionHydraulicSampleListResource,
                    '{}/<borehole_id>{}/<section_id>{}'.format(
                        settings.HYDWS_PATH_BOREHOLES,
                        settings.HYDWS_PATH_SECTIONS,
                        settings.HYDWS_PATH_HYDRAULICS))
