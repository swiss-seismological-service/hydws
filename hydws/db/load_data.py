"""
Provide facilities for importing json data.
"""
import sys
import traceback
import argparse
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from hydws import __version__
from hydws.db.base import ORMBase
from hydws.utils import url
from hydws.utils.app import CustomParser, App, AppError
from hydws.utils.error import Error, ExitCodes
from hydws.server import settings
# TODO (sarsonl) make version loading dynamic
from hydws.server.v1.ostream.schema import (BoreholeSchema,
                                            BoreholeAssignPublicIdSchema)


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
        parser.add_argument('--version', '-V', action='version',
                            version='%(prog)s version ' + __version__)
        parser.add_argument('--assignids', action="store_true")
        parser.add_argument('--borehole_namespace', type=str,
                                     help="If --assignids, prepend this namespace to the borehole publicid")
        parser.add_argument('--section_namespace', type=str,
                                     help="If --assignids, prepend this namespace to the section publicid")
        parser.add_argument('--overwrite_publicids', action="store_true",
                                     help="Overwrite pubic id's that exist in the input data"
                                        " with new generated public ids")
        # required arguments
        parser.add_argument('db_url', type=url, metavar='URL',
                            help=('DB URL indicating the database dialect and '
                                  'connection arguments. For SQlite only a '
                                  'absolute file path is supported.'))
        parser.add_argument('data_file', nargs="?", type=argparse.FileType("r"),
                            help=('Path to json data that will be added to db'))


        return parser

    def load_json_into_db(self, opened_file, schema, schema_args):
        """
        Loads a json file and deserializes it based on BoreholeSchema.

        :param opened_file: file object containing JSON data
        :param schema: Schema class to deserialize data
        :param schema_args: dict of args to pass to schema instance


        :rtype: List or single instance of orm.Borehole
        """
        data = json.load(opened_file)
        
        many = False
        if isinstance(data, list):
            many = True
        schema_args['many'] = many
        loaded_data = schema(**schema_args).load(data)
        return loaded_data, many

    def validate_args(self):
        if not self.args.assignids and (
                self.args.borehole_namespace is not None or
                self.args.section_namespace is not None or  
                self.args.overwrite_publicids):
            raise ValueError("--borehole_namespace and --section_namespace "
                             "and --overwrite_publicids only allowed if "
                             "--assignids is used.")

    def run(self):
        """
        Run application.
        """
        exit_code = ExitCodes.EXIT_SUCCESS
        try:
            self.validate_args()
            self.logger.info('{}: Version v{}'.format(self.PROG, __version__))
            self.logger.debug('Configuration: {!r}'.format(self.args))

            schema = BoreholeSchema
            schema_args = {}
            if self.args.assignids:
                schema_args = {
                    'borehole_namespace': self.args.borehole_namespace,
                    'section_namespace': self.args.section_namespace,
                    'overwrite': self.args.overwrite_publicids}
                schema = BoreholeAssignPublicIdSchema

            deserialized_data, many_boreholes = self.load_json_into_db(
                    self.args.data_file, schema, schema_args)

            if self.args.data_file:
                engine = create_engine(self.args.db_url)

                self.logger.debug('Adding data to db...')
                Session = sessionmaker(bind=engine)
                session = Session()

                if many_boreholes:
                    session.add(*deserialized_data)
                else:
                    session.add(deserialized_data)

                self.logger.info(
                    "Data successfully imported to db.")

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
