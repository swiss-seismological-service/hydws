"""
.. module:: routes
    :synopsis: Contains resources for HYDWS route handling.

.. moduleauthor:: Laura Sarson <laura.sarson@sed.ethz.ch>

"""
import datetime as datetime

import logging
from sqlalchemy import literal, or_
from flask_restful import Api, Resource
from sqlalchemy.orm.exc import NoResultFound
from webargs.flaskparser import use_kwargs
from sqlalchemy.orm import contains_eager, lazyload
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
        

        level = query_params.get('level')

        if level == 'section':
            sec_base_query = session.query(BoreholeSection).\
                options(lazyload(BoreholeSection._borehole)).\
                join(Borehole)
            sec_query = DynamicQuery(sec_base_query)

            sec_query.filter_level(query_params, 'borehole')
            sec_query.filter_level(query_params, 'section')
            sec_list = [i._oid for i in sec_query.return_all()]

        query = session.query(Borehole)
        if level == 'section':
            if sec_list:
                logging.info(f"sections with _oid exist that match query "
                             f"params: {sec_list}")
                query = query.options(lazyload(Borehole._sections)).\
                    join(BoreholeSection, isouter=True).\
                    options(contains_eager("_sections"))
                query = query.filter(or_(BoreholeSection._oid.in_(sec_list),
                                         Borehole._sections == None))
            else:
                logging.info(f"sections with _oid do not exist that match "
                             f"query params")
        dynamic_query = DynamicQuery(query)

        # Use borehole level filtering.
        dynamic_query.filter_level(query_params,
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

        if level == 'hydraulic':
            hyd_base_query = session.query(HydraulicSample).\
                options(lazyload(HydraulicSample._section).\
                        lazyload(BoreholeSection._borehole)).\
                join(BoreholeSection).join(Borehole).\
                filter(Borehole.publicid==borehole_id)
            hyd_query = DynamicQuery(hyd_base_query)

            hyd_query.filter_level(query_params,
                                   'hydraulic')
            hyd_list = [i._oid for i in hyd_query.return_all()]


        if level in ['section', 'hydraulic']:
            sec_base_query = session.query(BoreholeSection).\
                options(lazyload(BoreholeSection._borehole)).\
                join(Borehole).\
                filter(Borehole.publicid==borehole_id)
            sec_query = DynamicQuery(sec_base_query)
            sec_query.filter_level(query_params, 'section')
            sec_list = [i._oid for i in sec_query.return_all()]

        query = session.query(Borehole)
        if level == 'section':
            if sec_list:
                logging.info(f"Sections with _oid exist that match query "
                             f"params: {sec_list}")
                query = query.options(lazyload(Borehole._sections)).\
                    join(BoreholeSection, isouter=True).\
                    options(contains_eager("_sections"))
                query = query.filter(BoreholeSection._oid.in_(sec_list))
            else:
                logging.info(f"No sections exist that match query params for borehole")
                

        #TODO(sarsonl): Currently if querying at the hydraulic level, and no hydraulics
        # exist, then no result is output. Not sure why as using left outer joins.
        elif level == 'hydraulic':
            
            if sec_list and hyd_list:
                logging.info(f"sections with _oid exist that match query "
                             f"params: {sec_list}. Hydraulics with _oid "
                             f"exist: {hyd_list}")
                query = query.options(lazyload(Borehole._sections).\
                        lazyload(BoreholeSection._hydraulics)).\
                        join(BoreholeSection).join(HydraulicSample).\
                    options(contains_eager("_sections").\
                            contains_eager("_hydraulics"))
                query = query.filter(or_(HydraulicSample._oid.in_(hyd_list),
                                         BoreholeSection._hydraulics == None))

            elif sec_list and not hyd_list:
                logging.info(f"sections with _oid exist that match query "
                             f"params: {sec_list} but no hydraulics exist")
                query = query.options(lazyload(Borehole._sections)).\
                        join(BoreholeSection).\
                    options(contains_eager("_sections"))
                query = query.filter(BoreholeSection._oid.in_(sec_list))
            else:
                logging.info(f"no sections and no hydraulics exist for "
                             f"borehole that match query params")

        query = query.filter(Borehole.publicid==borehole_id)
        dynamic_query = DynamicQuery(query)

        dynamic_query.format_results(limit=query_params.get('limit'),
                                     offset=query_params.get('offset'))
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
                             f"{borehole_id!r} {section_id!r}")

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

        dynamic_query.filter_level(query_params,
                                   'hydraulic')
        # (sarsonl) Explicit order_by required as not depending on relationships.
        dynamic_query.format_results(order_by=HydraulicSample.datetime_value,
                                     limit=query_params.get('limit'),
                                     offset=query_params.get('offset'))

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
