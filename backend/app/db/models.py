from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry
from sqlalchemy.sql import func

Base = declarative_base()


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    town = Column(String)
    street = Column(String)
    lat = Column(Float)
    long = Column(Float)
    post_time = Column(DateTime(timezone=True), server_default=func.now())

    geom = Column(Geometry(geometry_type="POINT"))
