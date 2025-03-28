import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from backend.app.api.locations import router as locations_router
from backend.app.core.logging import setup_logging
from backend.app.db.database import get_db_async
from backend.app.services.async_runner import message_handler, run_listener

# from backend.app.db.database import init_db
from backend.app.services.async_runner import main

logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # init_db()
    main_task = asyncio.create_task(main())

    logger.info("Application initialized, database ready")

    yield

    logger.info("Shutting down background tasks")
    if not main_task.done():
        main_task.cancel()

    try:
        await main_task
    except asyncio.CancelledError:
        logger.info("Main task was cancelled")

    logger.info("Application shutdown complete")


app = FastAPI(lifespan=lifespan)

app.include_router(locations_router)


@app.get("/")
async def root():
    return {"message": "Antiradar API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
