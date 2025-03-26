import asyncio
import logging
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager

from backend.app.db.database import get_db
from backend.app.services.AsyncRunner import run_listener, message_handler
from backend.app.api.locations import router as locations_router
from backend.app.core.logging import setup_logging

logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    listener_task = asyncio.create_task(run_listener())
    handler_task = asyncio.create_task(message_handler())

    logger.info("Background tasks started")

    yield

    logger.info("Shutting down background tasks")
    if not listener_task.done():
        listener_task.cancel()
    if not handler_task.done():
        handler_task.cancel()

    try:
        await listener_task
    except asyncio.CancelledError:
        pass
    try:
        await handler_task
    except asyncio.CancelledError:
        pass

    logger.info("Background tasks shut down")


app = FastAPI(lifespan=lifespan)

app.include_router(locations_router)


@app.get("/")
async def root():
    return {"message": "Antiradar API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
