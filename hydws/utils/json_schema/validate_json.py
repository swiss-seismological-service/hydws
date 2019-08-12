"""
Validator that uses jsonschema to validate a JSON file against a predefined
schema file. This schema file is based upon the HYDWS marshmallow schemas and
will be regenerated if these schemas change, under a different version.

Usage:
$ python3.6 validate_json.py /path/to/hydws_jsonschema_v1 /path/to/file.json

Where filename.json has been created manually or programatically and contains
a hydws style json instance or array. Below is a (formatted) example of what
a valid instance of a borehole with a section and hydraulics would look like.
This looks like a dictionary and can be defined as such if creating the data
programatically. In python this can then be written to file with json.dump()
using the json library.

{
    "bedrockdepth": {
        "value": 0
    },
    "depth": {
        "value": 1000
    },
    "latitude": {
        "uncertainty": 0.5368853227,
        "value": 10.66320713
    },
    "longitude": {
        "uncertainty": 0.7947170871,
        "value": 10.66320713
    },
    "publicid": "smi:ch.ethz.sed/bh/11111111-e4a0-4692-bf29-33b5591eb798",
    "sections": [
        {
            "bottomclosed": false,
            "bottomdepth": {
                "value": 1000
            },
            "bottomlatitude": {
                "uncertainty": 0.5368853227,
                "value": 10.66320713
            },
            "bottomlongitude": {
                "uncertainty": 0.7947170871,
                "value": 10.66320713
            },
            "casingdiameter": {
                "value": 0.28
            },
            "endtime": "2010-12-10T00:00:00",
            "holediameter": {
                "value": 0.3
            },
            "hydraulics": [
                {
                    "bottomflow": {
                        "value": 42
                    },
                    "bottompressure": {
                        "value": 73
                    },
                    "bottomtemperature": {
                        "value": 303
                    },
                    "datetime": {
                        "value": "2010-12-01T12:00:00"
                    },
                    "fluiddensity": {
                        "value": 8
                    },
                    "fluidph": {
                        "value": 7
                    },
                    "fluidviscosity": {
                        "value": 0.5
                    },
                    "topflow": {
                        "value": 42
                    },
                    "toppressure": {
                        "value": 73
                    },
                    "toptemperature": {
                        "value": 273
                    }
                }
            ],
            "publicid": "smi:ch.ethz.sed/bh/section/11111111-8d89-ade73cc8b",
            "starttime": "2010-01-10T00:00:00",
            "topclosed": false,
            "topdepth": {
                "value": 0
            },
            "toplatitude": {
                "uncertainty": 0.5368853227,
                "value": 10.66320713
            },
            "toplongitude": {
                "uncertainty": 0.7947170871,
                "value": 10.66320713
            }
        }
    ]
}

"""
import sys
import json
import argparse
from jsonschema import Draft4Validator
from jsonschema.exceptions import ValidationError as JSValidationError
from hydws.utils.error import Error


class ValidationFailedError(Error):
    """Json schema validation failed: {}"""


def flatten_dict(data, sep='_'):
    """
    Flatten a a nested dict using `sep` as key
    separator, also handle a list of dicts and dict
    values which are lists.

    :param data: Data containing dictionary keys which include
        `sep`. This seperator should delimit the dict
        key into a nested dict
        e.g. {"datetime_value": "2019-01-01"}
        will be decomposed into {"datetime": {"value": "2019-01-01"}}
    :type data: List of dicts or dict.
    :param sep: Dictionary key delimitor
    :type sep: String

    :return: `data` with dictionary keys decomposed to nested dicts.
    :type: List of dicts or dict: of same type as input `data`
    """
    retval = {}
    list_array = []
    if isinstance(data, list):
        for item in data:
            list_array.append(flatten_dict(item))
        return list_array
    else:
        for k, v in data.items():
            if isinstance(v, dict):
                for sub_k, sub_v in flatten_dict(v, sep).items():
                    retval[k + sep + sub_k] = sub_v
            elif isinstance(v, list):
                list_value = []
                for item in v:
                    list_value.append(flatten_dict(item))
                retval[k] = list_value
            else:
                retval[k] = v
        return retval

def validate_json_file(jsonschema, infile):
    """
    Validates a json file against a jsonschema which is composed
    in a jsonschema Draft 4 format.

    :param jsonschema: Filename of jsonschema that has been created
        to validate data against HYDWS schemas
    :type jsonschema: File containing JSON data
    :param infile: File containing JSON data
    :type infile: Readable file object

    :raises: jsonschema.exceptions.ValidationError if the file
        does not match the schema.
    """
    jsonschema_borehole = json.load(jsonschema)
    data = json.load(infile)

    data = flatten_dict(data)

    if isinstance(data, list):
        for item in data:
            Draft4Validator(jsonschema_borehole).check_schema(item)
    else:
        try:
            Draft4Validator(jsonschema_borehole).validate(data)
        except JSValidationError as err:
            raise ValidationFailedError(err)

    print("No Exceptions raised: JSON validated!")


def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("jsonschema", type=argparse.FileType('r'),
                        help="Path to jsonschema.")
    parser.add_argument("infile", nargs="?", type=argparse.FileType('r'),
                        default=sys.stdin,
                        help="Path to file for validation.")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parseargs()
    validate_json_file(args.jsonschema, args.infile)
