"""Create and populate db with possible cases for combinations of boreholes,
sections and hydraulics samples. It's purpose is to test correctly
returned messages on request when this db is used in a session.

Example Usage:
    python populate_db_test_cases --db_url sqlite:///test.db

for creatiion of a db in the directory where the code is being run.

"""

import datetime
import argparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from hydws.db import orm


bh1 = orm.Borehole(
    publicid='smi:ch.ethz.sed/bh/11111111-e4a0-4692-bf29-33b5591eb2d43',
    depth_value=1000,
    latitude_value=10.66320713,
    latitude_uncertainty=0.5368853227,
    longitude_value=10.66320713,
    longitude_uncertainty=0.7947170871,
    bedrockdepth_value=0,
    literaturesource_author='Charles Dickens',
    literaturesource_creator_mbox_resourceid='123456'

)



def add_orm_values(db_url):




    try:
        engine = create_engine(db_url, echo="debug")

        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(bh1)
        session.commit()
        session.close()

    except Exception as err:
        print(err)


def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--db_url", type=str, required=True,
        help="e.g. sqlite:///test.db  to create test.db in current"
             " directory.")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parseargs()
    add_orm_values(args.db_url)
