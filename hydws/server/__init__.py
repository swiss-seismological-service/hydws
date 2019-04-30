"""
Server related general purpose utilities.
"""
import datetime

from flask import Flask, make_response, g
from flask_sqlalchemy import SQLAlchemy
from webargs.flaskparser import parser

from hydws import __version__
from hydws.server import settings, errors


db = SQLAlchemy()


def create_app(config_dict={}):
    """
    Factory function for Flask application.

    :param :cls:`flask.Config config` flask configuration object
    """
    app = Flask(__name__)
    app.config.update(config_dict)

    db.init_app(app)

    # XXX(damb): Avoid circular imports.
    from hydws.server.v1 import blueprint as api_v1_bp, API_VERSION_V1
    app.register_blueprint(
        api_v1_bp,
        url_prefix='/v{version}'.format(version=API_VERSION_V1))

    @app.before_request
    def before_request():
        g.request_starttime = datetime.datetime.utcnow()

    def register_error(err):
        @app.errorhandler(err)
        def handle_error(error):
            return make_response(
                error.description, error.code,
                {'Content-Type': '{}; {}'.format(settings.ERROR_MIMETYPE,
                                                 settings.CHARSET_TEXT)})

    errors_to_register = (
        errors.NoDataError,
        errors.BadRequestError,
        errors.RequestTooLargeError,
        errors.RequestURITooLargeError,
        errors.InternalServerError,
        errors.TemporarilyUnavailableError)

    for err in errors_to_register:
        register_error(err)

    # register parser error handler
    @parser.error_handler
    def handle_error(error, req, schema, status_code, headers):
        raise errors.FDSNHTTPError.create(
            400, service_version=__version__,
            error_desc_long=error.messages)

    return app
