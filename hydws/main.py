# import logging

from fastapi import FastAPI
# from fastapi.logger import logger as fastapi_logger
from fastapi.middleware.cors import CORSMiddleware

from hydws.datamodel.base import ORMBase, engine
from hydws.routers.v1 import boreholes

# gunicorn_error_logger = logging.getLogger("gunicorn.error")
# gunicorn_logger = logging.getLogger("gunicorn")
# uvicorn_access_logger = logging.getLogger("uvicorn.access")
# uvicorn_access_logger.handlers = gunicorn_error_logger.handlers

# fastapi_logger.handlers = gunicorn_error_logger.handlers

# if __name__ != "__main__":
#     fastapi_logger.setLevel(gunicorn_logger.level)
# else:
#     fastapi_logger.setLevel(logging.DEBUG)

ORMBase.metadata.create_all(bind=engine)

app = FastAPI(
    docs_url="/hydws/docs",
    redoc_url=None,
    openapi_url="/hydws/openapi.json")
app.include_router(boreholes.router, prefix='/hydws/v1')


origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:5000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex='http.*://.*\\.ethz\\.ch',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
