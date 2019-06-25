"""
Functions which might be used as *executables*:
    - :code:`emerge()` -- initialize (and create) a HYDWS DB
"""

import logging  # noqa
import os
import sys
import traceback

from sqlalchemy import create_engine

from hydws import __version__
from hydws.db.base import ORMBase
from hydws.db import orm  # noqa
from hydws.utils import url
from hydws.utils.app import CustomParser, App, AppError
from hydws.utils.error import Error, ExitCodes


class HYDWSDBInitApp(App):
    """
    Implementation of an utility application to automate the HYDWS DB
    initialization process.
    """
    PROG = 'hydws-db-init'

    class DBAlreadyAvailable(Error):
        """The SQLite database file '{}' is already available."""

    def build_parser(self, parents=[]):
        """
        Configure a parser.

        :param list parents: list of parent parsers
        :returns: parser
        :rtype: :py:class:`argparse.ArgumentParser`
        """
        parser = CustomParser(
            prog=self.PROG,
            description='Initialize (and create) a DB for HYDWS.',
            parents=parents)

        # optional arguments
        parser.add_argument('--version', '-V', action='version',
                            version='%(prog)s version ' + __version__)
        parser.add_argument('--sql', action='store_true', default=False,
                            help=('render the SQL; dump the metadata creation '
                                  'sequence to stdout'))
        parser.add_argument('-o', '--overwrite', action='store_true',
                            default=False,
                            help=('overwrite if already existent '
                                  '(SQLite only)'))

        # positional arguments
        parser.add_argument('db_url', type=url, metavar='URL',
                            help=('DB URL indicating the database dialect and '
                                  'connection arguments. For SQlite only a '
                                  'absolute file path is supported.'))

        return parser

    def run(self):
        """
        Run application.
        """
        # configure SQLAlchemy logging
        # log_level = self.logger.getEffectiveLevel()
        # logging.getLogger('sqlalchemy.engine').setLevel(log_level)
        exit_code = ExitCodes.EXIT_SUCCESS
        try:
            self.logger.info('{}: Version v{}'.format(self.PROG, __version__))
            self.logger.debug('Configuration: {!r}'.format(self.args))

            if self.args.db_url.startswith('sqlite'):
                p = self.args.db_url[10:]

                if not self.args.overwrite and os.path.isfile(p):
                    raise self.DBAlreadyAvailable(p)

                if os.path.isfile(p):
                    os.remove(p)

            if self.args.sql:
                # dump sql only
                def dump(sql, *multiparams, **params):
                    print(sql.compile(dialect=engine.dialect))

                idx = self.args.db_url.find(':')

                engine = create_engine(self.args.db_url[0:idx] + '://',
                                       strategy='mock', executor=dump)
                ORMBase.metadata.create_all(engine, checkfirst=False)
            else:
                # create db tables
                engine = create_engine(self.args.db_url)

                self.logger.debug('Creating database tables ...')
                ORMBase.metadata.create_all(engine)

                self.logger.info(
                    "DB '{}' successfully initialized.".format(
                        self.args.db_url))

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


# ----------------------------------------------------------------------------
def emerge():
    """
    Main function for HYDWS DB initializer
    """

    app = HYDWSDBInitApp(log_id='HYDWS')

    try:
        app.configure(None,
                      positional_required_args=['db_url'])
    except AppError as err:
        # handle errors during the application configuration
        print('ERROR: Application configuration failed "%s".' % err,
              file=sys.stderr)
        sys.exit(ExitCodes.EXIT_ERROR)

    app.run()


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    emerge()
