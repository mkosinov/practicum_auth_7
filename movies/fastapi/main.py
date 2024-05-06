from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.v1 import films, genres, persons
from core.config import settings
from core.logger import logger
from db import elastic, redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Определение логики работы (запуска и остановки) приложения."""
    # Логика при запуске приложения.
    redis.redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    elastic.es = AsyncElasticsearch(
        hosts=[f"{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}"]
    )
    logger.info("Приложение запущено")
    yield
    # Логика при завершении приложения.
    await redis.redis.close()
    await elastic.es.close()
    logger.info("Приложение остановлено")


app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url=settings.OPEN_API_DOCS_URL,
    openapi_url=settings.OPENAPI_URL,
    default_response_class=ORJSONResponse,
)

app.include_router(
    films.router, prefix="/api/v1/films", tags=["Кинопроизведения"]
)
app.include_router(persons.router, prefix="/api/v1/persons", tags=["Персоны"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["Жанры"])