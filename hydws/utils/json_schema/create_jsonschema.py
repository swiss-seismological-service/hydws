"""
Creates a jsonschema draft 4 schema to validate a JSON file of borehole data.
This schema file is based upon the HYDWS marshmallow schemas and
will be regenerated if these schemas change, under a different version.
"""
from os.path import join, isdir, isfile
import json
import argparse
from marshmallow_jsonschema import JSONSchema
from hydws.utils.error import Error


class VersionNotImplementedError(Error):
    """The web service version does not exist. {}"""

class PathError(Error):
    """The path does not exist. {}"""

def write_borehole_jsonschema(jsonschema_output_path):
    json_schema = JSONSchema()
    borehole_schema = BoreholeSchema()
    dumped_borehole_schema = json_schema.dump(borehole_schema)
    strict_borehole_schema = dumped_borehole_schema.copy()

    # (sarsonl) This is a hack, but the only method at the moment that
    # marshmallow_jsonschema allows to make the schema strict, i.e.
    # no additional fields allowed. As there are multiple schemas defined
    # each schema definition must have the additionalProperties set to False.
    for schema in dumped_borehole_schema["definitions"].keys():
        strict_borehole_schema["definitions"][schema].\
            update({"additionalProperties": False})

    with open(jsonschema_output_path, 'w', encoding='utf-8') as f:
        try:
            json.dump(strict_borehole_schema, f, ensure_ascii=False, indent=2)
        except TypeError as e:
            raise Exception("json schema cannot be serialized: {}".format(e))
    print("JSON schema written to: ", jsonschema_output_path)

def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("version", type=str, choices=["v1", ],
                        help=" HYDWS version string.")
    parser.add_argument("--path", type=str, default="",
                        help="Path to create jsonschema.")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite file if exists.")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parseargs()
    jsonschema_write_to = join(
        args.path, "hydws_jsonschema_{}.json".format(args.version))
    if args.version == 'v1':
        from hydws.server.v1.ostream.schema import BoreholeSchema
    else:
        raise VersionNotImplementedError("Version does not exist")
    if args.path:
        if not isdir(args.path):
            raise PathError("Path for creation of jsonschema does not exist.")
    if isfile(jsonschema_write_to):
        if args.force:
            print("Existing file will be overwritten: {}".
                  format(jsonschema_write_to))
        else:
            raise FileExistsError("{} exists and will not be overwritten".
                                  format(jsonschema_write_to))
    write_borehole_jsonschema(jsonschema_write_to)
