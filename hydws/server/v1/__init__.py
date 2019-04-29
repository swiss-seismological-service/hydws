"""
HYDWS blueprint v1.
"""

from flask import Blueprint

API_VERSION_V1 = 1
API_VERSION = API_VERSION_V1

blueprint = Blueprint('v1', __name__)

# XXX(damb): Register modules with blueprint.
from hydws.server.v1 import routes, schema  # noqa
