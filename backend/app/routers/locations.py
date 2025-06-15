import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_db
from backend.app.schemas.location import (
    LocationCreate,
    LocationResponse,
    LocationUpdate,
)
from backend.app.services.location_service import LocationService
from backend.utils.converter import string_to_datetime

router = APIRouter(
    prefix="/locations",
    tags=["locations"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)


@router.get("/", response_model=List[LocationResponse])
async def get_locations(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Number of records to return"
    ),
    town: Optional[str] = Query(None, description="Filter by town name"),
    db: Session = Depends(get_db),
):
    try:
        service = LocationService(db)

        if town:
            locations = service.get_locations_by_town(
                town, skip=skip, limit=limit
            )
        else:
            locations = service.get_locations(skip=skip, limit=limit)

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


@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(
    location_id: int,
    db: Session = Depends(get_db),
):
    try:
        service = LocationService(db)
        location = service.get_location(location_id)

        if not location:
            raise HTTPException(status_code=404, detail="Location not found")

        logger.info("Successfully retrieved location %d via API.", location_id)
        return location
    except HTTPException:
        raise
    except Exception as e:
        logger.error("API error fetching location %d: %s", location_id, e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error retrieving location",
        )


@router.post("/", response_model=LocationResponse, status_code=201)
async def create_location(
    location: LocationCreate,
    db: Session = Depends(get_db),
):
    try:
        service = LocationService(db)
        created_location = service.create_location(location)

        logger.info(
            "Successfully created location with ID: %d", created_location.id
        )
        return created_location
    except Exception as e:
        logger.error("API error creating location: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error creating location",
        )


@router.put("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: int,
    location: LocationUpdate,
    db: Session = Depends(get_db),
):
    try:
        service = LocationService(db)
        updated_location = service.update_location(location_id, location)

        if not updated_location:
            raise HTTPException(status_code=404, detail="Location not found")

        logger.info("Successfully updated location %d via API.", location_id)
        return updated_location
    except HTTPException:
        raise
    except Exception as e:
        logger.error("API error updating location %d: %s", location_id, e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error updating location",
        )


@router.delete("/{location_id}", status_code=204)
async def delete_location(
    location_id: int,
    db: Session = Depends(get_db),
):
    try:
        service = LocationService(db)
        deleted = service.delete_location(location_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Location not found")

        logger.info("Successfully deleted location %d via API.", location_id)
        return
    except HTTPException:
        raise
    except Exception as e:
        logger.error("API error deleting location %d: %s", location_id, e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error deleting location",
        )


@router.get("/query/recent", response_model=List[LocationResponse])
async def get_recent_locations(
    hours: int = Query(
        ...,
        ge=1,
        le=168,
        description="Number of hours to look back (max 7 days)",
    ),
    db: Session = Depends(get_db),
):
    try:
        service = LocationService(db)
        locations = service.get_recent_locations(hours)

        if not locations:
            logger.warning("No locations found in the last %d hours.", hours)
            raise HTTPException(status_code=404, detail="No locations found")

        logger.info(
            "Successfully retrieved %d recent locations via API.",
            len(locations),
        )
        return locations
    except HTTPException:
        raise
    except Exception as e:
        logger.error("API error fetching recent locations: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error retrieving recent locations",
        )


@router.get(
    "/query/since/{datetime_str}", response_model=List[LocationResponse]
)
async def get_locations_since(
    datetime_str: str,
    db: Session = Depends(get_db),
):
    try:
        since_datetime = string_to_datetime(datetime_str)
        service = LocationService(db)
        locations = service.get_locations_since(since_datetime)

        if not locations:
            logger.warning(
                "No locations found since datetime: %s", since_datetime
            )
            raise HTTPException(status_code=404, detail="No locations found")

        logger.info(
            "Successfully retrieved %d locations since %s via API.",
            len(locations),
            since_datetime,
        )
        return locations
    except ValueError as e:
        logger.error("Invalid datetime format: %s", e)
        raise HTTPException(
            status_code=400,
            detail="Invalid datetime format. Use YYYY-MM-DDTHH:MM:SS.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("API error fetching locations since datetime: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error retrieving locations",
        )
