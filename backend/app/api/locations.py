from fastapi import APIRouter, Depends
from typing import List

from backend.app.db import models
from backend.app.db.database import get_db
from backend.app.db.DatabaseHandler import DatabaseHandler


router = APIRouter()


def get_db_handler(db=Depends(get_db)):
    return DatabaseHandler(db)


@router.get("/locations", response_model=List[models.LocationPydantic])
def get_all_locations(db_handler: DatabaseHandler = Depends(get_db_handler)):
    locations = db_handler.get_all_locations()
    return locations
