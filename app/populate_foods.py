import sys
import os

# This adds the 'backend' folder to the python path automatically
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.models import Base, Food
from sqlalchemy.orm import Session # Fixed import

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def populate():
    # FIXED: Changed 'version' to 'Session'
    db: Session = SessionLocal()

    # Basic staples
    foods = [
        {"name": "chicken breast (cooked)", "calories": 165, "protein": 31, "carbs": 0, "fat": 3.6},
        {"name": "white rice (cooked)", "calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3},
        {"name": "brown rice (cooked)", "calories": 111, "protein": 2.6, "carbs": 23, "fat": 0.9},
        {"name": "egg (large)", "calories": 78, "protein": 6, "carbs": 0.6, "fat": 5},
        {"name": "oats (raw)", "calories": 389, "protein": 16.9, "carbs": 66, "fat": 6.9},
        {"name": "banana", "calories": 89, "protein": 1.1, "carbs": 22.8, "fat": 0.3},
        {"name": "potato (boiled)", "calories": 87, "protein": 1.9, "carbs": 20, "fat": 0.1},
        {"name": "broccoli", "calories": 34, "protein": 2.8, "carbs": 7, "fat": 0.4},
        {"name": "olive oil", "calories": 884, "protein": 0, "carbs": 0, "fat": 100},
    ]

    for item in foods:
        # Check if exists to avoid duplicates
        existing = db.query(Food).filter(Food.name == item["name"]).first()
        if not existing:
            new_food = Food(
                name=item["name"],
                calories_per_100g=item["calories"],
                protein_per_100g=item["protein"],
                carbs_per_100g=item["carbs"],
                fat_per_100g=item["fat"]
            )
            db.add(new_food)
            print(f"Added {item['name']}")
    
    db.commit()
    db.close()
    print("Database populated successfully!")

if __name__ == "__main__":
    populate()