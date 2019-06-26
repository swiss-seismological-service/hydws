# hydws

REST webservice allowing access to hydraulic data.

## Installation

The installation of the package is possible by means of invoking

```
pip install -e .
```

This will create sym links to the python entry points 'hydws-db-init' and 'hydws-test'.

Note, that encapsulating the installation by means of a [virtual
environment](https://docs.python.org/3/tutorial/venv.html) is strongly
recommended.

## Initialize HYDWS
```
hydws-db-init <db_url>
```
Run the above command. To be run locally with a sqlite db, db_url=sqlite:///<absolute_path>/<name_db_file>

The database now contains tables ready for population.

## Setup with Docker

<Docker setup here>

## Test local installation

The following command should not be used for production, but instead for testing.

A sqlite database file exists already populated with data:
db_url = sqlite:///<path to repo>/hydws/server/v1/data/test.db

```
hydws-test --logging-conf <path_to_logging.conf> <db_url>
```
where logging.conf exists in the repository. By default the port used is 5000.

Testing examples can be found with the Postman test collection.

## API usage

The full specification for the HYDWS API can be found here: <link to spec>

Some examples demonstrate the usage with the data using db_url=test.db


To return an array of JSON objects representing boreholes:

```
curl "http://localhost:5000/v1/boreholes?&level=borehole"

```

To return a JSON object representing a borehole with all borehole sections and all hydraulics:

```
curl "http://localhost:5000/v1/boreholes/c21pOmNoLmV0aHouc2VkL2JoLzExMTExMTExLWU0YTAtNDY5Mi1iZjI5LTMzYjU1OTFlYjc5OA==?level=hydraulic"

```
Note: the borehole publicid: c21pOmNoLmV0... is encoded with base64. This is decoded within the application.
The command to encode/decode strings with python can be found below:
```
import base64
encoded borehole publicid = base64.b64encode(b'<borehole publicid>')
decoded borehole publicid = base64.b64decode(b'<encoded borehole publicid>')
```

To return a JSON array of all hydraulics from a specific borehole and specific section:
```
curl "http://localhost:5000/v1/boreholes/c21pOmNoLmV0aHouc2VkL2JoLzExMTExMTExLWU0YTAtNDY5Mi1iZjI5LTMzYjU1OTFlYjc5OA==/sections/c21pOmNoLmV0aHouc2VkL2JoL3NlY3Rpb24vMTExMTExMTEtOGQ4OS00ZjEzLTk1ZTctNTI2YWRlNzNjYzhi/hydraulics?"
```

Note: Both the borehole publicid and section publicid are base64 encoded as noted above.

### API call response body

The response body will be JSON, or an array of JSON objects.


### Postman tests

Postman is an API development and testing tool. A collection of tests has been created for HYDWS. To run the tests, follow the instructions to initialize and run a local instance.
The button below can be pressed to run the tests:

[![Run in Postman](https://run.pstmn.io/button.svg)](https://app.getpostman.com/run-collection/3da8e474b7ecf5b8e1e0)



## Unit tests

Unit tests can be run from the top level of the repository using the pytest command. 

