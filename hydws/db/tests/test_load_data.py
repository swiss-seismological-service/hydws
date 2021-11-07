# Copyright (C) 2019, ETH Zurich - Swiss Seismological Service SED
"""
Well related test facilities.

To debug, please run the command (editing the paths as required):
hydws-data-import --logging-conf path_to_config/config/logging.conf sqlite:////absolute path/tests/data/test_loading.db /absolute_path/tests/data/borehole_file_updated.json # noqa
"""
import os
import datetime
import unittest
import subprocess
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, contains_eager

from hydws.db import orm

current_dir = os.path.dirname(os.path.abspath(__file__))
db_filename = os.path.join(current_dir, "data/test_loading.db")
db_sqlite_string = f"sqlite:///{db_filename}"
json_file_path = os.path.join(current_dir, 'data/borehole_file.json')
json2_file_path = os.path.join(current_dir, 'data/borehole_file_updated.json')
json_no_meta_file_path = os.path.join(
    current_dir, 'data/borehole_file_no_section_metadata.json')

class LoadBoreholeTestCase(unittest.TestCase):
    """
    Test cases for :py:class:`ramsis.datamodel.well.Borehole`.
    """
    def test_load_merge_identical_file(self):

        os.remove(db_filename)
        subprocess.run(
            ['hydws-db-init', '-o', db_sqlite_string],
            stdout=subprocess.PIPE)
        engine = create_engine(db_sqlite_string)
        Session = sessionmaker(bind=engine)

        subprocess.run(
            ['hydws-data-import',
             db_sqlite_string, json_file_path])
        session = Session()
        bh0 = session.query(orm.Borehole).\
            options(contains_eager("_sections").
                    contains_eager("_hydraulics")).one_or_none()
        session.close()
        subprocess.run(
            ['hydws-data-import', '--merge_only',
             db_sqlite_string, json_file_path])
        engine = create_engine(db_sqlite_string)

        session = Session()
        bh1 = session.query(orm.Borehole).\
            options(contains_eager("_sections").
                    contains_eager("_hydraulics")).one_or_none()
        session.close()

        self.assertEqual(len(bh0._sections[0]._hydraulics),
                         len(bh1._sections[0]._hydraulics))
        self.assertEqual(bh0._sections[0]._hydraulics[0].datetime_value,
                         bh1._sections[0]._hydraulics[0].datetime_value)
        self.assertEqual(bh0._sections[0]._hydraulics[-1].datetime_value,
                         bh1._sections[0]._hydraulics[-1].datetime_value)

    def test_load_updated_file(self):

        os.remove(db_filename)
        subprocess.run(
            ['hydws-db-init', '-o',
             db_sqlite_string],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        engine = create_engine(db_sqlite_string)
        Session = sessionmaker(bind=engine)

        subprocess.run(
            ['hydws-data-import',
             db_sqlite_string, json_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        session = Session()
        bh0 = session.query(orm.Borehole).\
            options(contains_eager("_sections").
                    contains_eager("_hydraulics")).one_or_none()
        session.close()
        subprocess.run(
            ['hydws-data-import', '--merge_only',
             db_sqlite_string, json2_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        engine = create_engine(db_sqlite_string)

        session = Session()
        bh1 = session.query(orm.Borehole).\
            options(contains_eager("_sections").
                    contains_eager("_hydraulics")).one_or_none()
        session.close()

        self.assertEqual(len(bh1._sections[0]._hydraulics), 4)
        self.assertEqual(bh0._sections[0]._hydraulics[0].datetime_value,
                         bh1._sections[0]._hydraulics[0].datetime_value)
        self.assertEqual(bh1._sections[0]._hydraulics[-1].datetime_value,
                         datetime.datetime(2006, 12, 12, 1, 0))

    def test_load_no_section_metadata(self):
        os.remove(db_filename)
        subprocess.run(
            ['hydws-db-init', '-o',
             db_sqlite_string],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        engine = create_engine(db_sqlite_string)
        Session = sessionmaker(bind=engine)

        subprocess.run(
            ['hydws-data-import',
             db_sqlite_string, json_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        session = Session()
        bh0 = session.query(orm.Borehole).\
            options(contains_eager("_sections").
                    contains_eager("_hydraulics")).one_or_none()
        session.close()
        subprocess.run(
            ['hydws-data-import', '--merge_only',
             db_sqlite_string, json_no_meta_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        engine = create_engine(db_sqlite_string)

        session = Session()
        bh1 = session.query(orm.Borehole).\
            options(contains_eager("_sections").
                    contains_eager("_hydraulics")).one_or_none()
        session.close()

        # Check that values are unchanged
        self.assertEqual(len(bh0._sections[0]._hydraulics),
                         len(bh1._sections[0]._hydraulics))
        # Check that the metadata is unchanged
        self.assertEqual(bh0._sections[0].toplatitude_value,
                         bh1._sections[0].toplatitude_value)
        self.assertEqual(bh0._sections[0].starttime,
                         bh1._sections[0].starttime)

def suite():
    suite = unittest.makeSuite(LoadBoreholeTestCase, 'test')
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
