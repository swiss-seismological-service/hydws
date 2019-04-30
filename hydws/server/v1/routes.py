"""
HYDWS resources.
"""

import logging

from flask_restful import Api, Resource
from webargs.flaskparser import use_kwargs

from hydws import __version__
from hydws.server import db, settings
from hydws.server.misc import with_fdsnws_exception_handling, decode_publicid
from hydws.server.v1 import blueprint
from hydws.server.v1.parser import BoreholeHydraulicDataListResourceSchema


api_v1 = Api(blueprint)


class ResourceBase(Resource):

    LOGGER = 'hydws.server.v1.resource'

    def __init__(self, logger=None):
        super().__init__()
        self.logger = logging.getLogger(logger if logger else self.LOGGER)

    def get(self, *args, **kwargs):
        raise NotImplementedError


class BoreholeListResource(ResourceBase):

    def get(self):
        pass


class BoreholeResource(ResourceBase):

    def get(self, borehole_id):
        pass


class BoreholeSectionListResource(ResourceBase):

    def get(self, borehole_id):
        pass


class BoreholeSectionResource(ResourceBase):

    def get(self, borehole_id, section_id):
        pass


class BoreholeHydraulicDataListResource(ResourceBase):

    LOGGER = 'hydws.server.v1.boreholehydraulicdatalistresource'

    @with_fdsnws_exception_handling(__version__)
    @use_kwargs(BoreholeHydraulicDataListResourceSchema(),
                locations=("query", ))
    def get(self, borehole_id, **kwargs):
        borehole_id = decode_publicid(borehole_id)

        self.logger.debug(
            f"Received request: borehole_id={borehole_id}, kwargs={kwargs}")

        # TODO TODO TODO

        return {"bh": borehole_id}


class SectionHydraulicDataListResource(ResourceBase):

    def get(self, borehole_id, section_id):
        pass


# TODO(damb):
# Add resources to API

api_v1.add_resource(BoreholeHydraulicDataListResource,
                    '{}/<borehole_id>'.format(settings.HYDWS_PATH_BOREHOLES))
