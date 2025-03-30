import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.utils.converter import string_to_datetime

from backend.app.db import models
from backend.app.db.database import get_db_async
from backend.app.db.database_handler import DatabaseHandler

router = APIRouter()
logger = logging.getLogger(__name__)

db_handler_instance = DatabaseHandler()


@router.get(
    "/locations/query/all", response_model=List[models.LocationPydantic]
)
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


@router.get(
    "/locations/query/last_hours/{x_hours}",
    response_model=List[models.LocationPydantic],
)
def get_all_locations_in_last_x_hours_api(
    x_hours: int,
    db: Session = Depends(get_db_async),
):
    try:
        logger.info("API endpoint /locations/%d called.", x_hours)
        locations = db_handler_instance.get_all_locations_in_last_x_hours(
            db=db, x_hours=x_hours
        )
        if not locations:
            logger.warning("No locations found in the last %d hours.", x_hours)
            raise HTTPException(status_code=404, detail="No locations found")
        logger.info(
            "Successfully retrieved %d locations via API.", len(locations)
        )
        return locations
    except HTTPException as e:
        logger.error("HTTP error: %s", e.detail)
        raise e
    except Exception as e:
        logger.error("API error fetching locations: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error retrieving locations",
        )


@router.get(
    "/locations/query/since/{datetime_str}",
    response_model=List[models.LocationPydantic],
)
def get_location_since_datetime_api(
    datetime_str: str,
    db: Session = Depends(get_db_async),
):
    try:
        datetime = string_to_datetime(datetime_str)
        logger.info("API endpoint /locations/%s called.", datetime)
        location = db_handler_instance.get_all_locations_since(
            db=db, since=datetime
        )
        if not location:
            logger.warning("No location found for datetime: %s", datetime)
            raise HTTPException(status_code=404, detail="Location not found")
        logger.info("Successfully retrieved location via API.")
        return location
    except HTTPException as e:
        logger.error("HTTP error: %s", e.detail)
        raise e
    except ValueError as e:
        logger.error("Invalid datetime format: %s", e)
        raise HTTPException(
            status_code=400,
            detail="Invalid datetime format. Use YYYY-MM-DDTHH:MM:SS.",
        )
    except Exception as e:
        logger.error("API error fetching location: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error retrieving location",
        )
