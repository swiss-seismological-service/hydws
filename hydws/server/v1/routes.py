"""
.. module:: routes
    :synopsis: Contains resources for HYDWS route handling.

.. moduleauthor:: Laura Sarson <laura.sarson@sed.ethz.ch>

"""

import logging
from sqlalchemy import literal, or_
from flask_restful import Api, Resource
from flask import request
from webargs.flaskparser import use_kwargs
from sqlalchemy.orm import contains_eager, lazyload

from hydws import __version__
from hydws.db.orm import Borehole, BoreholeSection, HydraulicSample, User
from hydws.server import db, settings
from hydws.server.errors import FDSNHTTPError
from hydws.server.misc import (with_fdsnws_exception_handling, decode_publicid,
                               make_response)
from hydws.server.v1 import blueprint
from hydws.utils import merge_data
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

    def post(self):
        """
        Template method to be implemented by HYDWS resources in order to serve
        HTTP POST requests.
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


def boreholesection_oids(session, borehole_id=None, **query_params):
    """
    Return a list of BoreholeSection id's that match to the search
    parameters given.

    """
    sec_base_query = session.query(BoreholeSection).\
        options(lazyload(BoreholeSection._borehole)).\
        join(Borehole)
    if borehole_id:
        sec_base_query = sec_base_query.filter(Borehole.publicid==borehole_id)
    sec_query = DynamicQuery(sec_base_query)
    sec_query.filter_level(query_params, 'section')
    sec_list = [i._oid for i in sec_query.return_all()]
    return sec_list

# Note (sarsonl): Seaching for a better way of keeping parent
# boreholes and sections without children hydraulics. This
# is a work-around where seperate calls are done to find if children
# exist before joining the tables.
def hydraulicsample_oids(session, borehole_id, **query_params):
    """
    Return a list of HydraulicSample id's that match to the search
    parameters given.
    """
    hyd_base_query = session.query(HydraulicSample).\
        options(lazyload(HydraulicSample._section).
                lazyload(BoreholeSection._borehole)).\
        join(BoreholeSection).join(Borehole).\
        filter(Borehole.publicid==borehole_id)
    hyd_query = DynamicQuery(hyd_base_query)

    hyd_query.filter_level(query_params,
                           'hydraulic')
    hyd_query.format_results(order_column=HydraulicSample.datetime_value,
                             limit=query_params.get('limit'),
                             offset=query_params.get('offset'))
    hyd_list = [i._oid for i in hyd_query.return_all()]
    return hyd_list

def query_with_sections(query, sec_list,
                        keep_all_boreholes=True,
                        **query_params):
    query = query.options(lazyload(Borehole._sections)).\
        join(BoreholeSection, isouter=True).\
        options(contains_eager("_sections")).\
        order_by(BoreholeSection.topdepth_value)
    if keep_all_boreholes:
        query = query.filter(or_(BoreholeSection._oid.in_(sec_list),
                                 Borehole._sections == None)) # noqa
    else:
        query = query.filter(BoreholeSection._oid.in_(sec_list))
    return query

def query_with_sections_and_hydraulics(query, hyd_list, **query_params):
    query = query.options(
        lazyload(Borehole._sections).
        lazyload(BoreholeSection._hydraulics)).\
        join(BoreholeSection, isouter=True).\
        join(HydraulicSample, isouter=True).\
        options(contains_eager("_sections").contains_eager("_hydraulics")).\
        filter(or_(HydraulicSample._oid.in_(hyd_list),
                   BoreholeSection._hydraulics == None)).\
        order_by(BoreholeSection.topdepth_value, HydraulicSample.datetime_value) # noqa
    return query

def query_hydraulicsamples(session, section_id):
    query = session.query(HydraulicSample).\
        options(lazyload(HydraulicSample._section)).\
        join(BoreholeSection).filter(BoreholeSection.publicid==section_id)

    return query

def section_in_borehole(query, borehole_id, section_id):
    boreholesection_filter = query(Borehole).\
        options(lazyload(Borehole._sections)).\
        filter(Borehole.publicid == borehole_id).\
        filter(BoreholeSection.publicid == section_id)

    section_exists = query(literal(True)).\
        filter(boreholesection_filter.exists()).scalar()

    return section_exists


class NewUserResource(ResourceBase):

    LOGGER = 'hydws.server.v1.newuserresource'

    @with_fdsnws_exception_handling(__version__)
    def post(self):
        user = User(username=request.args.get('username'))
        user.hash_password(request.args.get('password'))
        db.session.add(user)
        db.session.commit()
        return make_response({'username': user.username}, 201)


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

    @with_fdsnws_exception_handling(__version__)
    def post(self):
        try:
            data = request.get_json()
        except KeyError:
            raise IOError("data sent via POST must contain "
                          "the 'data' parameter")
        info = merge_data.merge_boreholes(data, db.session)

        return make_response({"info": info}, settings.MIMETYPE_JSON)

    def _process_request(self, session,
                         **query_params):

        level = query_params.get('level')

        if level == 'section':
            sec_list = boreholesection_oids(session, None, **query_params)

        query = session.query(Borehole)
        if level == 'section':
            print('sec list: ', sec_list)
            if sec_list:
                logging.info(f"sections with _oid exist that match query "
                             f"params: {sec_list}")
                query = query_with_sections(query, sec_list, **query_params)
            else:
                logging.info("sections with _oid do not exist that match "
                             "query params")
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
            hyd_list = hydraulicsample_oids(session, borehole_id,
                                            **query_params)

        if level in ['section', 'hydraulic']:
            sec_list = boreholesection_oids(session, borehole_id,
                                            **query_params)

        query = session.query(Borehole)

        if level == 'section':
            if sec_list:
                logging.info(f"Sections with _oid exist that match query "
                             f"params: {sec_list}")
                query = query_with_sections(
                    query, sec_list, **query_params)
            else:
                logging.info("No sections exist that match query "
                             "params for borehole")

        elif level == 'hydraulic':
            if sec_list and hyd_list:
                logging.info("sections with _oid exist that match query "
                             f"params: {sec_list}. Hydraulics with _oid "
                             f"exist: {hyd_list}")

                query = query_with_sections_and_hydraulics(
                    query, hyd_list, **query_params)
                logging.info(str(query))

            elif sec_list and not hyd_list:
                logging.info(f"sections with _oid exist that match query "
                             f"params: {sec_list} but no hydraulics exist")
                query = query_with_sections(
                    query, sec_list, **query_params)
            else:
                logging.info("no sections and no hydraulics exist for "
                             "borehole that match query params")

        query = query.filter(Borehole.publicid==borehole_id)
        dynamic_query = DynamicQuery(query)

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

    def _process_request(self, session, borehole_id=None, section_id=None,
                         **query_params):
        if not borehole_id or not section_id:
            raise ValueError(f"Invalid borehole or section identifier: "
                             f"{borehole_id!r} {section_id!r}")

        section_exists = section_in_borehole(session.query,
                                             borehole_id, section_id)

        if not section_exists:
            raise ValueError("Borehole Section is not a child of Borehole.")

        query = query_hydraulicsamples(session, section_id)

        dynamic_query = DynamicQuery(query)

        dynamic_query.filter_level(query_params,
                                   'hydraulic')
        # (sarsonl) Explicit order_by required as hydraulic samples
        # returned that don't depend on relationships.
        dynamic_query.format_results(
            order_column=HydraulicSample.datetime_value,
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
api_v1.add_resource(NewUserResource, '{}/users'.format(
    settings.HYDWS_PATH_BASE))
