from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from hydws.datamodel.base import ORMBase, engine

from hydws.routers import boreholes


ORMBase.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(boreholes.router, prefix='/v1')


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
