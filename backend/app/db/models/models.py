from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    town = Column(String)
    street = Column(String)
    lat = Column(Float)
    long = Column(Float)
    message = Column(String)
    post_time = Column(DateTime(timezone=True), server_default=func.now())
