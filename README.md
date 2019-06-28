# hydws

REST webservice allowing access to hydraulic data.

## Installation

The installation of the package is possible by means of invoking

```
pip install -e .
```

This will create sym links to the python entry points 'hydws-db-init' and
'hydws-test'.

Note, that encapsulating the installation by means of a [virtual
environment](https://docs.python.org/3/tutorial/venv.html) is strongly
recommended.

## Initialize HYDWS
```
hydws-db-init <db_url>
```
Run the above command. To be run locally with a sqlite db,
db_url=`sqlite:///<absolute_path>/<name_db_file>`

The database now contains tables ready for population.

## Setup with Docker

A basic knowledge about [Docker](https://docs.docker.com/engine/) and how
this kind of application containers work is required. For more information
about operating system support (which includes Linux, macOS and specific
versions of Windows) and on how to install Docker, please refer to the official
[Docker website](https://www.docker.com/products/docker).

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
$ cd docker
```

**Configuration**:

Before building and running the container adjust the variables defined within
`.env` configuration file according to your needs. Make sure to pick a proper
username and password for the internally used PostgreSQL database and write
these down for later.

**Building**:

Once you environment variables are configured you are ready to build the
container image.

```
$ docker build -t hydws:1.0 .
```

**Compose Configuration**:

In case you want to manage your own volumes now is the time. The configuration
provided relies on named docker volumes.

**Deployment**:

The container should be run using the provided `docker-compose.yml`
configuration file.

```
$ docker-compose up -d
```

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


## Test local installation

The following command should not be used for production, but instead for
testing.

A sqlite database file exists already populated with data: db_url =
`sqlite:///<path to repo>/hydws/server/v1/data/test.db`

```
hydws-test --logging-conf <path_to_logging.conf> <db_url>
```
where logging.conf exists in the repository. By default the port used is 5000.

Testing examples can be found in the Postman test collection.

The full selection of hydws-test parameters can be found with:
```
hydws-test -h
```

## API usage

The full specification for the HYDWS API can be found here: <link to spec>

Some examples demonstrate the usage with the data using db_url=test.db


To return an array of JSON objects representing boreholes:

```
$ curl "http://localhost:5000/v1/boreholes?&level=borehole"

```

To return a JSON object representing a borehole with all borehole sections and
all hydraulics:

```
$ curl "http://localhost:5000/v1/boreholes/c21pOmNoLmV0aHouc2VkL2JoLzExMTExMTExLWU0YTAtNDY5Mi1iZjI5LTMzYjU1OTFlYjc5OA==?level=hydraulic"

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
$ curl "http://localhost:5000/v1/boreholes/c21pOmNoLmV0aHouc2VkL2JoLzExMTExMTExLWU0YTAtNDY5Mi1iZjI5LTMzYjU1OTFlYjc5OA==/sections/c21pOmNoLmV0aHouc2VkL2JoL3NlY3Rpb24vMTExMTExMTEtOGQ4OS00ZjEzLTk1ZTctNTI2YWRlNzNjYzhi/hydraulics?"
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


