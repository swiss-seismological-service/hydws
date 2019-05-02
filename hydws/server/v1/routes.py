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
        raise NotImplementedError

    def _handle_nodata(self, kwargs):
        raise FDSNHTTPError.create(
            int(kwargs.get(
                'nodata',
                settings.FDSN_DEFAULT_NO_CONTENT_ERROR_CODE)))

    def _process_request(self, borehole_id=None, section_id=None,
                         **query_params):
        raise NotImplementedError


class BoreholeListResource(ResourceBase):

    def get(self):
        pass


class BoreholeResource(ResourceBase):

    def get(self, borehole_id):
        pass


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
        try:
            resp = BoreholeSchema().dumps(resp)
        except Exception:
            raise FDSNHTTPError.create(500, service_version=__version__)

        return make_response(resp, settings.MIMETYPE_JSON)

    def _process_request(self, session, borehole_id=None, section_id=None,
                         **query_params):

        if not borehole_id:
            raise ValueError(f"Invalid borehole identifier: {borehole_id!r}")

        # TODO(damb): Add additional filter criteria
        try:
            bh = session.query(orm.Borehole).\
                join(orm.BoreholeSection).\
                filter(orm.Borehole.m_publicid==borehole_id).\
                one()
        except NoResultFound:
            return None

        # TODO TODO TODO
        # A borehole at least must have a single borehole-section

        return bh


class SectionHydraulicDataListResource(ResourceBase):

    def get(self, borehole_id, section_id):
        pass


# TODO(damb):
# Add resources to API

api_v1.add_resource(BoreholeHydraulicDataListResource,
                    '{}/<borehole_id>'.format(settings.HYDWS_PATH_BOREHOLES))
