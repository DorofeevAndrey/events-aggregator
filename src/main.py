from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.api.events import router as events_router
from src.api.health import router as health_router
from src.api.sync import router as sync_router
from src.api.tickets import router as tickets_router
from src.core import logging as logging_config
from src.core.lifespan import lifespan

logging_config.setup_logging()

app = FastAPI(lifespan=lifespan)


# FastApi not recomented, just for tests on lms
@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(status_code=400, content={"detail": exc.errors()})


api_router = APIRouter(prefix="/api")

api_router.include_router(health_router)
api_router.include_router(sync_router)

api_router.include_router(events_router)
api_router.include_router(tickets_router)

app.include_router(api_router)
