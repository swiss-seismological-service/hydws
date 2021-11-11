# Copyright (C) 2019, ETH Zurich - Swiss Seismological Service SED
"""
Json import testing facilities.
"""
from os import path
import unittest
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from hydws.db import load_data
from hydws.db.orm import Borehole, BoreholeSection
import argparse
from sqlalchemy.orm import lazyload

dirpath = path.dirname(path.abspath(__file__))

json_data = path.join(dirpath, "test_json.json")
opened_data = open(json_data, 'r')


class DataImportTestCase(unittest.TestCase):
    """Test get methods in routes."""

    def setUp(self):
        engine = create_engine("sqlite:///{}/initialized.db".format(dirpath))
        Session = sessionmaker(bind=engine)
        session = Session()
        q = engine.table_names()
        for table in q:
            session.execute(f'delete from {table}')
        session.commit()
        session.close()

    @patch('hydws.db.load_data.argparse.ArgumentParser.parse_args',
           return_value=argparse.Namespace(
               db_url="sqlite:///{}/initialized.db".format(dirpath),
               assignids=True, overwrite_publicids=False,
               publicid_uri="eth_uri/", merge_only=False,
               data_file=opened_data, path_logging_conf=None, version=None, auto_datetime_off=False))
    @patch('hydws.db.load_data.sys.exit')
    def test_data_import(self, sys_exit, parse_args):
        load_data.load_data()
        engine = create_engine("sqlite:///{}/initialized.db".format(dirpath))
        Session = sessionmaker(bind=engine)
        session = Session()

        data = session.query(Borehole).\
            options(lazyload(Borehole._sections).
                    lazyload(BoreholeSection._hydraulics)).one()

        startswith_bh_namespace = data.publicid.startswith(
            "eth_uri/borehole/")
        self.assertTrue(startswith_bh_namespace)

        startswith_sec_namespace = data._sections[0].publicid.\
            startswith("eth_uri/borehole/section/")
        self.assertTrue(startswith_sec_namespace)

        session.close()
