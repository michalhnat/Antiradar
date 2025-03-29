import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db import models
from backend.app.db.database_handler import DatabaseHandler

from backend.app.db.database import get_db_async

router = APIRouter()
logger = logging.getLogger(__name__)

db_handler_instance = DatabaseHandler()


@router.get("/locations", response_model=List[models.LocationPydantic])
def get_all_locations_api(
    db: Session = Depends(get_db_async),
):
    try:
        logger.info("API endpoint /locations called.")
        locations = db_handler_instance.get_all_locations(db=db)
        logger.info(
            "Successfully retrieved %d locations via API.", len(locations)
        )
        return locations
    except Exception as e:
        logger.error("API error fetching locations: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error retrieving locations",
        )
