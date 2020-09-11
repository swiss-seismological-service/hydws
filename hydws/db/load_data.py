"""
Provide facilities for importing json data.
"""
import sys
import traceback
import argparse
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, contains_eager

from hydws import __version__
from hydws.utils import url
from hydws.utils.app import CustomParser, App, AppError
from hydws.utils.error import Error, ExitCodes
from hydws.server import settings
# TODO (sarsonl) make version loading dynamic
from hydws.server.v1.ostream.schema import BoreholeSchema
from hydws.db.orm import Borehole, BoreholeSection, HydraulicSample

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

    def load_json(self, opened_file, context, schema_class=BoreholeSchema):
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

        schema = schema_class(many=many)
        schema.context = context
        loaded_data = schema.load(data)
        return loaded_data, many

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
            self.logger.debug('Configuration: {!r}'.format(self.args))

            context = {}
            if self.args.assignids:
                context = {
                    'publicid_uri': self.args.publicid_uri,
                    'overwrite': self.args.overwrite_publicids}

            deserialized_data, many_boreholes = self.load_json(
                self.args.data_file, context)

            if self.args.data_file:
                engine = create_engine(self.args.db_url)

                self.logger.debug('Adding data to db...')
                Session = sessionmaker(bind=engine)
                session = Session()

                if not many_boreholes:
                    deserialized_data = [deserialized_data]

                for bh in deserialized_data:
                    bh_existing = session.query(Borehole).\
                        options(contains_eager("_sections").
                                contains_eager("_hydraulics")).\
                        filter(
                        Borehole.publicid == bh.publicid).one_or_none()
                    if bh_existing:
                        self.logger.info("A borehole exists with the same "
                                         "publicid. Merging with existing "
                                         "borehole.")
                        for section in bh._sections:
                            section_existing = session.query(BoreholeSection).\
                                options(contains_eager("_hydraulics")).\
                                filter(
                                    BoreholeSection.publicid == section.publicid).one_or_none()
                            if section_existing:
                                # Get time range of imported dataset
                                first_sample = min(h.datetime_value for h in section._hydraulics)
                                last_sample = max(h.datetime_value for h in section._hydraulics)
                                print("first and last sample times", first_sample, last_sample)
                                print("section existing with x hydraulic sample:", len(section_existing._hydraulics))
                                print("wanting to add from section with x hydrauli samples", len(section._hydraulics))
                                session.query(HydraulicSample).filter(HydraulicSample.datetime_value>= first_sample).\
                                        filter(HydraulicSample.datetime_value <= last_sample).\
                                        filter(HydraulicSample.boreholesection_oid == section_existing._oid).\
                                        delete(synchronize_session=False)
                                print("borehole section in session:", section in session)
                                print("session commit, number f hydraulics after delete", len(section_existing._hydraulics))
                                print("number of borehole sections: ", [(b._oid, b.m_publicid) for b in session.query(BoreholeSection).all()])
                                print("append new hydraulics")
                                for sample in section._hydraulics:
                                    sample._section = section_existing
                                section_existing._hydraulics.extend(section._hydraulics)
                                print("after extend number f hydraulics after delete", len(section_existing._hydraulics))
                                session.expunge(section)
                                session.expunge(bh)
                                print("after expunge borehole section in session:", section in session)
                                print("next session.commit")
                                session.commit()
                                print("number of hydraulics now in db section: ", len(section_existing._hydraulics))
                            else:
                                session.add(section)
                        #bh_existing.merge(bh)
                    else:
                        if self.args.merge_only:
                            raise ValueError(
                                "No borehole exists with publicid: "
                                f"{bh.publicid} and cannot be merged.")
                        session.add(bh)
                try:
                    session.commit()
                    self.logger.info(
                        "Data successfully imported to db.")
                except Exception:
                    session.rollback()
                    raise
                finally:
                    session.close()

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
