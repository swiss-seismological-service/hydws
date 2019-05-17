"""
HYDWS settings and configuration constants.
"""
from hydws import settings as global_settings

PATH_HYDWS_CONF = '/var/www/hydws/config/hydws_config'
HYDWS_CONFIG_SECTION = global_settings.HYDWS_CONFIG_SECTION

HYDWS_DEFAULT_SERVER_PORT = 5000

# ----------------------------------------------------------------------------
# service specific configuration parameters
HYDWS_PATH_BOREHOLES = '/boreholes'
HYDWS_PATH_SECTIONS = '/sections'
HYDWS_PATH_HYDRAULICS='/hydraulics'
FDSN_DEFAULT_NO_CONTENT_ERROR_CODE = 204
FDSN_NO_CONTENT_CODES = (FDSN_DEFAULT_NO_CONTENT_ERROR_CODE, 404)
HYDWS_SERVICE_DOCUMENTATION_URI = 'http://URL/to/hydws/docs/'

HYDWS_DEFAULT_OFORMAT = 'json'
HYDWS_OFORMATS = (HYDWS_DEFAULT_OFORMAT, 'xml')

HYDWS_DEFAULT_LEVEL = 'section'
HYDWS_SECTION_LEVELS = (HYDWS_DEFAULT_LEVEL, 'borehole')
HYDWS_HYDRAULIC_LEVELS = (HYDWS_DEFAULT_LEVEL, 'borehole', 'hydraulic')
MIMETYPE_JSON = 'application/json'
MIMETYPE_TEXT = 'text/plain'
ERROR_MIMETYPE = MIMETYPE_TEXT

CHARSET_TEXT = 'charset=utf-8'
