"""
@author Ali Da Silva Ouederni
@date Oct. 2019

Application to convert csv data to a json file
"""
#!/usr/bin/python
# flake8: noqa

import sys
import getopt
import re
import csv
import json
import datetime as dt
import argparse
import os
import hydws.server.v1.ostream.schema as schema

from hydws.db.orm import Borehole, BoreholeSection, HydraulicSample

from datetime import timedelta

def main(argv):
    mylist = []
    today = dt.datetime.today()
    mylist.append(today)
    filepath_csv = ''
    output_filepath_json = ''
    boreholesection_param = ''
    publicid1 = "id:borehole_{:%Y%m%dT%H%M%S.%f}".format(today)
    publicid2 = "id:boreholesection_{:%Y%m%dT%H%M%S.%f}".format(today)
    try:
        opts, args = getopt.getopt(argv, "hi:o:b:s:",
                                   ["ifile=", "ofile=",
                                    "borehole_param=", "boreholeSection="])
    except getopt.GetoptError:
        print("##########################################################"
              "############################################")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
              "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("Oops!", sys.exc_info()[0], "occured.")
        print("Required are -i (inputfile) -o (outputfile) -b "
              "(Boreholevalues)")
        print("Optional with the required is -s (BoreholeSectionvalues)")
        print("Make sure you give the right values with arguments.")
        print("Try it again!")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
              "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("#########################################################"
              "############################################")
        sys.exit(2)
    print("")
    print("#############################################################"
          "########################################")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
          "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    for opt, arg in opts:
        if opt == '-h':
            my_parser = argparse.ArgumentParser(description="A description")
            my_parser.add_argument('inputfile',
                                   metavar='-i',
                                   type=str,
                                   help='The path to the inputfile')
            my_parser.add_argument('outputfile',
                                   metavar='-o',
                                   type=str,
                                   help='The path for the outputfile')
            my_parser.add_argument('borehole',
                                   metavar='-b',
                                   type=str,
                                   help='Values for the borehole(required: '
                                        'latitude_value,'
                                        'longitude_value, altitude_value, '
                                        'depth_value)')
            my_parser.add_argument('-s',
                                   metavar='--boreholeSection',
                                   type=str,
                                   help='Optional value -s, to put after the '
                                        'Borehole -b, for the boreholeSection')
            args = my_parser.parse_args()
            input_path = args.Path
            print('\n'.join(os.listdir(input_path)))
            sys.exit()
        elif opt in ("-i", "--ifile"):
            filepath_csv = arg
            print("Argument given for Inputfile -i: " + arg)
        elif opt in ("-o", "--ofile"):
            output_filepath_json = arg
            print("Argument given for Outputfile -o: " + arg)
        elif opt in ("-b", "--borehole_param"):
            borehole_param = arg
            print("Arguments given for the Borehole -b: " + arg)
        elif opt in ("-s", "--boreholeSection"):
            boreholesection_param = arg
            print("Arguments given for the Boreholesection -s: " + arg)
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
          "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("##############################################################"
          "#########################################")
    try:
        # First define the Borehole level with
        # information from the geldinganis borehole
        if "latitude_value=" not in borehole_param:
            print("Please define the latitude_value!")
            sys.exit(2)
        if "longitude_value=" not in borehole_param:
            print("Please define the longitude_value!")
            sys.exit(2)
        if "depth_value=" not in borehole_param:
            print("Please define the depth_value!")
            sys.exit(2)
        if ",publicid=" not in borehole_param:
            borehole_param = borehole_param + ",publicid= \"" + \
                publicid1 + "\""
            print(
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("The publicid for the Borehole was not defined, "
                  "publicid set to: " + str(publicid1))
        print("")
        print("Borehole: ", borehole_param)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
              "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("##########################################################"
              "#############################################")
        bh = Borehole(**eval("dict({})".format(borehole_param)))
    except:
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
              "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("Oops!", sys.exc_info()[0], "occured.")
        print("Required are -i (inputfile) -o (outputfile) -b (Boreholevalues)")
        print("Optional with the required is -s (BoreholeSectionvalues)")
        print("Make sure you give the right values with arguments.")
        print("Try it again!")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
              "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("########################################################"
              "###############################################")
        sys.exit(2)
    # Then define the borehole section
    try:
        try:
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
                  "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            if "toplatitude_value=" not in boreholesection_param:
                boreholesection_param = boreholesection_param + "toplatitude_value=" + str(bh.latitude_value)
                print("The toplatitude_value was not defined, toplatitude_value set to: " + str(bh.latitude_value))
            if "bottomlatitude_value=" not in boreholesection_param:
                boreholesection_param = boreholesection_param + ",bottomlatitude_value=" + str(bh.latitude_value)
                print("The bottomlatitude_value was not defined, bottomlatitude_value set to: " +
                      str(bh.latitude_value))
            if "toplongitude_value=" not in boreholesection_param:
                boreholesection_param = boreholesection_param + ",toplongitude_value=" + str(bh.longitude_value)
                print("The toplongitude_value was not defined, toplongitude_value set to: " + str(bh.longitude_value))
            if "bottomlongitude_value=" not in boreholesection_param:
                boreholesection_param = boreholesection_param + ",bottomlongitude_value=" + str(bh.longitude_value)
                print("The bottomlongitude_value was not defined, bottomlongitude_value set to: " +
                      str(bh.longitude_value))
            if "topdepth_value=" not in boreholesection_param:
                boreholesection_param = boreholesection_param + ",topdepth_value=" + str(0)
                print("The topdepth_value was not defined, topdepth_value set to: " + str(0))
            if ",publicid=" not in boreholesection_param:
                boreholesection_param = boreholesection_param + ",publicid= \"" + publicid2 + "\""
                print("The publicid for the Boreholesection was not defined, publicid set to: " + str(publicid2))
            print("")
            print("Borehole_Section: ", boreholesection_param)
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
                  "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("####################################################"
                  "###################################################")
            bh_section = BoreholeSection(**eval("dict({})".format(boreholesection_param)))
        except:
            print("Because the BoreholeSection -s was not defined,")
            print("The toplatitude_value was not defined, toplatitude_value set to: " + str(bh.latitude_value))
            boreholesection_param = boreholesection_param + "toplatitude_value=" + str(bh.latitude_value)
            print("The bottomlatitude_value was not defined, bottomlatitude_value set to: " + str(bh.latitude_value))
            boreholesection_param = boreholesection_param + ",bottomlatitude_value=" + str(bh.latitude_value)
            print("The toplongitude_value was not defined, toplongitude_value set to: " + str(bh.longitude_value))
            boreholesection_param = boreholesection_param + ",toplongitude_value=" + str(bh.longitude_value)
            print("The bottomlongitude_value was not defined, bottomlongitude_value set to: " + str(bh.longitude_value))
            boreholesection_param = boreholesection_param + ",bottomlongitude_value=" + str(bh.longitude_value)
            print("The topdepth_value was not defined, topdepth_value set to: " + str(0))
            boreholesection_param = boreholesection_param + ",topdepth_value=" + str(0)
            print("The publicid for the Boreholesection was not defined, publicid set to: " + str(publicid2))
            boreholesection_param = boreholesection_param + ",publicid= \"" + publicid2 + "\""
            print(
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print(
                "####################################################"
                "###################################################")
            bh_section = BoreholeSection(**eval("dict({})".format(boreholesection_param)))

    except:
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
              "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("Oops!", sys.exc_info()[0], "occured.")
        print("Required are -i (inputfile) -o (outputfile) -b (Boreholevalues)")
        print("Optional with the required is -s (BoreholeSectionvalues)")
        print("Make sure you give the right values with arguments.")
        print("Try it again!")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
              "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("###################################################"
              "####################################################")
        sys.exit(2)

    def daterange(start_date, end_date):
        delta = timedelta(seconds=60)
        while start_date < end_date:
            yield start_date
            start_date += delta

    with open(filepath_csv) as opened_f:
        loaded_hydraulics = []
        for row in csv.DictReader(opened_f):
            loaded_hydraulics.append({k: (v if k != 'Start time (date)' and k != 'End time (date)'
                                          else dt.datetime.strptime(v, "%d/%m/ %H:%M").replace(year=2019))
                                      for k, v in row.items()})

    hydraulic_samples = list()
    regex = re.compile(
        r"High rate pulse injection between (?P<min_val>\d+) l/s & (?P<max_val>\d+) l/s \(highest possible "
        r"frequency\)")
    for sample in loaded_hydraulics:
        m = regex.match(sample['Operation'])
        if m:
            for i, t in enumerate(daterange(sample['Start time (date)'], sample['End time (date)'])):
                if i % 2:
                    hydraulic_samples.append(HydraulicSample(
                        datetime_value=t, topflow_value=int(m.group('min_val')) / 1000
                    ))
                else:
                    hydraulic_samples.append(HydraulicSample(
                        datetime_value=t, topflow_value=int(m.group('max_val')) / 1000
                    ))
        else:
            hydraulic_samples.append(HydraulicSample(
                datetime_value=sample['Start time (date)'], topflow_value=int(sample['Flow rate (l/s)']) / 1000
            ))

    # Associate the borehole with the section and the hydraulics
    bh_section._hydraulics = hydraulic_samples
    bh._sections = [bh_section]

    dumped_data = schema.BoreholeSchema().dump(bh)

    with open(output_filepath_json, 'w') as fpath:
        json.dump(dumped_data, fpath)

    print("written to file: ", output_filepath_json)


if __name__ == '__main__':
    main(sys.argv[1:])
