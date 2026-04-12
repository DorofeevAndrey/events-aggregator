from fastapi import FastAPI, APIRouter
from src.api.sync import router as sync_router

app = FastAPI()

api_router = APIRouter(prefix="/api")


@api_router.get("/health")
async def health():
    return {"status": "ok"}


api_router.include_router(sync_router)

app.include_router(api_router)
