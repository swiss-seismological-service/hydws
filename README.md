[![codecov](https://codecov.io/gh/swiss-seismological-service/hydws/graph/badge.svg?token=7B7LXOZ3CV)](https://codecov.io/gh/swiss-seismological-service/hydws)
[![test](https://github.com/swiss-seismological-service/hydws/actions/workflows/tests.yml/badge.svg)](https://github.com/swiss-seismological-service/hydws/actions/workflows/tests.yml)

# hydws

REST webservice allowing access to hydraulic data.

Instructions for installation and examples of usage may be found below.

## Quickly Accessing Data

If you are using Python, use the [hydws-client](https://gitlab.seismo.ethz.ch/indu/hydws-client) library to access the data. Alternatively you can simply request the data directly (eg. curl or browser). The resulting data is accessed per default in JSON format, **hydraulics data of a single section can also be accessed in CSV format.**

Use the following example to get started quickly using curl or a simple web browser:

1. Navigate to /hydws/v1/boreholes and copy the `publicid` of the `borehole`, and the `section` you are interested in.
2. Navigating to /hydws/v1/boreholes/`borehole_publicid`/section/`section_publicid`/hydraulics would return ALL the hydraulic data for that section.
3. Navigating to /hydws/v1/boreholes/`borehole_publicid`/section/`section_publicid`/hydraulics?starttime=2021-01-01T00:00:00&endtime=2021-01-02T00:00:00 would return the hydraulic data for that section between the specified times.
4. Adding `&format=csv` to the end of the URL returns the data in CSV format.

## Installation

Using [Docker](https://docs.docker.com/engine/) allows for an easy setup of the webservice, the database and the required dependencies. Manual installation is also possible, but requires some manual steps to prepare the database.

**Configuration**:

Before building and running the container, copy the file `.env.example` to `.env` and
adjust the variables defined within according to your needs. Make sure to pick a proper
username and password for the internally used PostgreSQL database and write
these down for later.

**Deployment**:

The container should be run using the provided `docker-compose.yml`
configuration file. For local development please replace the
`image: ${TAG_COMMIT}` option with `build: .`

Then you can just run:

```
$ docker-compose up -d
```

# HYDWS REST API

## Introduction

HYDWS provides a REST API interface for serving borehole hydraulic sample data. This document specifies the URLs, query parameters and expected results. An OpenAPI specification is also available by navigating to the `/hydws/docs` endpoint on a running instance.

## Response

All responses are primarily in JSON. The response will reflect the hierarchical one to many relationship between borehole and borehole sections, and between borehole section and hydraulic samples.
Both borehole and borehole section have a unique publicid which is required to make calls which specifies the borehole and/or borehole section. This publicid needs to be a valid `UUID4` string.

The standard HTTP response status codes are used.

### GET /hydws/v1/boreholes

List the available boreholes with their sections.

Parameters:
_ starttime: Boreholes returned if any borehole section has a starttime that falls within the section epoch time. format: YYYY-MM-DDTHH:MM:SS (UTC)  
 _ endtime: Boreholes returned if any borehole section has a endtime that falls within the section epoch time. format: YYYY-MM-DDTHH:MM:SS (UTC)  
 _ minlatitude: Boreholes returned where borehole (mouth) latitude is equal to or greater than this value. Unit: Degrees  
 _ minlongitude: Boreholes returned where borehole (mouth) longitude is equal to or greater than this value. Unit: Degrees  
 _ maxlatitude: Boreholes returned where borehole (mouth) latitude is equal to or less than this value. Unit: Degrees  
 _ maxlongitude: Boreholes returned where borehole (mouth) longitude is equal to or less than this value. Unit: Degrees

Response:

```json
[
  {
    "publicid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "description": "string",
    "name": "string",
    "location": "string",
    "institution": "string",
    "measureddepth": { "value": 0 },
    "bedrockaltitude": { "value": 0 },
    "altitude": { "value": 0 },
    "latitude": { "value": 0 },
    "longitude": { "value": 0 },
    "creationinfo": {
      "author": "string",
      "agencyid": "string",
      "creationtime": "2024-04-16T09:50:37.076Z",
      "version": "string",
      "copyrightowner": "string",
      "licence": "string"
    },
    "sections": [
      {
        "publicid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "starttime": "2024-04-16T09:50:37.075Z",
        "endtime": "2024-04-16T09:50:37.075Z",
        "topclosed": true,
        "bottomclosed": true,
        "sectiontype": "string",
        "casingtype": "string",
        "description": "string",
        "name": "string",
        "hydraulics": [],
        "casingdiameter": { "value": 0 },
        "holediameter": { "value": 0 },
        "bottommeasureddepth": { "value": 0 },
        "topmeasureddepth": { "value": 0 },
        "bottomaltitude": { "value": 0 },
        "bottomlatitude": { "value": 0 },
        "bottomlongitude": { "value": 0 },
        "topaltitude": { "value": 0 },
        "toplatitude": { "value": 0 },
        "toplongitude": { "value": 0 }
      }
    ]
  }
]
```

### GET /hydws/v1/boreholes/:borehole_id

Return results of borehole section with optional hydraulic results for the given `borehole_id` which is a UUID.

Parameters:

    * level: level of output results. [`borehole` | `section` | `hydraulic`] #default: section
    * starttime: Boreholes returned if any borehole section has a starttime that falls within the section epoch time. format: YYYY-MM-DDTHH:MM:SS (UTC)
    * endtime: Boreholes returned if any borehole section has a endtime that falls within the section epoch time. format: YYYY-MM-DDTHH:MM:SS (UTC)

Response:

```json
{
  "publicid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "description": "string",
  "name": "string",
  "location": "string",
  "institution": "string",
  "measureddepth": { "value": 0 },
  "bedrockaltitude": { "value": 0 },
  "altitude": { "value": 0 },
  "latitude": { "value": 0 },
  "longitude": { "value": 0 },
  "creationinfo": {
    "author": "string",
    "agencyid": "string",
    "creationtime": "2024-04-16T09:50:37.076Z",
    "version": "string",
    "copyrightowner": "string",
    "licence": "string"
  },
  "sections": [
    {
      "publicid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "starttime": "2024-04-16T09:50:37.075Z",
      "endtime": "2024-04-16T09:50:37.075Z",
      "topclosed": true,
      "bottomclosed": true,
      "sectiontype": "string",
      "casingtype": "string",
      "description": "string",
      "name": "string",
      "casingdiameter": { "value": 0 },
      "holediameter": { "value": 0 },
      "bottommeasureddepth": { "value": 0 },
      "topmeasureddepth": { "value": 0 },
      "bottomaltitude": { "value": 0 },
      "bottomlatitude": { "value": 0 },
      "bottomlongitude": { "value": 0 },
      "topaltitude": { "value": 0 },
      "toplatitude": { "value": 0 },
      "toplongitude": { "value": 0 },
      "hydraulics": [
        {
          "fluidcomposition": "string",
          "fluidph": { "value": 0 },
          "fluidviscosity": { "value": 0 },
          "fluiddensity": { "value": 0 },
          "toppressure": { "value": 0 },
          "topflow": { "value": 0 },
          "toptemperature": { "value": 0 },
          "bottompressure": { "value": 0 },
          "bottomflow": { "value": 0 },
          "bottomtemperature": { "value": 0 },
          "datetime": { "value": "2024-04:50:37.076Z" }
        }
      ]
    }
  ]
}
```

#### GET /hydws/v1/boreholes/:borehole_id/sections/:section_id/hydraulics

Get hydraulic data for specific `borehole_id` and `section_id`, both of which are UUID's.

Parameters:
_ starttime: Returns HydraulicSamples which have a datetime value larger than this parameter. Format: YYYY-MM-DDTHH:MM:SS (UTC)  
 _ endtime: Returns HydraulicSamples which have a datetime value smaller than this parameter. Format: YYYY-MM-DDTHH:MM:SS (UTC)  
 \* format: Format of the output. [`json` | `csv`] #default: json  
Response:

```json
[
  {
    "fluidcomposition": "string",
    "fluidph": {
      "value": 0,
      "uncertainty": 0,
      "loweruncertainty": 0,
      "upperuncertainty": 0,
      "confidencelevel": 0
    },
    "fluidviscosity": {
      "value": 0,
      "uncertainty": 0,
      "loweruncertainty": 0,
      "upperuncertainty": 0,
      "confidencelevel": 0
    },
    "fluiddensity": {
      "value": 0,
      "uncertainty": 0,
      "loweruncertainty": 0,
      "upperuncertainty": 0,
      "confidencelevel": 0
    },
    "toppressure": {
      "value": 0,
      "uncertainty": 0,
      "loweruncertainty": 0,
      "upperuncertainty": 0,
      "confidencelevel": 0
    },
    "topflow": {
      "value": 0,
      "uncertainty": 0,
      "loweruncertainty": 0,
      "upperuncertainty": 0,
      "confidencelevel": 0
    },
    "toptemperature": {
      "value": 0,
      "uncertainty": 0,
      "loweruncertainty": 0,
      "upperuncertainty": 0,
      "confidencelevel": 0
    },
    "bottompressure": {
      "value": 0,
      "uncertainty": 0,
      "loweruncertainty": 0,
      "upperuncertainty": 0,
      "confidencelevel": 0
    },
    "bottomflow": {
      "value": 0,
      "uncertainty": 0,
      "loweruncertainty": 0,
      "upperuncertainty": 0,
      "confidencelevel": 0
    },
    "bottomtemperature": {
      "value": 0,
      "uncertainty": 0,
      "loweruncertainty": 0,
      "upperuncertainty": 0,
      "confidencelevel": 0
    },
    "datetime": {
      "value": "2024-04-16T09:50:37.076Z",
      "uncertainty": 0,
      "loweruncertainty": 0,
      "upperuncertainty": 0,
      "confidencelevel": 0
    },
    "additionalProp1": {}
  }
]
```

### POST /hydws/v1/boreholes

Post data to be saved in the database. The data should be of the same json format as is output by the webservice.
Example using curl to upload a file:

`curl -i -X POST -H "Content-Type: application/json" --data @/absolute_path_to_file/borehole_file.json "localhost:8080/hydws/v1/boreholes"`

Where localhost would be changed to the name of the machine that the service is running on.

A file may contain more than one borehole, as a comma seperated list using square parentheses.

#### Hydraulic Merges vs Overwrites

Borehole and Section metadata will always be merged with existing data. Keys have to be explicitly overwritten by the user if they are to be updated or removed.

Hydraulic data will per default overwrite all existing data for the same BoreholeSection and period. Meaning that if the new hydraulic data contains samples for eg. 1 Week, **all** the existing data for that week will be deleted and replaced with the new data. This is also the case if the existing data contains a different kind of measurements (eg. flow vs pressure data).

It is possible, to explicitly merge merge different kinds of measurements by passing the `merge=True` query parameter with the POST request. POSTing eg. Flow data with `merge=True` will overwrite all existing flow data, but keep the existing pressure data for the same period.

The challenge with this approach is, that the timestamps don't have to match exactly and/or the sample frequency can be different. The additional parameter `merge_limit` can be used to control the behaviour in this situation. By default, the merge limit is 60s. This means, that all measurements of the same kind, are considered to be continous if their timestamps are within 60s of each other.

The merge strategy explained with an example: (see below for accompanying data example)  
`toppressure_value` is recorded with one measurement every 60s, `topflow_value` measurements for the same timespan are merged into this existing dataset, but are recorded at 30s intervals. If the merge limit is set to 60s, the `toppressure` measurements are considered to be continous (<=60s) and will be upsampled to match the 30s interval of the `topflow` measurements (by forward filling). If the merge limit is set to 30s, the toppressure measurements will be considered to have gaps and will be kept as is, resulting in every 2nd `HydraulicSample` (row entry) not containing a `toppressure_value`.

Careful though: In the example above, the `toppressure` measurements are upsampled to match the `topflow` measurements. This means that their value will be inserted into the new rows created by `topflow`. If the timestamps are not aligned though, then the `toppressure` entries will still have their own samples, and the inverse happens also (since topflow is also considered continuous at 30s intervals). In this case the resulting number of rows will not be twice the number as before (since the sampling rate is twice as high), but will be 3 time the number of rows as before.

```
datetime,             toppressure
2021-01-01 00:00:00   1
2021-01-01 00:01:00   2
2021-01-01 00:02:00   3

datetime,             topflow
2021-01-01 00:00:00   10
2021-01-01 00:00:30   20
2021-01-01 00:01:00   30
2021-01-01 00:01:30   40
2021-01-01 00:02:00   50
```

results in:

```
datetime,             toppressure  topflow
2021-01-01 00:00:00   1            10
2021-01-01 00:00:30   1            20
2021-01-01 00:01:00   2            30
2021-01-01 00:01:30   2            40
2021-01-01 00:02:00   3            50
```

but merging topflow values which dont align:

```
datetime,             topflow
2021-01-01 00:00:15   10
2021-01-01 00:00:45   20
2021-01-01 00:01:15   30
2021-01-01 00:01:45   40
2021-01-01 00:02:15   50
```

Results in three times the number of rows

```
datetime,             toppressure  topflow
2021-01-01 00:00:00   1
2021-01-01 00:00:15   1            10
2021-01-01 00:00:30   1            10
2021-01-01 00:00:45   1            20
2021-01-01 00:01:00   2            20
2021-01-01 00:01:15   2            30
2021-01-01 00:01:30   2            30
2021-01-01 00:01:45   2            40
2021-01-01 00:02:00   3            40
2021-01-01 00:02:15                50
```
