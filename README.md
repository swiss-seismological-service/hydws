[![pipeline status](https://gitlab.seismo.ethz.ch/indu/hydws/badges/main/pipeline.svg)](https://gitlab.seismo.ethz.ch/indu/hydws/-/commits/main) [![coverage report](https://gitlab.seismo.ethz.ch/indu/hydws/badges/main/coverage.svg)](https://gitlab.seismo.ethz.ch/indu/hydws/-/commits/main)

# hydws

REST webservice allowing access to hydraulic data.

Instructions for installation and examples of usage may be found below.

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
    * starttime: Boreholes returned if any borehole section has a starttime that falls within the section epoch time. format: YYYY-MM-DDTHH:MM:SS (UTC)  
    * endtime: Boreholes returned if any borehole section has a endtime that falls within the section epoch time. format: YYYY-MM-DDTHH:MM:SS (UTC)  
    * minlatitude: Boreholes returned where borehole (mouth) latitude is equal to or greater than this value. Unit: Degrees  
    * minlongitude: Boreholes returned where borehole (mouth) longitude is equal to or greater than this value. Unit: Degrees  
    * maxlatitude: Boreholes returned where borehole (mouth) latitude is equal to or less than this value. Unit: Degrees  
    * maxlongitude: Boreholes returned where borehole (mouth) longitude is equal to or less than this value. Unit: Degrees  

Response:
```json
[  
    {  
        "publicid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",  
        "description": "string",  
        "name": "string",  
        "location": "string",  
        "institution": "string",  
        "measureddepth": {"value": 0},  
        "bedrockaltitude": {"value": 0},  
        "altitude": {"value": 0},  
        "latitude": {"value": 0},  
        "longitude": {"value": 0},  
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
                "casingdiameter": {"value": 0},  
                "holediameter": {"value": 0},  
                "bottommeasureddepth": {"value": 0},  
                "topmeasureddepth": {"value": 0},  
                "bottomaltitude": {"value": 0},  
                "bottomlatitude": {"value": 0},  
                "bottomlongitude": {"value": 0},  
                "topaltitude": {"value": 0},  
                "toplatitude": {"value": 0},  
                "toplongitude": {"value": 0 }  
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
    "measureddepth": {"value": 0},
    "bedrockaltitude": {"value": 0},
    "altitude": {"value": 0},
    "latitude": {"value": 0},
    "longitude": {"value": 0},
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
            "casingdiameter": {"value": 0},
            "holediameter": {"value": 0},
            "bottommeasureddepth": {"value": 0},
            "topmeasureddepth": {"value": 0},
            "bottomaltitude": {"value": 0},
            "bottomlatitude": {"value": 0},
            "bottomlongitude": {"value": 0},
            "topaltitude": {"value": 0},
            "toplatitude": {"value": 0},
            "toplongitude": {"value": 0},
            "hydraulics": [
                {
                    "fluidcomposition": "string",
                    "fluidph": {"value": 0},
                    "fluidviscosity": {"value": 0},
                    "fluiddensity": {"value": 0},
                    "toppressure": {"value": 0},
                    "topflow": {"value": 0},
                    "toptemperature": {"value": 0},
                    "bottompressure": {"value": 0},
                    "bottomflow": {"value": 0},
                    "bottomtemperature": {"value": 0},
                    "datetime": {"value": "2024-04:50:37.076Z"}
                }
            ]
        }
    ]
}
```

#### GET /hydws/v1/boreholes/:borehole_id/sections/:section_id/hydraulics

Get hydraulic data for specific `borehole_id` and `section_id`, both of which are UUID's.

Parameters:
    * starttime: Returns HydraulicSamples which have a datetime value larger than this parameter. Format: YYYY-MM-DDTHH:MM:SS (UTC)  
    * endtime: Returns HydraulicSamples which have a datetime value smaller than this parameter. Format: YYYY-MM-DDTHH:MM:SS (UTC)  
    * format: Format of the output. [`json` | `csv`] #default: json  
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
