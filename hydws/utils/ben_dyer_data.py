"""
@author Laura Sarson
@date Aug. 2020

"""

#!/usr/bin/python
import copy
import csv
import json
from pyproj import Transformer
import datetime as dt
import os

from hydws.db.orm import Borehole, BoreholeSection, HydraulicSample
from hydws.server.v1.ostream.schema import BoreholeSchema

from datetime import timedelta

HOLE_DIAMETER = 0.3 # Incorrect hole diameter

# Use CH1903+, EPSG:2056
# lab origin converts to:
# 8.477376506386285, 46.51096307156062
###
# There are in effect, two local coordinate systems being used here.
# The swiss coordinate system and the local bedretto system.
#
# We are going to convert from the local Bedretto coords,
# to swiss coords and then to lat/lon
LAB_ORIGIN_EASTING = 2679720.70
LAB_ORIGIN_NORTHING = 1151600.13
LAB_ORIGIN_DEPTH = -1485.00

CB1_TOP_LOCAL_EASTING = -37.44
CB1_TOP_LOCAL_NORTHING = 33.43
CB1_TOP_LOCAL_DEPTH = -0.41

CB1_MEASURED_DEPTH = 298.6  # This value is assumed to be the measured depth
# since it is the
# longest measured depth recorded in ben dyer's slides. It could be wrong.

# These values are estimated from the graphics in Ben Dyer's
# slides, it is probably not accurate.
CB1_BOTTOM_LOCAL_DEPTH = 200.0
CB1_BOTTOM_LOCAL_EASTING = -205.0
CB1_BOTTOM_LOCAL_NORTHING = -110.0

CB1_DEPTH = CB1_BOTTOM_LOCAL_DEPTH - CB1_TOP_LOCAL_DEPTH

CB1_PUBLIC_ID = "smi:ch.ethz.sed/bh/CB1"
CB1_PUBLIC_ID_SECTION = "smi:ch.ethz.sed/bh/CB1/section_"

ABS_PATH = os.path.dirname(os.path.realpath(__file__))

CB1_STARTTIME = dt.datetime(2019, 1, 1)

CB1_S1_TOP_PACKER_MDEPTH = 290.7
CB1_S1_BOTTOM_PACKER_MDEPTH = 293.4

CB1_S2_TOP_PACKER_MDEPTH = 265.6
CB1_S2_BOTTOM_PACKER_MDEPTH = 268.3

CB1_S3_TOP_PACKER_MDEPTH = 248.7
CB1_S3_BOTTOM_PACKER_MDEPTH = 251.4
# Same value for top and bottom as only have depth recorded for Hydrofrac test
CB1_S4_TOP_PACKER_MDEPTH = 298.6
CB1_S4_BOTTOM_PACKER_MDEPTH = 298.6

CB1_S5_TOP_PACKER_MDEPTH = 281.0
CB1_S5_BOTTOM_PACKER_MDEPTH = 281.0

CB1_S6_TOP_PACKER_MDEPTH = 288.5
CB1_S6_BOTTOM_PACKER_MDEPTH = 298.5

CB1_S7_TOP_PACKER_MDEPTH = 264.0
CB1_S7_BOTTOM_PACKER_MDEPTH = 274.0


class RamsisCoordinateTransformer:
    def __init__(self, ref_easting, ref_northing, ref_depth,
                 external_proj=4326, local_proj=2056):
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

def get_hydraulics(filename_list):
    hydraulic_samples = []
    # populate hydraulic data from csv:
    start_of_year = dt.datetime(2020, 1, 1)
    # assume that the injected fluid is water?
    old_minute = 0
    for filename in filename_list:
        with open(os.path.join(ABS_PATH, 'ben_dyer_data',
                  'AllHydraulicDataForDivine', filename)) as open_f:
            print("Processing: ", filename)
            reader = csv.reader(open_f, skipinitialspace=True)
            row_count = 0
            file_cols = 0
            for line in reader:
                if row_count == 0:
                    if line == ["line; DayOfYear; Time; Q_in [lpm]; Pi dhl "
                                "[MPa]; Pi uphl [MPa]; Pp uphl [MPa]"]:
                        file_cols = 7
                    elif line == ["line; DayOfYear; Time; Q_in [lpm]; "
                                  "Pi dhl [MPa]; Pi uphl [MPa]"]:
                        file_cols = 6
                    elif line == ["line; DayOfYear; Time; Q_in [lpm]; Pi dhl "
                                  "[MPa]; Pi uphl [MPa]; Pp uphl [MPa]; Pi "
                                  "Flowboard [MPa]"]:
                        file_cols = 8
                    elif line == ["line; DayOfYear; Time; Q_in [lpm]; Pi dhl "
                                  "[MPa]; Pi uphl [MPa]; Pp uphl [MPa]; Q_out"
                                  " [lpm]; Pi Flowboard [MPa]"]:
                        file_cols = 9
                    else:
                        raise IOError(f"not handled: {line}")
                    row_count += 1
                    continue
                if file_cols == 7:
                    (line_num, day_year, time, q_in, pi_dhl,
                     pi_uphl, pp_uphl) = line
                elif file_cols == 6:
                    (line_num, day_year, time, q_in, pi_dhl,
                     pi_uphl) = line
                elif file_cols == 8:
                    (line_num, day_year, time, q_in, pi_dhl, pi_uphl, pp_uphl,
                     pi_flowboard) = line
                elif file_cols == 9:
                    (line_num, day_year, time, q_in, pi_dhl, pi_uphl, pp_uphl,
                     q_out, pi_flowboard) = line

                day_error = 31 if day_year in ['5', '6', '7'] else 0
                dttime = start_of_year + timedelta(float(day_year) -1 +
                                                   float(day_error))
                hour, minute, second = (int(i) for i in time.split(':'))
                if old_minute == minute:
                    continue
                else:
                    old_minute = minute
                dttime = dttime.replace(hour=hour, minute=minute, second=second)
                # Using topflow and toppressure referencing the top of the
                # borehole, even though not sure if it should be bottom
                #- the EM1 and HM1 models currently depend
                # on top values (these can be changed, but should
                # change everything at same time)
                topflow = float(q_in) / (1.0e3 * 60.0)
                # Requirement is that pressures are positive: This is not so
                # for data, any negative values -> 0
                pressure_uphl = float(pi_uphl) * 1.0e6
                if pressure_uphl < 0.0:
                    pressure_uphl = 0.0
                # check if there is any more info that we can add to this.
                hsample = HydraulicSample(datetime_value=dttime,
                                          topflow_value=topflow,
                                          toppressure_value=pressure_uphl)
                hydraulic_samples.append(hsample)
                row_count += 1
    return hydraulic_samples

def borehole_sections(transformer):
    sections = []
    easting_diff = CB1_BOTTOM_LOCAL_EASTING - CB1_TOP_LOCAL_EASTING
    northing_diff = CB1_BOTTOM_LOCAL_NORTHING - CB1_TOP_LOCAL_NORTHING
    depth_diff = CB1_BOTTOM_LOCAL_DEPTH - CB1_TOP_LOCAL_DEPTH

    filenames = [(['STIM_292_20200122T194016_1_Ben.dat',
                   'STIM_292_20200123T035526_2_Ben.dat',
                   'STIM_292_20200123T103113_3_Ben.dat'], 1),
                 (['STIM_267_20200123T152308_Ben.dat'], 2),
                 (['STIM_250_20200123T182903_Ben.dat'], 3),
                 (['HF_298_20200124T181939_Ben.dat'], 4),
                 (['HF_281_new_20200124T194527_Ben.dat'], 5),
                 (['TOTAL_295m_postprocess_Ben.dat'], 6),
                 (['TOTAL_269m_postprocess_Ben.dat'], 7)]
    for filename_list, section_index in filenames:
        # convert measured depth into lat, lon
        mdepth_frac = globals()[
            f'CB1_S{section_index}_TOP_PACKER_MDEPTH'] / CB1_MEASURED_DEPTH

        top_easting = easting_diff * mdepth_frac + CB1_TOP_LOCAL_EASTING
        top_northing = northing_diff * mdepth_frac + CB1_TOP_LOCAL_NORTHING
        top_depth = depth_diff * mdepth_frac + CB1_TOP_LOCAL_DEPTH
        # In the file we want the borehole section depth to be the depth
        # from the borehole top

        (cb1_top_lon,
         cb1_top_lat,
         cb1_top_depth) = transformer.from_local_coords(
            top_easting, top_northing, top_depth)

        bmdepth_frac = globals()[
            f'CB1_S{section_index}_BOTTOM_PACKER_MDEPTH'] / CB1_MEASURED_DEPTH

        bottom_easting = easting_diff * bmdepth_frac + CB1_TOP_LOCAL_EASTING
        bottom_northing = northing_diff * bmdepth_frac + CB1_TOP_LOCAL_NORTHING
        bottom_depth = depth_diff * bmdepth_frac + CB1_TOP_LOCAL_DEPTH
        # In the file we want the borehole section depth to be the depth
        # from the borehole top

        (cb1_bottom_lon,
         cb1_bottom_lat,
         cb1_bottom_depth) = transformer.from_local_coords(
            bottom_easting, bottom_northing, bottom_depth)

        hydraulic_samples = get_hydraulics(filename_list)
        section_dttimes = [sample.datetime_value for sample
                           in hydraulic_samples]
        starttime_section = min(section_dttimes)
        endtime_section = max(section_dttimes)

        borehole_section = BoreholeSection(
            toplongitude_value=cb1_top_lon,
            toplatitude_value=cb1_top_lat,
            topdepth_value=round(top_depth, 2),
            bottomlongitude_value=cb1_bottom_lon,
            bottomlatitude_value=cb1_bottom_lat,
            bottomdepth_value=round(bottom_depth, 2),
            starttime=starttime_section,
            endtime=endtime_section,
            holediameter_value=HOLE_DIAMETER,
            publicid=CB1_PUBLIC_ID_SECTION+str(section_index),
            _hydraulics=hydraulic_samples,
            description=(f"From files: {filename_list}, "
                         f"ben dyer section: {section_index}"),
            topclosed=False,
            bottomclosed=True)
        sections.append(borehole_section)
    return sections

def create_borehole():
    transformer = RamsisCoordinateTransformer(LAB_ORIGIN_EASTING,
                                              LAB_ORIGIN_NORTHING,
                                              LAB_ORIGIN_DEPTH)

    origin_lon, origin_lat, origin_depth = transformer.from_local_coords(
        0, 0, 0)

    cb1_top_lon, cb1_top_lat, cb1_top_depth = transformer.from_local_coords(
        CB1_TOP_LOCAL_EASTING, CB1_TOP_LOCAL_NORTHING, CB1_TOP_LOCAL_DEPTH)

    (cb1_bottom_lon,
     cb1_bottom_lat,
     cb1_bottom_depth) = transformer.from_local_coords(
        CB1_BOTTOM_LOCAL_EASTING,
        CB1_BOTTOM_LOCAL_NORTHING,
        CB1_BOTTOM_LOCAL_DEPTH)

    sections = borehole_sections(transformer)

    borehole = Borehole(longitude_value=cb1_top_lon,
                        latitude_value=cb1_top_lat,
                        altitude_value=-LAB_ORIGIN_DEPTH-CB1_TOP_LOCAL_DEPTH,
                        depth_value=CB1_DEPTH,
                        measureddepth_value=CB1_MEASURED_DEPTH,
                        publicid=CB1_PUBLIC_ID,
                        _sections=sections)
    return borehole

def main():

    borehole = create_borehole()
    borehole_write = copy.deepcopy(borehole)
    for section in borehole._sections:
        starttime = dt.datetime.strftime(section.starttime, "%Y%m%d%H%M%S")
        endtime = dt.datetime.strftime(section.endtime, "%Y%m%d%H%M%S")
        sid = section.topdepth_value
        output_file = f"ben_dyer_cb1_minute_sampled_{starttime}_{endtime}_{sid}m.json"
        section_copy = section.copy()
        borehole_write._sections = [section_copy]
        with open(output_file, 'w') as new_file:
            print("writing to output file:", output_file)
            json.dump(BoreholeSchema(many=False).dump(borehole_write),
                      new_file)


if __name__ == '__main__':
    main()
