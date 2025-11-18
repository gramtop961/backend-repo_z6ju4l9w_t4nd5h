import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Food, Meal, MealItem

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Nutrition API is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# ---------- Models for API payloads ----------
class CreateFoodPayload(BaseModel):
    name: str
    calories_per_100g: float = Field(ge=0)
    protein_per_100g: float = Field(ge=0)
    carbs_per_100g: float = Field(ge=0)
    fat_per_100g: float = Field(ge=0)

class CalculateMealItem(BaseModel):
    name: str
    grams: float = Field(gt=0)
    calories_per_100g: float = Field(ge=0)
    protein_per_100g: float = Field(ge=0)
    carbs_per_100g: float = Field(ge=0)
    fat_per_100g: float = Field(ge=0)

class CalculateMealPayload(BaseModel):
    items: List[CalculateMealItem]
    name: Optional[str] = None

# ---------- Helper ----------

def calc_totals(items: List[CalculateMealItem]):
    totals = {
        "calories": 0.0,
        "protein": 0.0,
        "carbs": 0.0,
        "fat": 0.0,
    }
    for it in items:
        factor = it.grams / 100.0
        totals["calories"] += it.calories_per_100g * factor
        totals["protein"] += it.protein_per_100g * factor
        totals["carbs"] += it.carbs_per_100g * factor
        totals["fat"] += it.fat_per_100g * factor
    return {k: round(v, 2) for k, v in totals.items()}

# ---------- Food Endpoints ----------

@app.post("/api/foods")
def create_food(payload: CreateFoodPayload):
    food = Food(**payload.model_dump())
    food_id = create_document("food", food)
    return {"id": food_id}

@app.get("/api/foods")
def list_foods(query: Optional[str] = None, limit: int = 50):
    filter_dict = {}
    if query:
        # Simple case-insensitive substring match
        filter_dict = {"name": {"$regex": query, "$options": "i"}}
    docs = get_documents("food", filter_dict, limit)
    # Convert ObjectId to str
    for d in docs:
        d["_id"] = str(d["_id"]) if "_id" in d else None
    return docs

# ---------- Meal Calculation & Save ----------

@app.post("/api/meals/calculate")
def calculate_meal(payload: CalculateMealPayload):
    if not payload.items:
        raise HTTPException(status_code=400, detail="No items provided")
    totals = calc_totals(payload.items)
    return {"name": payload.name, "totals": totals}

@app.post("/api/meals/save")
def save_meal(payload: CalculateMealPayload):
    if not payload.items:
        raise HTTPException(status_code=400, detail="No items provided")
    totals = calc_totals(payload.items)
    # Store meal with raw items for reproducibility
    meal_doc = {
        "name": payload.name or "Meal",
        "items": [it.model_dump() for it in payload.items],
        "total_calories": totals["calories"],
        "total_protein": totals["protein"],
        "total_carbs": totals["carbs"],
        "total_fat": totals["fat"],
    }
    meal_id = create_document("meal", meal_doc)
    return {"id": meal_id, "totals": totals}

@app.get("/api/meals")
def list_meals(limit: int = 50):
    docs = get_documents("meal", {}, limit)
    for d in docs:
        d["_id"] = str(d["_id"]) if "_id" in d else None
    return docs

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
