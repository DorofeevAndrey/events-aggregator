from fastapi import FastAPI
from fastapi.params import Depends
from sqlalchemy import literal, select

from src.db.session import get_db_session

app = FastAPI()


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/health/db")
async def health_db(session=Depends(get_db_session)):
    await session.execute(select(literal(1)))
    return {"status": "ok"}
