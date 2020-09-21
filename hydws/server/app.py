"""
Launch HYDWS.
"""
import os
import sys
import traceback

from hydws import __version__
from hydws.server import settings, create_app
from hydws.utils import url
from hydws.utils.app import CustomParser, App, AppError
from hydws.utils.error import Error, ExitCodes


class HydraulicWebserviceBase(App):
    """
    Base production implementation of HYDWS.
    """
    PROG = 'hydws'

    def build_parser(self, parents=[]):
        """
        Set up the commandline argument parser.

        :param list parents: list of parent parsers
        :returns: parser
        :rtype: :py:class:`argparse.ArgumentParser`
        """

        parser = CustomParser(
            prog=self.PROG,
            description='Launch HYDWS.',
            parents=parents)

        parser.add_argument('--version', '-V', action='version',
                            version='%(prog)s version ' + __version__)

        # positional arguments
        parser.add_argument('db_url', type=url, metavar='URL',
                            help=('DB URL indicating the database dialect and '
                                  'connection arguments. For SQlite only a '
                                  'absolute file path is supported.'))

        return parser

    # build_parser ()

    def run(self):
        """
        Run application.
        """
        # configure SQLAlchemy logging
        # log_level = self.logger.getEffectiveLevel()
        # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

        exit_code = ExitCodes.EXIT_SUCCESS
        try:
            self.logger.info('{}: Version v{}'.format(self.PROG, __version__))
            self.logger.debug('Configuration: {!r}'.format(self.args))

            app = self.setup_app()

            try:
                from mod_wsgi import version  # noqa
                self.logger.info('Serving with mod_wsgi.')
            except Exception:
                pass

            return app

        except Error as err:
            self.logger.error(err)
            exit_code = ExitCodes.EXIT_ERROR
        except Exception as err:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.logger.critical('Local Exception: %s' % err)
            self.logger.critical(
                'Traceback information: ' + repr(traceback.format_exception(
                    exc_type, exc_value, exc_traceback)))
            exit_code = ExitCodes.EXIT_ERROR

        sys.exit(exit_code)

    def setup_app(self):
        """
        Build the Flask app.

        :rtype :py:class:`flask.Flask`
        """
        app_config = dict(
            # TODO(damb): Pass log_level to app.config!
            PROPAGATE_EXCEPTIONS=True,
            SQLALCHEMY_DATABASE_URI=self.args.db_url,
            SQLALCHEMY_TRACK_MODIFICATIONS=False)

        return create_app(config_dict=app_config)


class HydraulicWebserviceTest(HydraulicWebserviceBase):
    """
    Test implementation of HYDWS.
    """
    PROG = 'hydws-test'

    def build_parser(self, parents=[]):
        """
        Set up the commandline argument parser.

        :param list parents: list of parent parsers
        :returns: parser
        :rtype: :py:class:`argparse.ArgumentParser`
        """
        parser = super().build_parser(parents)
        parser.add_argument('-p', '--port', metavar='PORT', type=int,
                            default=settings.HYDWS_DEFAULT_SERVER_PORT,
                            help='server port')

        return parser

    # build_parser ()

    def run(self):
        """
        Run application.
        """
        exit_code = ExitCodes.EXIT_SUCCESS
        try:
            self.logger.info('{}: Version v{}'.format(self.PROG, __version__))
            self.logger.debug('Configuration: {!r}'.format(self.args))

            app = self.setup_app()

            # run local Flask WSGI server (not for production)
            self.logger.info('Serving with local WSGI server.')
            self.logger.debug('Registered rules: {}'.format(app.url_map))

            app.run(threaded=True, port=self.args.port,
                    host="0.0.0.0",
                    debug=(os.environ.get('DEBUG') == 'True'),
                    use_reloader=True, passthrough_errors=True)

        except Error as err:
            self.logger.error(err)
            exit_code = ExitCodes.EXIT_ERROR
        except Exception as err:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.logger.critical('Local Exception: %s' % err)
            self.logger.critical(
                'Traceback information: ' + repr(traceback.format_exception(
                    exc_type, exc_value, exc_traceback)))
            exit_code = ExitCodes.EXIT_ERROR

        sys.exit(exit_code)


HydraulicWebservice = HydraulicWebserviceBase


# -----------------------------------------------------------------------------
def _main(app):
    """
    Main function executor for HYDWS
    """
    try:
        app.configure(
            settings.PATH_HYDWS_CONF,
            positional_required_args=['db_url'],
            config_section=settings.HYDWS_CONFIG_SECTION)
    except AppError as err:
        # handle errors during the application configuration
        print('ERROR: Application configuration failed "%s".' % err,
              file=sys.stderr)
        sys.exit(ExitCodes.EXIT_ERROR)

    return app.run()


def main_test():
    return _main(HydraulicWebserviceTest(log_id='HYDWS'))


def main_prod():
    return _main(HydraulicWebservice(log_id='HYDWS'))


main = main_prod


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main_test()
