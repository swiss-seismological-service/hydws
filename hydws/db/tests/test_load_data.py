# Copyright (C) 2019, ETH Zurich - Swiss Seismological Service SED
"""
Well related test facilities.
"""
import os
import unittest
import subprocess
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from hydws.db import orm

current_dir = os.path.abspath(__file__)
db_filename = os.path.join(current_dir, "data/test_loading.db")
db_sqlite_string = f"sqlite:///{db_filename}"

class LoadBoreholeTestCase(unittest.TestCase):
    """
    Test cases for :py:class:`ramsis.datamodel.well.Borehole`.
    """
    db = None


    def test_load_merge_identical_file(self):

        subprocess.run(['hydws-db-init', '-o', db_sqlite_string, '| > log_file.txt'])
        engine = create_engine(db_sqlite_string, echo="debug")
        Session = sessionmaker(bind=engine)

        subprocess.run(['hydws-data-import', db_sqlite_string])
        session = Session()
        bh0 = session.query(orm.Borehole).one_or_none()
        session.close()
        subprocess.run(['hydws-data-import', '--merge_only', db_sqlite_string])
        engine = create_engine(db_sqlite_string, echo="debug")

        session = Session()
        bh1 = session.query(orm.Borehole).one_or_none()
        session.close()

        self.assertEqual(bh0, bh1)

def suite():
    suite = unittest.makeSuite(LoadBoreholeTestCase, 'test')
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
