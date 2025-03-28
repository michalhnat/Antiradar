from typing import List

from fastapi import APIRouter, Depends

from backend.app.db import models
from backend.app.db.database import get_db_async
from backend.app.db.database_handler import DatabaseHandler

router = APIRouter()


def get_db_handler(db=Depends(get_db_async)):
    return DatabaseHandler(db)


@router.get("/locations", response_model=List[models.LocationPydantic])
def get_all_locations(db_handler: DatabaseHandler = Depends(get_db_handler)):
    locations = db_handler.get_all_locations()
    return locations
