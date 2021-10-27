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

from hydws.db import orm, base


res0 = base.ResourceIdentifier(resourceid='2143214214',)
creator0 = base.Author(_mbox=res0,)
ls0 = base.LiteratureSource(author='Charles Dickens', _creator=creator0,)


bh0 = orm.Borehole(
    publicid='smi:ch.ethz.sed/bh/11111111-e4a0-4692-bf29-33b5591eb2d43',
    name="Borehole1",
    description="description of borehole",
    latitude_value=10.66320713,
    latitude_uncertainty=0.5368853227,
    longitude_value=10.66320713,
    longitude_uncertainty=0.7947170871,
    altitude_value=30.0,
    bedrockaltitude_value=0,
    measureddepth_value=1100,
    _literaturesource=ls0,
)


bh1 = orm.Borehole(
    publicid='smi:ch.ethz.sed/bh/11111111-e4a0-4692-bf29-33b5591eb798',
    latitude_value=10.66320713,
    latitude_uncertainty=0.5368853227,
    longitude_value=10.66320713,
    longitude_uncertainty=0.7947170871,
    altitude_value=30.0,
    measureddepth_value=1000,
    bedrockaltitude_value=0)

bh1_section1 = orm.BoreholeSection(
    publicid='smi:ch.ethz.sed/bh/section/'
             '11111111-8d89-4f13-95e7-526ade73cc8b',
    starttime=datetime.datetime(2010, 1, 10),
    endtime=datetime.datetime(2010, 12, 10),
    topclosed=False,
    bottomclosed=False,
    toplatitude_value=10.66320713,
    toplatitude_uncertainty=0.5368853227,
    toplongitude_value=10.66320713,
    toplongitude_uncertainty=0.7947170871,
    topaltitude_value=0,
    bottomlatitude_value=10.66320713,
    bottomlatitude_uncertainty=0.5368853227,
    bottomlongitude_value=10.66320713,
    bottomlongitude_uncertainty=0.7947170871,
    bottomaltitude_value=-1000,
    topmeasureddepth_value=900,
    bottommeasureddepth_value=1000,
    holediameter_value=0.3,
    casingdiameter_value=0.28, )

bh1_section2 = orm.BoreholeSection(
    publicid='smi:ch.ethz.sed/bh/section/'
             '11111111-8d89-4f13-95e7-526ade73cc5y',
    starttime=datetime.datetime(2010, 1, 10),
    topclosed=False,
    bottomclosed=True,
    toplatitude_value=10.06320713,
    toplatitude_uncertainty=0.5368853227,
    toplongitude_value=10.06320713,
    toplongitude_uncertainty=0.7947170871,
    topaltitude_value=-1000,
    bottomlatitude_value=10.06320713,
    bottomlatitude_uncertainty=0.5368853227,
    bottomlongitude_value=10.06320713,
    bottomlongitude_uncertainty=0.7947170871,
    bottomaltitude_value=-1100,
    topmeasureddepth_value=100,
    bottommeasureddepth_value=1000,
    holediameter_value=0.3,
    casingdiameter_value=0.28, )

sample1 = orm.HydraulicSample(
    datetime_value=datetime.datetime(2010, 12, 9, 12, 00),
    toptemperature_value=273,
    topflow_value=42,
    toppressure_value=73,
    bottomtemperature_value=303,
    bottomflow_value=42,
    bottompressure_value=73,
    fluiddensity_value=8,
    fluidviscosity_value=0.5,
    fluidph_value=7, )

sample2 = orm.HydraulicSample(
    datetime_value=datetime.datetime(2010, 12, 9, 13, 00),
    toptemperature_value=290,
    topflow_value=52,
    toppressure_value=83,
    bottomtemperature_value=313,
    bottomflow_value=55,
    bottompressure_value=83,
    fluiddensity_value=8,
    fluidviscosity_value=0.7,
    fluidph_value=8, )

sample3 = orm.HydraulicSample(
    datetime_value=datetime.datetime(2010, 12, 1, 12, 00),
    toptemperature_value=273,
    topflow_value=42,
    toppressure_value=73,
    bottomtemperature_value=303,
    bottomflow_value=42,
    bottompressure_value=73,
    fluiddensity_value=8,
    fluidviscosity_value=0.5,
    fluidph_value=7, )

# Second borehole, no sections.
bh2 = orm.Borehole(
    publicid='smi:ch.ethz.sed/bh/11111111-e4a0-4692-bf29-33b5591eb799',
    name="Borehole2",
    description="description of borehole2",
    latitude_value=40.66320713,
    latitude_uncertainty=0.5368853227,
    longitude_value=-10.66320713,
    longitude_uncertainty=0.7947170871,
    measureddepth_value=2000.0,
    altitude_value=30.0,
    bedrockaltitude_value=100)

# Third borehole, sections but no hydraulics
bh3 = orm.Borehole(
    publicid='smi:ch.ethz.sed/bh/11111111-e4a0-4692-bf29-33b5591eb7987',
    name="Borehole3",
    description="description of borehole3",
    latitude_value=10.66320713,
    latitude_uncertainty=0.5368853227,
    longitude_value=10.66320713,
    longitude_uncertainty=0.7947170871,
    altitude_value=30.0,
    bedrockaltitude_value=0)

bh3_section1 = orm.BoreholeSection(
    publicid='smi:ch.ethz.sed/bh/section/'
             '11111111-8d89-4f13-95e7-526ade73cc7c',
    starttime=datetime.datetime(2018, 12, 1, 00, 1),
    endtime=datetime.datetime(2019, 2, 12, 00),
    topclosed=False,
    bottomclosed=False,
    toplatitude_value=15.63484349,
    toplatitude_uncertainty=0.0008854447,
    toplongitude_value=-50.66323323,
    toplongitude_uncertainty=0.7947170871,
    topaltitude_value=0,
    bottomlatitude_value=50.66323327,
    bottomlatitude_uncertainty=0.5368853227,
    bottomlongitude_value=50.66323330,
    bottomlongitude_uncertainty=0.7947170871,
    bottomaltitude_value=-100,
    topmeasureddepth_value=900,
    bottommeasureddepth_value=1000,
    holediameter_value=0.3,
    casingdiameter_value=0.28, )

bh3_section2 = orm.BoreholeSection(
    publicid='smi:ch.ethz.sed/bh/section/'
             '11111111-8d89-4f13-95e7-526ade73cc2i',
    starttime=datetime.datetime(2018, 12, 1, 00, 1),
    endtime=datetime.datetime(2019, 2, 12, 00, 00),
    topclosed=False,
    bottomclosed=False,
    toplatitude_value=15.63484349,
    toplatitude_uncertainty=0.0008854447,
    toplongitude_value=-50.66323323,
    toplongitude_uncertainty=0.7947170871,
    topaltitude_value=-100,
    bottomlatitude_value=50.66323327,
    bottomlatitude_uncertainty=0.5368853227,
    bottomlongitude_value=50.66323330,
    bottomlongitude_uncertainty=0.7947170871,
    bottomaltitude_value=-200,
    topmeasureddepth_value=900,
    bottommeasureddepth_value=1000,
    holediameter_value=0.3,
    casingdiameter_value=0.28, )

bh3_section3 = orm.BoreholeSection(
    publicid='smi:ch.ethz.sed/bh/section/'
             '11111111-8d89-4f13-95e7-526ade73cc5e',
    starttime=datetime.datetime(2019, 2, 12, 00, 1),
    endtime=datetime.datetime(2019, 3, 12, 00, 00),
    topclosed=False,
    bottomclosed=True,
    toplatitude_value=15.63484349,
    toplatitude_uncertainty=0.0008854447,
    toplongitude_value=-50.66323323,
    toplongitude_uncertainty=0.7947170871,
    topaltitude_value=-100,
    bottomlatitude_value=50.66323327,
    bottomlatitude_uncertainty=0.5368853227,
    bottomlongitude_value=50.66323330,
    bottomlongitude_uncertainty=0.7947170871,
    bottomaltitude_value=-200,
    holediameter_value=0.3,
    casingdiameter_value=0.25, )  # This has been altered from bh3_section2


bh4 = orm.Borehole(
    publicid='smi:ch.ethz.sed/bh/11111111-e4a0-4692-bf29-33b5591eb7123',
    name="Borehole4",
    description="description of borehole4",
    latitude_value=10.66320713,
    latitude_uncertainty=0.5368853227,
    longitude_value=10.66320713,
    longitude_uncertainty=0.7947170871,
    altitude_value=30.0,
    bedrockaltitude_value=0)

bh4_section1 = orm.BoreholeSection(
    publicid='smi:ch.ethz.sed/bh/section/'
             '11111111-8d89-4f13-95e7-526ade73c123',
    topclosed=False,
    bottomclosed=False,
    toplatitude_value=15.63484349,
    toplatitude_uncertainty=0.0008854447,
    toplongitude_value=-50.66323323,
    toplongitude_uncertainty=0.7947170871,
    topaltitude_value=0,
    bottomlatitude_value=50.66323327,
    bottomlatitude_uncertainty=0.5368853227,
    bottomlongitude_value=50.66323330,
    bottomlongitude_uncertainty=0.7947170871,
    bottomaltitude_value=-100,
    topmeasureddepth_value=900,
    bottommeasureddepth_value=1000,
    holediameter_value=0.3,
    casingdiameter_value=0.28, )

samples_single_section = []
start_date = datetime.datetime(2010, 12, 1)
flow = 0.001
for dt in [start_date + datetime.timedelta(minutes=n) for n in range(900)]:
    samplex = orm.HydraulicSample(
        datetime_value=dt,
        toptemperature_value=273,
        topflow_value=flow,
        toppressure_value=73,
        bottomtemperature_value=303,
        bottomflow_value=flow,
        bottompressure_value=73,
        fluiddensity_value=8,
        fluidviscosity_value=0.5,
        fluidph_value=7, )
    samples_single_section.append(samplex)
    flow += 0.001


def insert_orm_values(db_url):

    bh1_section1._hydraulics.append(sample1)
    bh1_section1._hydraulics.append(sample2)
    bh1_section1._hydraulics.append(sample3)
    bh4_section1._hydraulics = samples_single_section
    bh1._sections = [bh1_section1, bh1_section2]
    bh4._sections = [bh4_section1]

    bh3._sections = [bh3_section1, bh3_section2, bh3_section3]

    try:
        engine = create_engine(db_url, echo="debug")

        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(bh0)
        session.add(bh1)
        session.add(bh2)
        session.add(bh3)
        session.add(bh4)
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
    insert_orm_values(args.db_url)
