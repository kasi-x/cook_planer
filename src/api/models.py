"""API data models"""

from pydantic import BaseModel, Field


class FoodItem(BaseModel):
    """Food item with basic info"""
    food_name: str
    price_per_100g: float
    energy_kcal: float
    protein_g: float


class OptimizeRequest(BaseModel):
    """Request for optimization"""
    selected_foods: list[str] = Field(..., min_length=1)
    max_food_amount_g: float = Field(default=1500, gt=0)


class NutrientStatus(BaseModel):
    """Status of a single nutrient"""
    name: str
    actual: float
    required: float
    unit: str
    ratio: float
    achieved: bool


class OptimizeResult(BaseModel):
    """Result of optimization"""
    success: bool
    message: str
    amounts: dict[str, float] = Field(default_factory=dict)
    total_cost: float = 0
    daily_cost: float = 0
    monthly_cost: float = 0
    nutrients: list[NutrientStatus] = Field(default_factory=list)
