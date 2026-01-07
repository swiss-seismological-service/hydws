from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from config import get_settings
from hydws.database import sessionmanager
from hydws.routers import boreholes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
    yield

    if sessionmanager._engine is not None:
        await sessionmanager.close()

app = FastAPI(
    docs_url="/hydws/docs",
    lifespan=lifespan,
    redoc_url=None,
    openapi_url="/hydws/openapi.json")

app.include_router(boreholes.router, prefix='/hydws/v1')


app = CORSMiddleware(
    app=app,
    allow_origins=get_settings().ALLOW_ORIGINS,
    allow_origin_regex=get_settings().ALLOW_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)
