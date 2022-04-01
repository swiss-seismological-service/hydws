# hydws

REST webservice allowing access to hydraulic data.
<<<<<<< HEAD
For a full specification of the api, please find the documentation under /docs/api.md
=======
>>>>>>> feat: add Readme and License

Instructions for installation and examples of usage may be found below.

## Installation

Currently, there is no bare-metal installation description available. Please,
use the ready-to-use Docker production image.

## Docker Installation

A basic knowledge about [Docker](https://docs.docker.com/engine/) and how
this kind of application containers work is required. For more information
about operating system support (which includes Linux, macOS and specific
versions of Windows) and on how to install Docker, please refer to the official
[Docker website](https://www.docker.com/products/docker).

<<<<<<< HEAD
**Features provided**:

* based on [baseimage](https://hub.docker.com/r/phusion/baseimage/)
* `apache2` + [mod_wsgi](https://github.com/GrahamDumpleton/mod_wsgi) for
  for Python 3.6
* powered by [PostgreSQL](https://www.postgresql.org/)
* logging (file based)

**Introduction**:

To construct a Docker image with the appropriate configuration it is
recommended to build your image from a Dockerfile. After cloning the repository
change into the `docker/` directory and modify the configuration.

```
$ cd docker/prod
```

=======
>>>>>>> feat: add Readme and License
**Configuration**:

Before building and running the container adjust the variables defined within
`.env` configuration file according to your needs. Make sure to pick a proper
username and password for the internally used PostgreSQL database and write
these down for later.

<<<<<<< HEAD
**Building**:

Once you environment variables are configured you are ready to build the
container image.

```
$ docker build -t hydws:1.0 .
```

**Compose Configuration**:

In case you want to manage your own volumes now is the time. The configuration
provided relies on named docker volumes.

=======
>>>>>>> feat: add Readme and License
**Deployment**:

The container should be run using the provided `docker-compose.yml`
configuration file.

```
$ docker-compose up -d
```

<<<<<<< HEAD
When deploying for the first time you are required to initialize the database.
This will create the database schema:

```
$ docker exec <container_name> \
  hydws-db-init \
  --logging-conf /var/www/hydws/config/logging.conf \
  postgresql://user:pass@hydws-psql:5432/hydws
```

When the containers are running the service is now available under
`http://localhost:8080`.


## API usage

The full specification for the HYDWS API can be found here: <link to spec>

Some examples demonstrate the usage with the data using db_url=test.db


To return an array of JSON objects representing boreholes:

```
$ curl "http://localhost:5000/hydws/v1/boreholes?&level=borehole"

```

To return a JSON object representing a borehole with all borehole sections and
all hydraulics:

```
$ curl "http://localhost:5000/hydws/v1/boreholes/c21pOmNoLmV0aHouc2VkL2JoLzExMTExMTExLWU0YTAtNDY5Mi1iZjI5LTMzYjU1OTFlYjc5OA==?level=hydraulic"

```
Note: the borehole publicid: c21pOmNoLmV0... is encoded with base64. This is
decoded within the application.  The command to encode/decode strings with
python can be found below:
```
import base64
encoded borehole publicid = base64.b64encode(b'<borehole publicid>')
decoded borehole publicid = base64.b64decode(b'<encoded borehole publicid>')
```

To return a JSON array of all hydraulics from a specific borehole and specific
section:
```
$ curl "http://localhost:5000/hydws/v1/boreholes/c21pOmNoLmV0aHouc2VkL2JoLzExMTExMTExLWU0YTAtNDY5Mi1iZjI5LTMzYjU1OTFlYjc5OA==/sections/c21pOmNoLmV0aHouc2VkL2JoL3NlY3Rpb24vMTExMTExMTEtOGQ4OS00ZjEzLTk1ZTctNTI2YWRlNzNjYzhi/hydraulics?"
```

Note: Both the borehole publicid and section publicid are base64 encoded as
noted above.

### API call response body

The response body will be JSON, or an array of JSON objects.


### Postman tests

Postman is an API development and testing tool. A collection of tests has been
created for HYDWS. To run the tests, follow the instructions to initialize and
run a local instance.  The button below can be pressed to run the tests:

[![Run in Postman](https://run.pstmn.io/button.svg)](https://app.getpostman.com/run-collection/3da8e474b7ecf5b8e1e0)

A dump of the Postman collection can be found under the pm/ directory and can be imported directly to Postman if required.

## Unit tests

Unit tests can be run from the top level of the repository using the pytest
command. 


=======
# HYDWS REST API

## Introduction

HYDWS provides a REST API interface for serving borehole hydraulic sample data. This document specifies the URLs, query parameters and expected results.

## Response

All responses are JSON. The response will reflect the hierarchical one to many relationship between borehole and borehole sections, and between borehole section and hydraulic samples.
Both borehole and borehole section have a unique publicid which is required to make calls which specifies the borehole and/or borehole section. This publicid is to be encoded as base64 before being included in the request URI.

The standard HTTP response status codes are used.

#### POST /hydws/v1/boreholes

Post data to be saved in the database. The data should be of the same json format as is output by the webservice.
Example using curl to upload a file:

`curl -i -X POST -H "Content-Type: application/json" --data @/absolute_path_to_file/borehole_file.json "localhost:8080/hydws/v1/boreholes"`

Where localhost would be changed to the name of the machine that the service is running on.

A file may contain more than one borehole, as a comma seperated list using square parentheses.

The query parameters are as follows:

    * auto_datetime_off: Boolean (default: False) If False, then section startime and endtime will be updated using the hydraulic samples. starttime will be the same as the time of the first hydraulic sample, and endtime the same as the last sample. If True, then starttime and endtime will be used from the input data values of section starttime and endtime. If these do not exist, then starttime and endtime will be kept as the existing values in the database.
    * merge_only: Boolean (default:False) defining whether partial data is being uploaded. Input True if only partial metadata is available, and False if all metadata is available. If the borehole already exists then data will be merged with the existing borehole, independent of this parameter selection.
    * debug: Boolean (default: False) to give a more verbose output on what metadata values are being overwritten.

#### GET /hydws/v1/boreholes

List the available boreholes, optionally with sections.

Parameters:

    * level: level of output results. [`borehole` | `section` # default]
    * starttime: Boreholes returned if any borehole section has a starttime that falls within the section epoch time. format: YYYY-MM-DD[THH:MM:SS] (UTC)
    * endtime: Boreholes returned if any borehole section has a endtime that falls within the section epoch time. format: YYYY-MM-DD[THH:MM:SS] (UTC)
    * minlatitude: Boreholes returned where borehole latitude is equal to or greater than this value. Unit: Degrees
    * minlongitude: Boreholes returned where borehole longitude is equal to or greater than this value. Unit: Degrees
    * maxlatitude: Boreholes returned where borehole latitude is equal to or less than this value. Unit: Degrees
    * maxlongitude: Boreholes returned where borehole longitude is equal to or less than this value. Unit: Degrees

Response:

    [
      {
        "publicid": "id:borehole_20190925T091320389843",
        "longitude": {
          "value": -21.807
        },
        "latitude": {
          "value": 64.1735
        },
        "altitude": {
          "value": 20
        },
        "depth": {
          "value": 1832
        },
        "bedrockdepth": {
          "value": 300
        }
      }
    ]

Notes: Altitude is the altitude of the well head with respect to sea level. Depth is increasing in the downward direction, so is always positively measured with respect to the well head.

#### GET /hydws/v1/boreholes/:borehole_id

Return results of borehole section with optional hydraulic results for the given base64 encoded `borehole_id`.

Parameters:

    Depending on the ‘level’ parameter chosen, different query parameters are allowed.
    ‘level=borehole’: No query parameters allowed.
    ‘level=section’: Query parameters are allowed that have a tick in the s column.
    ‘level=hydraulic’: Query parameters are allowed that have a tick in the h column.

    Some of these parameters refer to properties on borehole sections, and some on hydraulic samples which are children of borehole sections. Those parameters with a tick in the s column will filter borehole sections on section properties.

    Hydraulic samples will only be returned if the borehole section that they belong to has not been filtered out. Hydraulic sample filtering is done with the parameters that only have a tick in the ‘h’ column and not the ‘s’ column. Starttime/endtime is the exception to the rule, as both sections and hydraulic samples have datetime values.

    Time parameters
    As both borehole sections and hydraulic samples have datetime values, both of these will be filtered by the same query parameter. Borehole sections have a datetime epoch which describes the time that the section is valid or active. When a section of a borehole changes (say, a new casing is put into the section) then a new section is created, and the epoch endtime of the old section is updated.
    Hydraulic sample datetime is simply the time that the sample was taken, in UTC.

| Parameter name       | Description                                                                                                                                                                                        | s         | h                                                                                                     |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ----------------------------------------------------------------------------------------------------- | --- | --- |
| level                | String: ‘borehole’                                                                                                                                                                                 | ‘section’ | ‘hydraulic’ #default: section Return boreholes, optionally with sections, optionally with hydraulics. |     |     |
| starttime            | Hydraulic samples are returned if their datetime is less or equal to starttime, borehole sections are returned if their datetime falls within the section epoch time YYYY-MM-DD[THH:MM:SS] (UTC)   | &check;   | &check;                                                                                               |
| endtime              | Hydraulic samples are returned if their datetime is greater or equal to endtime, borehole sections are returned if their datetime falls within the section epoch time. YYYY-MM-DD[THH:MM:SS] (UTC) | &check;   | &check;                                                                                               |
| minbottomtemperature | Float [Kelvin]: Include hydraulic sample results where temperature at bottom of borehole section is equal to or greater than this                                                                  |           | &check;                                                                                               |
| maxbottomtemperature | Float [Kelvin]: Include hydraulic sample results where temperature at bottom of borehole section is equal to or less than this                                                                     |           | &check;                                                                                               |
| mintoptemperature    | Float [Kelvin]: Include hydraulic sample results where temperature at top of borehole section is equal to or greater than this                                                                     |           | &check;                                                                                               |
| maxtoptemperature    | Float [Kelvin]: Include hydraulic sample results where temperature at top of borehole section is equal to or less than this                                                                        |           | &check;                                                                                               |
| minbottomflow        | Float [m^3 per second]: Include hydraulic sample results where flow at bottom of borehole section is equal to or greater than this                                                                 |           | &check;                                                                                               |
| maxbottomflow        | Float [m^3 per second]: Include hydraulic sample results where flow at bottom of borehole section is equal to or less than this                                                                    |           | &check;                                                                                               |
| mintopflow           | Float [m^3 per second]: Include hydraulic sample results where flow at top of borehole section is equal to or greater than this                                                                    |           | &check;                                                                                               |
| maxtopflow           | Float [m^3 per second]: Include hydraulic sample results where flow at top of borehole section is equal to or less than this                                                                       |           | &check;                                                                                               |
| minbottompressure    | Float [Pascal]: Include hydraulic sample results where pressure at bottom of borehole section is equal to or greater than this                                                                     |           | &check;                                                                                               |
| maxbottompressure    | Float [Pascal]: Include hydraulic sample results where pressure at bottom of borehole section is equal to or less than thi                                                                         |           | &check;                                                                                               |
| mintoppressure       | Float [Pascal]: Include hydraulic sample results where pressure at top of borehole section is equal to or greater than this                                                                        |           | &check;                                                                                               |
| maxtoppressure       | Float [Pascal]: Include hydraulic sample results where pressure at top of borehole section is equal to or less than this                                                                           |           | &check;                                                                                               |
| minfluiddensity      | Float [kg per m^3]: Include hydraulic sample results where fluid density in borehole section is equal to or greater than this                                                                      |           | &check;                                                                                               |
| maxfluiddensity      | Float [kg per m^3]: Include hydraulic sample results where fluid density in borehole section is equal to or less than this                                                                         |           | &check;                                                                                               |
| minfluidviscosity    | Float [Centipoise]: Include hydraulic sample results where fluid viscosity in borehole section is equal to or greater than this                                                                    |           | &check;                                                                                               |
| maxfluidviscosity    | Float [Centipoise]: Include hydraulic sample results where fluid viscosity in borehole section is equal to or less than this                                                                       |           | &check;                                                                                               |
| minfluidph           | Float: [pH] Include hydraulic sample results where fluid ph in borehole section is equal to or greater than this                                                                                   |           | &check;                                                                                               |
| maxfluidph           | Float [pH]: Include hydraulic sample results where fluid ph in borehole section is equal to or less than this                                                                                      |           | &check;                                                                                               |
| limit                | Integer: Limit on hydraulic samples                                                                                                                                                                |           | &check;                                                                                               |
| offset               | Integer: Offset on hydraulics samples                                                                                                                                                              |           | &check;                                                                                               |
| mincasingdiameter    | Float [Meter]: Include borehole sections results where casing diameter in borehole section is equal to or greater than this                                                                        | &check;   | &check;                                                                                               |
| maxcasingdiameter    | Float [Meter]: Include borehole sections results where casing diameter in borehole section is equal to or less than this                                                                           | &check;   | &check;                                                                                               |
| minholediameter      | Float [Meter]: Include borehole sections results where hole diameter in borehole section is equal to or greater than this                                                                          | &check;   | &check;                                                                                               |
| maxholediameter      | Float [Meter]: Include borehole sections results where hole diameter in borehole section is equal to or less than this                                                                             | &check;   | &check;                                                                                               |
| mintopdepth          | Float [Meter]: Include borehole section results where depth of the top of borehole section is equal to or greater than this                                                                        | &check;   | &check;                                                                                               |
| maxtopdepth          | Float [Meter]: Include borehole section results where depth of the top of borehole section is equal to or less than this                                                                           | &check;   | &check;                                                                                               |
| minbottomdepth       | Float [Meter]: Include borehole section results where depth of the bottom of borehole section is equal to or greater than this                                                                     | &check;   | &check;                                                                                               |
| maxbottomdepth       | Float [Meter]: Include borehole section results where depth of the bottom of borehole section is equal to or less than this                                                                        | &check;   | &check;                                                                                               |
| topclosed            | Boolean: Include borehole section results which equal topclosed                                                                                                                                    | &check;   | &check;                                                                                               |
| bottomclosed         | Boolean: Include borehole sections result which equal bottomclosed                                                                                                                                 | &check;   | &check;                                                                                               |
| casingtype           | String: Include borehole sections result which equal casingtype exactly                                                                                                                            | &check;   | &check;                                                                                               |
| sectiontype          | String: Include borehole sections result which equal sectiontype exactly                                                                                                                           | &check;   | &check;                                                                                               |

Response:

    {
      "publicid": "id:borehole_20190925T091320389843",
      "longitude": {
        "value": -21.807
      },
      "latitude": {
        "value": 64.1735
      },
      "altitude": {
        "value": 20
      },
      "depth": {
        "value": 1832
      },
      "sections": [
        {
          "publicid": "id:boreholesection_192509T091320.389843",
          "starttime": "2001-12-31T00:00:00",
          "toplongitude": {
            "value": -21.8025
          },
          "bottomlongitude": {
            "value": -21.8008
          },
          "toplatitude": {
            "value": 64.1765
          },
          "bottomlatitude": {
            "value": 64.18
          },
          "topdepth": {
            "value": 908
          },
          "bottomdepth": {
            "value": 1832
          },
          "holediameter": {
            "value": 0.216
          },
          "casingdiameter": {
            "value": 0.225
          },
          "topclosed": false,
          "bottomclosed": false,
          "hydraulics": [
            {
              "datetime": {
                "value": "2019-10-05T01:00:00"
              },
              "topflow": {
                "value": 0.021
              }
            },
            {
              "datetime": {
                "value": "2019-10-05T02:00:00"
              },
              "topflow": {
                "value": 0.009
              }
            },
            {
              "datetime": {
                "value": "2019-10-05T02:59:00"
              },
              "topflow": {
                "value": 0.021
              }
            }
          ]
        }
      ]
    }

#### GET /hydws/v1/boreholes/:borehole_id/sections/:section_id/hydraulics

Get hydraulic data for specific base64 encoded `borehole_id` and `section_id`.

Parameters:

    * starttime: Boreholes returned if any borehole section has a starttime that falls within the section epoch time. Format: YYYY-MM-DD[THH:MM:SS] (UTC)
    * endtime: Boreholes returned if any borehole section has a endtime that falls within the section epoch time. Format: YYYY-MM-DD[THH:MM:SS] (UTC)
    * mincasingdiameter: Include borehole sections results where casing diameter in borehole section is equal to or greater than this.  Units: m
    * maxcasingdiameter: Include borehole sections results where casing diameter in borehole section is equal to or less than this.  Units: m
    * minholediameter: Include borehole sections results where hole diameter in borehole section is equal to or greater than this.  Units: m
    * maxholediameter: Include borehole sections results where hole diameter in borehole section is equal to or less than this.  Units: m
    * mintopdepth: Include borehole section results where depth of the top of borehole section is equal to or greater than this. Units: m
    * maxtopdepth: Include borehole section results where depth of the top of borehole section is equal to or less than this. Units: m
    * minbottomdepth: Include borehole section results where depth of the bottom of borehole section is equal to or greater than this. Units: m
    * maxbottomdepth: Include borehole section results where depth of the bottom of borehole section is equal to or less than this. Units: m
    * topclosed: Include borehole section results which equal topclosed [`true` | `false`]
    * bottomclosed: Include borehole sections result which equal bottomclosed [`true` | `false`]
    * casingtype: Include borehole sections result which equal `casingtype` exactly
    * sectiontype: Include borehole sections result which equal `sectiontype` exactly

Response:

    [
      {
        "datetime": {
          "value": "2019-10-04T08:00:00"
        },
        "topclosed": {
          "value": false
        },
        "bottomclosed": {
          "value": true
        },
        "topflow": {
          "value": 0
        },
        "holediameter": {
          "value": 0.3
        },
        "topdepth": {
          "value": 1100
        },
        "bottomdepth": {
          "value": 1200
        },
        "casingdiameter": {
          "value": 0.35
        },
        "sectiontype": {
          "value": "section_type_a"
        },
        "casingtype": {
          "value": "casing_type_a"
        },
      {
        "datetime": {
          "value": "2019-10-04T08:01:00"
        },
        "topclosed": {
          "value": false
        },
        "bottomclosed": {
          "value": true
        },
        "topflow": {
          "value": 0
        },
        "holediameter": {
          "value": 0.3
        },
        "topdepth": {
          "value": 1100
        },
        "bottomdepth": {
          "value": 1200
        },
        "casingdiameter": {
          "value": 0.35
        },
        "sectiontype": {
          "value": "section_type_a"
        },
        "casingtype": {
          "value": "casing_type_a"
        }
      }
    ]
>>>>>>> feat: add Readme and License
