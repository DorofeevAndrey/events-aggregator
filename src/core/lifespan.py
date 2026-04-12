import asyncio
from contextlib import asynccontextmanager

from src.tasks.sync_events import background_sync


@asynccontextmanager
async def lifespan(app):
    task = asyncio.create_task(background_sync())

    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
