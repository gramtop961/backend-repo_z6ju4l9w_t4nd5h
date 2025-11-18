"""
Database Schemas for Nutrition App

Each Pydantic model represents a collection in MongoDB.
Collection name is the lowercase of the class name.

Use these for validation and persistence via database helper functions.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

# --- Nutrition App Schemas ---

class Food(BaseModel):
    """
    Food items with macro nutrients per 100 grams
    Collection name: "food"
    """
    name: str = Field(..., description="Food name")
    calories_per_100g: float = Field(..., ge=0, description="Calories per 100g")
    protein_per_100g: float = Field(..., ge=0, description="Protein grams per 100g")
    carbs_per_100g: float = Field(..., ge=0, description="Carb grams per 100g")
    fat_per_100g: float = Field(..., ge=0, description="Fat grams per 100g")

class MealItem(BaseModel):
    """
    One line item in a meal. Either reference a food by id or provide custom macros per 100g.
    """
    food_id: Optional[str] = Field(None, description="Referenced food document id")
    name: Optional[str] = Field(None, description="Custom item name (if no food_id)")
    quantity_g: float = Field(..., gt=0, description="Quantity in grams")
    # Optional custom macros per 100g for ad-hoc items
    calories_per_100g: Optional[float] = Field(None, ge=0)
    protein_per_100g: Optional[float] = Field(None, ge=0)
    carbs_per_100g: Optional[float] = Field(None, ge=0)
    fat_per_100g: Optional[float] = Field(None, ge=0)

class Meal(BaseModel):
    """
    A saved meal with a name and items
    Collection name: "meal"
    """
    name: str = Field(..., description="Meal name")
    items: List[MealItem] = Field(..., description="List of meal items")
    total_calories: float = Field(..., ge=0)
    total_protein: float = Field(..., ge=0)
    total_carbs: float = Field(..., ge=0)
    total_fat: float = Field(..., ge=0)

# Existing example schemas remain below for reference

class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")
