"""
Provide facilities for importing json data.
"""
import sys
import traceback
import argparse
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from hydws import __version__
from hydws.utils import url
from hydws.utils.app import CustomParser, App, AppError
from hydws.utils.error import Error, ExitCodes
from hydws.utils.merge_data import merge_boreholes
from hydws.server import settings

class HYDWSLoadDataApp(App):
    """
    Implementation of an utility application to automate the HYDWS DB
    data import process.
    """
    PROG = 'hydws-data-import'

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
            description='Add data to an initialized HYDWS database.',
            parents=parents)

        # optional arguments
        parser.add_argument("--version", "-V", action="version",
                            version="%(prog)s version " + __version__)
        parser.add_argument("--merge_only", action="store_true",
                            help="Only allow data to be merged with existing "
                            "borehole. Error if publicid cannot be found")
        parser.add_argument("--assignids", action="store_true",
                            help="Generate public ids for boreholes and "
                            "borehole sections")
        parser.add_argument("--publicid_uri", type=str,
                            help="If --assignids, prepend this URI to "
                            "the generated borehole and borehole section "
                            "public ids. E.g. 'smi:ch.ethz.sed/'")
        parser.add_argument("--overwrite_publicids", action="store_true",
                            help="Overwrite pubic id's that exist in the "
                                 "input data  with new generated public ids")
        # required arguments
        parser.add_argument("db_url", type=url, metavar="URL",
                            help=("DB URL indicating the database dialect "
                                  "and connection arguments. For SQlite "
                                  "only a absolute file path is supported."))
        parser.add_argument("data_file", nargs="?",
                            type=argparse.FileType("r"),
                            help=("Path to json data that will be added to "
                                  "the db"))
        return parser

    def validate_args(self):
        if not self.args.assignids and (
                self.args.publicid_uri is not None or
                self.args.overwrite_publicids):
            raise ValueError("--publicid_uri and --overwrite_publicids "
                             "only allowed if --assignids is used.")
        if self.args.merge_only and (
                self.args.assignids or self.args.publicid_uri is not None or
                self.args.overwrite_publicids):
            raise ValueError("--assignids, --publicid_uri and "
                             "--overwrite_publicids only allowed if "
                             "--merge_only is not used.")

    def run(self):
        """
        Run application.
        """
        exit_code = ExitCodes.EXIT_SUCCESS
        try:
            self.validate_args()
            self.logger.info('{}: Version v{}'.format(self.PROG, __version__))
            if self.args.data_file:
                engine = create_engine(self.args.db_url)

            Session = sessionmaker(bind=engine)
            session = Session()
            self.logger.debug('Configuration: {!r}'.format(self.args))
            _ = merge_boreholes(
                self.args.data_file, session,
                assignids=self.args.assignids,
                publicid_uri=self.args.publicid_uri,
                overwrite_publicids=self.args.overwrite_publicids,
                merge_only=self.args.merge_only)

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
def load_data():
    """
    Main function for HYDWS DB data importer
    """

    app = HYDWSLoadDataApp(log_id='HYDWS_data_import')

    try:
        app.configure(settings.PATH_HYDWS_CONF,
                      positional_required_args=['data_file', 'db_url'])
    except AppError as err:
        # handle errors during the application configuration
        print('ERROR: Application configuration failed "%s".' % err,
              file=sys.stderr)
        sys.exit(ExitCodes.EXIT_ERROR)

    app.run()


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    load_data()
