"""
Dependencies:
    pip install xlrd pandas obspy
    # Other libraries that are required by these modules should be downloaded.

Usage:
    python ~/ben_dyer_data_seismic.py
    --output_filename output_name.qml new_excel_file.xls old_excel_file.xls

If --output_filename is not defined, results will be written to standard out
"""

import sys
import argparse
import pandas as pd
import datetime
from pyproj import Transformer
import logging

from obspy.core.event import Catalog, Event, Origin, Magnitude,\
    CreationInfo, Comment
from obspy.geodetics import FlinnEngdahl

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('QUAKEML_TRANSFORM')

class CoordinateTransformer:
    def __init__(self, ref_easting, ref_northing, ref_depth,
                 external_proj, local_proj):
        self.ref_easting = ref_easting
        self.ref_northing = ref_northing
        self.ref_depth = ref_depth
        self.local_proj = local_proj
        self.external_proj = external_proj

        self.transformer_to_local = Transformer.from_proj(
            self.external_proj, self.local_proj, always_xy=True)
        self.transformer_to_external = Transformer.from_proj(
            self.local_proj, self.external_proj, always_xy=True)

    def to_local_coords(self, lon, lat, depth=None):
        # Easting and northing in projected coordinates
        easting_0, northing_0 = self.transformer_to_local.transform(lon, lat)
        easting = easting_0 - self.ref_easting
        northing = northing_0 - self.ref_northing
        if depth:
            new_depth = depth - self.ref_depth
        else:
            new_depth = None

        return easting, northing, new_depth

    def from_local_coords(self, easting, northing, depth=None):
        easting_0 = easting + self.ref_easting
        northing_0 = northing + self.ref_northing

        lon, lat = self.transformer_to_external.transform(easting_0,
                                                          northing_0)
        if depth:
            new_depth = self.ref_depth + depth
        else:
            new_depth = None
        return lon, lat, new_depth

def read_csv(input_filename, sheet_name):
    df = pd.read_csv(input_filename, sep=';')
    df = df.drop(axis=1, labels=['id_watched_folder',
                                 'Time_Stamp', 'Trigger Time'])
    # Sort values by columns that might change if a row has been
    # manually updated.
    df = df.sort_values(["Origin Time", "Source"])
    df = df.reset_index(drop=True)
    return df

def diff_csv(df_1, df_2):
    comparison = ~df_1.eq(df_2)
    new_locations = comparison.any(axis=1)
    new_rows = df_2[new_locations==True] # noqa
    return new_rows


def read_seismic(old_csv_filename, new_csv_filename, sheet_name,
                 lab_origin_easting, lab_origin_northing, lab_origin_depth,
                 local_proj, external_proj, creation_time,
                 catalog_description="",
                 output_filename=sys.stdout):
    transformer = CoordinateTransformer(lab_origin_easting,
                                        lab_origin_northing,
                                        lab_origin_depth,
                                        external_proj=external_proj,
                                        local_proj=local_proj)
    old_df = read_csv(old_csv_filename, sheet_name)
    new_df = read_csv(new_csv_filename, sheet_name)
    new_rows = diff_csv(new_df, old_df)
    # Code from https://github.com/obspy/docs/blob/master/workshops/2016-03-07
    # ipgp/06_Event_metadata-with_solutions.ipynb
    cat = Catalog()
    cat.description = catalog_description
    for ind, row in new_rows.iterrows():
        if row['Status'] not in [2, 4, 5]:
            continue
        e = Event()
        if row['Status'] == 2:
            e.event_type = "earthquake"
        elif row['Status'] == 4:
            e.event_type = "explosion"
        elif row['Status'] == 5:
            e.event_type = "not existing"
        o = Origin()
        o.time = row['Origin Time']
        o.longitude, o.latitude, _ = transformer.from_local_coords(row['X'],
                                                                   row['Y'])
        o.depth = row['Depth'] + lab_origin_depth
        o.depth_type = "from location"
        ev_mode = row['Location'].lower()
        if "l2 msmx" in ev_mode or "l2 check" in ev_mode:
            o.evaluation_mode = "automatic"
        elif "boot msmx" in ev_mode:
            o.evaluation_mode = "manual"
        else:
            e.event_type == "not existing"
        o.evaluation_status = "final"
        o.region = FlinnEngdahl().get_region(o.longitude, o.latitude)

        m = Magnitude()
        m.mag = row['MomMag']
        m.magnitude_type = "Mw"

        # Not sure what else should go in or where it should go...

        cat.append(e)
        e.origins = [o]
        e.magnitudes = [m]
        m.origin_id = o.resource_id
        e.preferred_origin_id = o.resource_id
        e.preferred_magnitude_id = m.resource_id
        creation_datetime = datetime.datetime.utcfromtimestamp(creation_time)
        info = CreationInfo(author="Divine", agency_id="GES",
                            creation_time=creation_datetime)
        e.creation_info = info
        o.creation_info = info
        m.creation_info = info
        o.comments = [Comment(text=row['Quality'],
                              resource_id="smi:ch.ges/locationquality/divine")]
    if not output_filename:
        output_filename = sys.stdout.buffer
    cat.write(output_filename, format="QUAKEML")


def parser():

    parser = argparse.ArgumentParser(
        description='Arguments to read Divine seismic events')
    # required arguments
    parser.add_argument("new_csv_filename", type=str,
                        help=("Divine input filename (of type excel) "
                              " including absolute path, to read from."))
    parser.add_argument("old_csv_filename", type=str,
                        help=("Divine input filename (of type excel) "
                              " including absolute path, to read from."))
    # optional arguments
    parser.add_argument("--sheet_name", type=str,
                        default="DivineEvents_Dieter",
                        help=("Sheet name to read from on spreadsheet."))
    parser.add_argument("--output_filename", type=str,
                        help=("Output filename including absolute path "
                              "if wanting "
                              "results written to file, else stdout."))
    parser.add_argument("--catalog_description", type=str,
                        help=("Description to be saved in catalog output"))
    parser.add_argument("--lab_origin_easting", type=float, default=2679720.70)
    parser.add_argument("--lab_origin_northing", type=float,
                        default=1151600.13)
    parser.add_argument("--lab_origin_depth", type=float, default=-1485.00)
    parser.add_argument("--local_proj", type=int, default=2056,
                        help=("EPSG projection integer for local coordinates."
                              "Default value is swiss CH1903+ grid suitable "
                              "for Bedretto."))
    parser.add_argument("--external_proj", type=int, default=4326,
                        help=("EPSG projection integer for external coords,"
                              "default is WGS84 grid."))
    parser.add_argument("--creation_time", type=float,
                        default=datetime.datetime.timestamp(
                            datetime.datetime.now(datetime.timezone.utc)))

    args = parser.parse_args()
    return args

def main():
    args = parser()
    read_seismic(
        args.new_csv_filename,
        args.old_csv_filename,
        args.sheet_name,
        args.lab_origin_easting,
        args.lab_origin_northing,
        args.lab_origin_depth,
        args.local_proj,
        args.external_proj,
        args.creation_time,
        catalog_description=args.catalog_description,
        output_filename=args.output_filename)


if __name__ == '__main__':
    main()
