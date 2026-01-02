# backend/app/calcs.py

def calculate_bmr(weight, height, age, gender):
    """BMR calculation using Mifflin-St Jeor Equation"""
    if gender.lower() == "male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

def calculate_tdee(bmr, activity_level):
    """TDEE based on activity factor"""
    factors = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very active": 1.9
    }
    return bmr * factors.get(activity_level.lower(), 1.2)

# app/calcs.py

def goal_calories(tdee, goal):
    """Adjust calories based on goal"""
    # Changed "lose" to "cut" and "gain" to "bulk" to match schemas.py
    if goal.lower() == "cut":
        return tdee - 500
    elif goal.lower() == "bulk":
        return tdee + 500
    return tdee  # maintain
def get_macro_targets(calories, goal="maintain"):
    """
    Return protein, carbs, fat targets (in grams) based on calories and goal.
    goal: "cut" | "maintain" | "bulk"
    """
    if goal == "cut":
        protein_pct, carb_pct, fat_pct = 0.30, 0.40, 0.30
    elif goal == "bulk":
        protein_pct, carb_pct, fat_pct = 0.25, 0.50, 0.25
    else:  # maintain
        protein_pct, carb_pct, fat_pct = 0.25, 0.45, 0.30

    protein_target = (calories * protein_pct) / 4
    carbs_target = (calories * carb_pct) / 4
    fat_target = (calories * fat_pct) / 9

    return protein_target, carbs_target, fat_target
def macro_distribution(protein, carbs, fat, protein_target, carbs_target, fat_target):
    """Calculate macro distribution percentages"""
    protein_pct = (protein / protein_target) * 100 if protein_target else 0
    carbs_pct = (carbs / carbs_target) * 100 if carbs_target else 0
    fat_pct = (fat / fat_target) * 100 if fat_target else 0
    return protein_pct, carbs_pct, fat_pct