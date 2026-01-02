from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
try:
    from app.database import engine, Base, get_db
    from app.models import Food, User
    from app.schemas import (
        FoodCreate,
        FoodResponse,
        DietInput,
        DietResult,
        UserInput,
        PredictionResponse,
        GoalInput,
    )
    from app.calcs import (
        calculate_bmr,
        calculate_tdee,
        goal_calories,
        get_macro_targets,
    )
except ImportError:
    print("Local imports failed, but continuing to load routes...")

# -------------------------------------------------
# App init
# -------------------------------------------------

app = FastAPI(title="Fitness Backend API")
# This finds the 'static' folder inside your 'app' folder
current_dir = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(current_dir, "static")

# 1. Mount the static folder so CSS/JS can be found
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")
else:
    print(f"WARNING: Static path not found at {static_path}")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)



# -------------------------------------------------
# Prediction (placeholder)
# -------------------------------------------------

@app.post("/api/predict", response_model=PredictionResponse)
def predict(data: UserInput):
    return PredictionResponse(
        muscle_gain=0.5,
        fat_loss=0.2,
        weight_change=0.3,
        nutritional_value="Balanced",
        advice="Train consistently and eat clean."
    )

# -------------------------------------------------
# Food
# -------------------------------------------------

@app.get("/foods", response_model=list[FoodResponse])
def get_foods(db: Session = Depends(get_db)):
    return db.query(Food).all()

@app.post("/food/custom", response_model=FoodResponse)
def add_or_update_food(food: FoodCreate, db: Session = Depends(get_db)):
    existing = db.query(Food).filter(Food.name == food.name.lower()).first()

    if existing:
        existing.calories_per_100g = food.calories_per_100g
        existing.protein_per_100g = food.protein_per_100g
        existing.carbs_per_100g = food.carbs_per_100g
        existing.fat_per_100g = food.fat_per_100g
        db.commit()
        db.refresh(existing)
        return existing

    new_food = Food(
        name=food.name.lower(),
        calories_per_100g=food.calories_per_100g,
        protein_per_100g=food.protein_per_100g,
        carbs_per_100g=food.carbs_per_100g,
        fat_per_100g=food.fat_per_100g
    )
    db.add(new_food)
    db.commit()
    db.refresh(new_food)
    return new_food

@app.get("/food/search", response_model=list[FoodResponse])
def search_food(query: str, db: Session = Depends(get_db)):
    return db.query(Food).filter(Food.name.contains(query.lower())).all()

# -------------------------------------------------
# Diet
# -------------------------------------------------

@app.post("/diet", response_model=DietResult)
def calculate_diet(diet: DietInput, db: Session = Depends(get_db)):
    calories_target = diet.target_calories
    goal = diet.goal

    total_calories = 0.0
    total_protein = 0.0
    total_carbs = 0.0
    total_fat = 0.0

    for item in diet.foods:
        food = db.query(Food).filter(Food.id == item.food_id).first()
        if not food:
            continue

        factor = item.grams / 100
        total_calories += food.calories_per_100g * factor
        total_protein += food.protein_per_100g * factor
        total_carbs += food.carbs_per_100g * factor
        total_fat += food.fat_per_100g * factor

    protein_target, carbs_target, fat_target = get_macro_targets(
        calories_target, goal
    )

    protein_pct = round((total_protein / protein_target) * 100, 1)
    carbs_pct = round((total_carbs / carbs_target) * 100, 1)
    fat_pct = round((total_fat / fat_target) * 100, 1)

    advice = []

    if protein_pct < 100:
        advice.append("Increase protein intake.")
    if carbs_pct < 100:
        advice.append("Increase carbs intake.")
    if fat_pct < 100:
        advice.append("Increase healthy fats.")

    if not advice:
        advice.append("Great macro balance!")

    return DietResult(
        calories=round(total_calories, 1),
        protein=round(total_protein, 1),
        carbs=round(total_carbs, 1),
        fat=round(total_fat, 1),
        protein_target=round(protein_target, 1),
        carbs_target=round(carbs_target, 1),
        fat_target=round(fat_target, 1),
        protein_pct=protein_pct,
        carbs_pct=carbs_pct,
        fat_pct=fat_pct,
        advice=" ".join(advice)
    )

# -------------------------------------------------
# Goal
# -------------------------------------------------

@app.post("/goal")
def calculate_goal(data: GoalInput):
    bmr = calculate_bmr(
        data.weight,
        data.height,
        data.age,
        data.gender
    )

    tdee = calculate_tdee(bmr, data.activity_level)
    calories = goal_calories(tdee, data.goal)

    return {
        "bmr": round(bmr, 2),
        "tdee": round(tdee, 2),
        "target_calories": round(calories, 2)
    }




# 2. Add the route specifically for your info page
@app.get("/info")
async def get_info_page():
    return FileResponse(os.path.join(static_path, "info.html"))

# Make sure this starts at the very beginning of the line!
@app.get("/")
async def get_home():
    # This MUST return FileResponse to show the website
    # Make sure 'static_path' points to your 'backend/app/static' folder
    return FileResponse(os.path.join(static_path, "index.html"))
@app.get("/diet")
async def get_diet_page():
    return FileResponse(os.path.join(static_path, "diet.html"))
@app.get("/summary")
async def get_summary_page():
    return FileResponse(os.path.join(static_path, "summary.html"))