from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LocationBase(BaseModel):
    town: str = Field(..., description="Town or city name")
    street: str = Field("", description="Street name or address")
    lat: Optional[float] = Field(None, description="Latitude coordinate")
    long: Optional[float] = Field(None, description="Longitude coordinate")
    message: str = Field(..., description="Original message content")


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    town: Optional[str] = None
    street: Optional[str] = None
    lat: Optional[float] = None
    long: Optional[float] = None
    message: Optional[str] = None


class LocationResponse(LocationBase):
    id: int = Field(..., description="Unique location identifier")
    post_time: datetime = Field(
        ..., description="When the location was posted"
    )

    class Config:
        from_attributes = True
