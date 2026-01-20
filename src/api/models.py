"""API data models"""

from enum import Enum
from pydantic import BaseModel, Field


class OptimizeStrategy(str, Enum):
    """Optimization strategy"""
    STRICT = "strict"  # 全栄養素を満たす（厳密）
    CALORIE_FOCUSED = "calorie_focused"  # カロリー重視
    BALANCED = "balanced"  # バランス型（デフォルト）
    CUSTOM_SCORE = "custom_score"  # カスタムスコア


class ScoringParams(BaseModel):
    """Parameters for custom scoring optimization"""
    deficit_penalty: float = Field(default=1.0, description="不足1%あたりのペナルティ点")
    cost_bonus: float = Field(default=0.1, description="1円節約あたりのボーナス点")
    calorie_weight: float = Field(default=1.0, description="カロリーの重み")
    protein_weight: float = Field(default=1.0, description="タンパク質の重み")
    vitamin_weight: float = Field(default=1.0, description="ビタミン類の重み")
    mineral_weight: float = Field(default=1.0, description="ミネラル類の重み")


class FoodItem(BaseModel):
    """Food item with basic info"""
    food_name: str
    price_per_100g: float
    energy_kcal: float
    protein_g: float


class FixedFood(BaseModel):
    """Food with fixed amount"""
    food_name: str
    amount_g: float = Field(gt=0)


class OptimizeRequest(BaseModel):
    """Request for optimization"""
    selected_foods: list[str] = Field(default_factory=list)
    max_food_amount_g: float = Field(default=1500, gt=0)
    fixed_foods: list[FixedFood] = Field(default_factory=list)
    strategy: OptimizeStrategy = Field(default=OptimizeStrategy.BALANCED)
    scoring_params: ScoringParams = Field(default_factory=ScoringParams)


class FoodAmount(BaseModel):
    """Food amount in optimization result"""
    food_name: str
    amount_g: float
    cost: float
    contribution_percent: float
    source_price: str
    source_nutrition: str


class FoodContribution(BaseModel):
    """Contribution of a food to a nutrient"""
    food_name: str
    amount: float
    contribution: float
    percentage: float


class NutrientStatus(BaseModel):
    """Status of a single nutrient"""
    name: str
    actual: float
    required: float
    unit: str
    ratio: float
    achieved: bool
    contributions: list[FoodContribution] = Field(default_factory=list)


class OptimizeResult(BaseModel):
    """Result of optimization"""
    success: bool
    message: str
    amounts: dict[str, float] = Field(default_factory=dict)
    food_amounts: list[FoodAmount] = Field(default_factory=list)
    total_cost: float = 0
    daily_cost: float = 0
    monthly_cost: float = 0
    nutrients: list[NutrientStatus] = Field(default_factory=list)
