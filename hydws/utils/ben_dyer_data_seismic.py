import pandas as pd
import os
import datetime as dt
from pyproj import Transformer

ABS_PATH = os.path.dirname(os.path.realpath(__file__))
from obspy import UTCDateTime
from obspy.core.event import Catalog, Event, Origin, Magnitude
from obspy.geodetics import FlinnEngdahl


LAB_ORIGIN_EASTING = 2679720.70
LAB_ORIGIN_NORTHING = 1151600.13
LAB_ORIGIN_DEPTH = 1485.00

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

def read_seismic():
        transformer = RamsisCoordinateTransformer(LAB_ORIGIN_EASTING,
                                              LAB_ORIGIN_NORTHING,
                                              LAB_ORIGIN_DEPTH)
        xls = pd.ExcelFile(os.path.join(ABS_PATH, 'ben_dyer_data',
                  "Zones2and6and7FinalLocations.xls"))
        sheet1 =  xls.parse('Zones2and6and7FinalLocations')
        sheet1.columns = ['sequence','source', 'datetime', 'profile', 'status',
                          'cluster', 'y', 'x', 'depth', 'mom_mag',
                          'pgv', 'stage', 'pwave_signoise', 'swave_signoise',
                          'quality', 'error', 'location', 'rms_noise', 'dummy1',
                          'dummy2', 'dummy3', 'dummy4', 'dummy5']
        sheet1['datetime'] = pd.to_datetime(sheet1['datetime'], format="  %d/%m/%Y      %H:%M:%S")

        # Code from https://github.com/obspy/docs/blob/master/workshops/2016-03-07_ipgp/06_Event_metadata-with_solutions.ipynb
        cat = Catalog()
        cat.description = "Bedretto Events detection Jan/Feb 2020 Zones 2, 6, 7"
        for ind, row in sheet1.iterrows(): 
            if row['status'] != 2:
                continue
            e = Event()
            e.event_type = "earthquake"
            
            o = Origin()
            o.time = row['datetime']
            o.longitude, o.latitude, _ = transformer.from_local_coords(row['y'], row['x'])
            o.depth = row['depth'] + LAB_ORIGIN_DEPTH
            o.depth_type = "from location"
            o.evaluation_mode = "manual"
            o.evaluation_status = "final"
            o.region = FlinnEngdahl().get_region(o.longitude, o.latitude)
            
            m = Magnitude()
            m.mag = row['mom_mag']
            m.magnitude_type = "Mw"
            
            # Not sure what else should go in or where it should go...
            
            cat.append(e)
            e.origins = [o]
            e.magnitudes = [m]
            m.origin_id = o.resource_id
            e.preferred_origin_id = o.resource_id
            e.preferred_magnitude_id = m.resource_id
        
        cat.write("Bedretto_test_seismic_catalog.xml", format="QUAKEML")

def main():
        read_seismic()

if __name__ == '__main__':
    main()
