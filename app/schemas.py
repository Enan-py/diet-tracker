from pydantic import BaseModel
from typing import List

# ---------- FOOD ----------

class FoodCreate(BaseModel):
    name: str
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float


class FoodResponse(FoodCreate):
    id: int

    class Config:
        from_attributes = True


# ---------- DIET ----------

class DietFood(BaseModel):
    food_id: int
    grams: float


class DietInput(BaseModel):
    foods: List[DietFood]
    target_calories: float 
    goal: str # "cut", "bulk", "maintain"

class DietResult(BaseModel):
    calories: float
    protein: float
    carbs: float
    fat: float

    protein_target: float
    carbs_target: float
    fat_target: float

    protein_pct: float
    carbs_pct: float
    fat_pct: float

    advice: str



# ---------- GOAL / ANALYSIS ----------

class GoalInput(BaseModel):
    age: int
    weight: float   # kg
    height: float   # cm
    gender: str     # "male" | "female"
    activity_level: str  # "low" | "medium" | "high"
    goal: str       # "cut" | "maintain" | "bulk"


# ---------- PREDICTION ----------

class UserInput(BaseModel):
    age: int
    weight: float
    height: float
    gender: str
    daily_diet: str
    weekly_workout: str


class PredictionResponse(BaseModel):
    muscle_gain: float
    fat_loss: float
    weight_change: float
    nutritional_value: str
    advice: str
