from fastapi import APIRouter, FastAPI

from src.api.sync import router as sync_router
from src.api.health import router as health_router
from src.core.lifespan import lifespan
from src.core import logging as logging_config

logging_config.setup_logging()

app = FastAPI(lifespan=lifespan)

api_router = APIRouter(prefix="/api")

api_router.include_router(sync_router)
api_router.include_router(health_router)

app.include_router(api_router)
