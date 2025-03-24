from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.services.elasticsearch import (
    init_indices,
    get_es_instance,
    wait_for_elasticsearch,
)
from app.services.minio_api import init_minio_bucket
from app.routers import current, children, parent

es = get_es_instance()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if not await wait_for_elasticsearch(es):
        raise Exception("Elasticsearch is not available after waiting")

    await init_indices(es)

    init_minio_bucket()

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(current.router)
app.include_router(children.router)
app.include_router(parent.router)
