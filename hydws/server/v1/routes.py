"""
HYDWS resources.
"""

import logging

from flask_restful import Api, Resource
from webargs.flaskparser import use_kwargs

from hydws.server import db
from hydws.server.v1 import blueprint
from hydws.server.v1.parser import BoreholeHydraulicDataListResourceSchema


api_v1 = Api(blueprint)


class ResourceBase(Resource):

    LOGGER = 'hydws.server.v1.resource'

    def __init__(self, logger=None):
        super().__init__()
        self.logger = logging.getLogger(logger if logger else self.LOGGER)

    def get(self, **kwargs):
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

    @use_kwargs(BoreholeHydraulicDataListResourceSchema(),
                locations=("query", ))
    def get(self, borehole_id, **kwargs):
        pass


class SectionHydraulicDataListResource(ResourceBase):

    def get(self, borehole_id, section_id):
        pass


# TODO(damb):
# Add resources to API
