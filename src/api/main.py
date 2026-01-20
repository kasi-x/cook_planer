"""FastAPI server for nutrition optimization"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models import FoodItem, OptimizeRequest, OptimizeResult
from .services import food_service

app = FastAPI(
    title="Nutrition Optimizer API",
    description="栄養価最適化API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check() -> dict:
    """Health check endpoint"""
    return {"status": "ok"}


@app.get("/api/foods", response_model=list[FoodItem])
def get_foods() -> list[FoodItem]:
    """Get all available food items"""
    return food_service.get_all_foods()


@app.post("/api/optimize", response_model=OptimizeResult)
def optimize(request: OptimizeRequest) -> OptimizeResult:
    """Run optimization on selected foods"""
    fixed_foods = {f.food_name: f.amount_g for f in request.fixed_foods}
    return food_service.optimize(
        selected_foods=request.selected_foods,
        max_food_amount_g=request.max_food_amount_g,
        fixed_foods=fixed_foods,
        strategy=request.strategy,
        scoring_params=request.scoring_params,
        age=request.age,
        gender=request.gender,
        meal_type=request.meal_type,
    )
