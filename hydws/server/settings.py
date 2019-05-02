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

FDSN_DEFAULT_NO_CONTENT_ERROR_CODE = 204
FDSN_NO_CONTENT_CODES = (FDSN_DEFAULT_NO_CONTENT_ERROR_CODE, 404)
HYDWS_SERVICE_DOCUMENTATION_URI = 'http://URL/to/hydws/docs/'

MIMETYPE_JSON = 'application/json'
MIMETYPE_TEXT = 'text/plain'
ERROR_MIMETYPE = MIMETYPE_TEXT

CHARSET_TEXT = 'charset=utf-8'
