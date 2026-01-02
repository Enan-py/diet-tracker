from sqlalchemy import Column, Integer, Float, String
from .database import Base
from sqlalchemy.dialects.sqlite import JSON

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer)
    weight = Column(Float)
    height = Column(Float)
    gender = Column(String)
    daily_diet = Column(String)
    weekly_workout = Column(String)
    recent_foods = Column(JSON, default=list)



class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    calories_per_100g = Column(Float)
    protein_per_100g = Column(Float)
    carbs_per_100g = Column(Float)
    fat_per_100g = Column(Float)
