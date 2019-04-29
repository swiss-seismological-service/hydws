"""
Server related general purpose utilities.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


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

    return app
