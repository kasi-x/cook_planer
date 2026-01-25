"""FastAPI server for nutrition optimization"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .models import FoodItem, OptimizeRequest, OptimizeResult
from .services import food_service
from src.scrapers.recipe_scraper import (
    get_all_recipes,
    process_recipe,
    parse_amount,
    match_ingredient,
    load_food_names,
    SAMPLE_RECIPES,
)

app = FastAPI(
    title="Nutrition Optimizer API",
    description="栄養価最適化API",
    version="1.0.0",
)

# CORS設定（本番環境では環境変数から追加のオリジンを設定可能）
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# 環境変数から追加のオリジンを読み込み（カンマ区切り）
extra_origins = os.environ.get("CORS_ORIGINS", "")
if extra_origins:
    allowed_origins.extend([o.strip() for o in extra_origins.split(",") if o.strip()])

# 本番環境では全オリジン許可も可能（CORS_ALLOW_ALL=true）
allow_all = os.environ.get("CORS_ALLOW_ALL", "").lower() == "true"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all else allowed_origins,
    allow_credentials=not allow_all,  # 全許可時はcredentials無効
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
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
    min_foods = {f.food_name: f.min_g for f in request.min_foods}
    return food_service.optimize(
        selected_foods=request.selected_foods,
        max_food_amount_g=request.max_food_amount_g,
        fixed_foods=fixed_foods,
        min_foods=min_foods,
        strategy=request.strategy,
        scoring_params=request.scoring_params,
        age=request.age,
        gender=request.gender,
        meal_type=request.meal_type,
        max_cost=request.max_cost,
    )


# --- レシピ関連のエンドポイント ---

class RecipeIngredient(BaseModel):
    """レシピの食材"""
    original_name: str
    amount_text: str
    amount_g: float | None
    matched_food: str | None


class Recipe(BaseModel):
    """レシピ"""
    id: str
    name: str
    servings: int
    source_url: str | None = None
    ingredients: list[RecipeIngredient]


class DishCalculateRequest(BaseModel):
    """一品計算リクエスト"""
    ingredients: list[dict] = Field(
        description="[{'food_name': '鶏肉（むね）', 'amount_g': 200}, ...]"
    )
    servings: int = Field(default=1, ge=1)


class DishNutrition(BaseModel):
    """一品の栄養情報"""
    name: str
    value: float
    unit: str


class DishCalculateResult(BaseModel):
    """一品計算結果"""
    success: bool
    message: str
    total_cost: float = 0
    per_serving_cost: float = 0
    nutrients: list[DishNutrition] = Field(default_factory=list)


@app.get("/api/recipes", response_model=list[Recipe])
def get_recipes() -> list[Recipe]:
    """登録済みレシピ一覧を取得"""
    from src.scrapers.recipe_scraper import load_sample_recipes

    food_names = load_food_names()
    recipes = get_all_recipes(food_names)
    # ソースJSONから source_url を取得
    raw_recipes = load_sample_recipes()
    url_map = {r["id"]: r.get("source_url") for r in raw_recipes}

    return [
        Recipe(
            id=r["id"],
            name=r["name"],
            servings=r["servings"],
            source_url=url_map.get(r["id"]),
            ingredients=[
                RecipeIngredient(
                    original_name=ing["original_name"],
                    amount_text=ing["amount_text"],
                    amount_g=ing["amount_g"],
                    matched_food=ing["matched_food"],
                )
                for ing in r["ingredients"]
            ],
        )
        for r in recipes
    ]


@app.get("/api/recipes/{recipe_id}", response_model=Recipe | None)
def get_recipe(recipe_id: str) -> Recipe | None:
    """レシピ詳細を取得"""
    from src.scrapers.recipe_scraper import load_sample_recipes

    food_names = load_food_names()
    recipes = get_all_recipes(food_names)
    raw_recipes = load_sample_recipes()
    url_map = {r["id"]: r.get("source_url") for r in raw_recipes}

    for r in recipes:
        if r["id"] == recipe_id:
            return Recipe(
                id=r["id"],
                name=r["name"],
                servings=r["servings"],
                source_url=url_map.get(r["id"]),
                ingredients=[
                    RecipeIngredient(
                        original_name=ing["original_name"],
                        amount_text=ing["amount_text"],
                        amount_g=ing["amount_g"],
                        matched_food=ing["matched_food"],
                    )
                    for ing in r["ingredients"]
                ],
            )
    return None


class LunchAnalysisRequest(BaseModel):
    """給食分析リクエスト"""
    age: int = Field(default=10, ge=6, le=15)
    gender: str = Field(default="male")


class NutrientData(BaseModel):
    """栄養素データ"""
    lunch_standards: dict[str, float]
    daily_requirements: dict[str, float]


@app.post("/api/lunch/analysis")
def get_lunch_analysis(request: LunchAnalysisRequest) -> NutrientData:
    """給食基準と1日必要量を取得"""
    from src.optimize import get_school_lunch_requirements, get_requirements_for_age_gender

    lunch = get_school_lunch_requirements(request.age)
    daily = get_requirements_for_age_gender(request.age, request.gender)

    return NutrientData(
        lunch_standards=lunch,
        daily_requirements=daily,
    )


@app.post("/api/lunch/optimize-cost")
def optimize_lunch_cost(request: LunchAnalysisRequest):
    """1日の1/3を最小コストで達成する最適化"""
    from src.optimize import (
        load_food_data,
        get_requirements_for_age_gender,
        optimize_diet,
        calculate_totals,
        get_upper_limits_for_age_gender,
        NUTRIENT_NAMES,
    )

    foods = load_food_data()
    daily = get_requirements_for_age_gender(request.age, request.gender)
    upper = get_upper_limits_for_age_gender(request.age, request.gender)

    # 1食分（1/3）の目標
    one_third = {k: v / 3 for k, v in daily.items()}
    one_third_upper = {k: v / 3 for k, v in upper.items()}

    # 全食品で最適化
    amounts = optimize_diet(
        foods,
        requirements=one_third,
        upper_limits=one_third_upper,
        max_food_amount_g=800,  # 1食として現実的な量
    )

    if not amounts:
        return {
            "success": False,
            "message": "最適化に失敗しました",
            "min_cost": 0,
            "foods": [],
            "nutrients": [],
        }

    totals = calculate_totals(foods, amounts)

    # 食品リスト
    food_list = []
    for name, amount in sorted(amounts.items(), key=lambda x: x[1], reverse=True):
        row = foods[foods["food_name"] == name].iloc[0]
        cost = row["price_per_100g"] * amount / 100
        food_list.append({
            "name": name,
            "amount_g": round(amount, 0),
            "cost": round(cost, 0),
            "cost_per_g": round(row["price_per_100g"] / 100, 2),
        })

    # 栄養達成状況
    nutrient_list = []
    for key in ["energy_kcal", "protein_g", "calcium_mg", "iron_mg", "vitamin_a_ug", "vitamin_c_mg"]:
        target = one_third.get(key, 0)
        actual = totals.get(key, 0)
        ratio = (actual / target * 100) if target > 0 else 0
        nutrient_list.append({
            "key": key,
            "name": NUTRIENT_NAMES.get(key, key),
            "target": round(target, 1),
            "actual": round(actual, 1),
            "ratio": round(ratio, 1),
            "achieved": ratio >= 100,
        })

    return {
        "success": True,
        "message": f"1食あたり¥{round(totals['total_cost'], 0)}で栄養基準達成可能",
        "min_cost": round(totals["total_cost"], 0),
        "total_weight_g": round(sum(amounts.values()), 0),
        "foods": food_list,
        "nutrients": nutrient_list,
    }


@app.get("/api/foods/cost-efficiency")
def get_cost_efficiency():
    """コスパの良い食品ランキング"""
    from src.optimize import load_food_data

    foods = load_food_data()

    # 各栄養素のコスパを計算（栄養量/価格）
    result = []
    for _, row in foods.iterrows():
        price = row["price_per_100g"]
        if price <= 0:
            continue

        # 総合スコア: (エネルギー + たんぱく質*10 + カルシウム/10) / 価格
        energy = row.get("energy_kcal", 0) or 0
        protein = row.get("protein_g", 0) or 0
        calcium = row.get("calcium_mg", 0) or 0

        score = (energy + protein * 10 + calcium / 10) / price

        result.append({
            "name": row["food_name"],
            "price_per_100g": round(price, 0),
            "energy_kcal": round(energy, 0),
            "protein_g": round(protein, 1),
            "calcium_mg": round(calcium, 0),
            "cost_efficiency_score": round(score, 2),
        })

    # スコア順にソート
    result.sort(key=lambda x: x["cost_efficiency_score"], reverse=True)
    return result[:20]  # トップ20


@app.get("/api/nutrients/cost-per-unit")
def get_nutrient_cost_per_unit():
    """各栄養素の単位あたりコスト（最安食品）"""
    from src.optimize import load_food_data, NUTRIENT_NAMES

    foods = load_food_data()

    # 分析対象の栄養素
    nutrients = {
        "energy_kcal": {"unit": "kcal", "display_unit": "100kcal"},
        "protein_g": {"unit": "g", "display_unit": "10g"},
        "calcium_mg": {"unit": "mg", "display_unit": "100mg"},
        "iron_mg": {"unit": "mg", "display_unit": "1mg"},
        "vitamin_a_ug": {"unit": "μg", "display_unit": "100μg"},
        "vitamin_c_mg": {"unit": "mg", "display_unit": "10mg"},
        "vitamin_b1_mg": {"unit": "mg", "display_unit": "0.1mg"},
        "vitamin_b2_mg": {"unit": "mg", "display_unit": "0.1mg"},
        "fiber_g": {"unit": "g", "display_unit": "1g"},
        "zinc_mg": {"unit": "mg", "display_unit": "1mg"},
    }

    result = {}

    for nutrient_key, info in nutrients.items():
        # 各食品のこの栄養素のコスパを計算
        food_costs = []

        for _, row in foods.iterrows():
            price = row["price_per_100g"]
            nutrient_value = row.get(nutrient_key, 0)

            if price <= 0 or not nutrient_value or nutrient_value <= 0:
                continue

            # 単位あたりのコスト（円/単位）
            cost_per_unit = price / nutrient_value

            food_costs.append({
                "food_name": row["food_name"],
                "price_per_100g": round(price, 0),
                "nutrient_per_100g": round(nutrient_value, 2),
                "cost_per_unit": round(cost_per_unit, 2),
            })

        # コスト順にソート（安い順）
        food_costs.sort(key=lambda x: x["cost_per_unit"])

        # トップ5を取得
        top_foods = food_costs[:5]

        # 単位変換係数を計算
        display_multiplier = 1
        if "100" in info["display_unit"]:
            display_multiplier = 100
        elif "10" in info["display_unit"]:
            display_multiplier = 10
        elif "0.1" in info["display_unit"]:
            display_multiplier = 0.1

        result[nutrient_key] = {
            "name": NUTRIENT_NAMES.get(nutrient_key, nutrient_key),
            "unit": info["unit"],
            "display_unit": info["display_unit"],
            "cheapest_cost": round(top_foods[0]["cost_per_unit"] * display_multiplier, 1) if top_foods else 0,
            "top_foods": [
                {
                    "name": f["food_name"],
                    "cost_per_display_unit": round(f["cost_per_unit"] * display_multiplier, 1),
                    "amount_per_100g": f["nutrient_per_100g"],
                }
                for f in top_foods
            ],
        }

    return result


@app.get("/api/price/history")
def get_price_history():
    """食料品価格の推移データを取得"""
    from src.scrapers.price_history import (
        get_price_change_summary,
        get_lunch_cost_comparison,
    )

    return {
        "price_summary": get_price_change_summary(),
        "lunch_costs": get_lunch_cost_comparison(),
    }


@app.get("/api/price/years-comparison")
def get_years_comparison():
    """全年度（2010-2026）の価格指数比較"""
    from src.scrapers.price_history import get_all_years_comparison

    return {
        "years": get_all_years_comparison(),
        "base_year": 2010,
    }


@app.get("/api/price/seasonal")
def get_seasonal_prices():
    """四半期別（4月/7月/10月/1月15日）の価格変動データ"""
    from src.scrapers.price_history import (
        get_seasonal_comparison,
        SEASONAL_FOOD_PRICES,
        get_all_years_seasonal_prices,
    )

    return {
        "categories": get_seasonal_comparison(2026),
        "food_examples": SEASONAL_FOOD_PRICES,
        "food_examples_by_year": get_all_years_seasonal_prices(),
        "available_years": [2010, 2012, 2014, 2016, 2018, 2020, 2022, 2024, 2026],
        "quarters": {
            "Q1_Apr": "4月15日",
            "Q2_Jul": "7月15日",
            "Q3_Oct": "10月15日",
            "Q4_Jan": "1月15日",
        },
    }


@app.get("/api/price/food-timeline/{food_name}")
def get_food_timeline(food_name: str):
    """特定食材の価格推移（2010-2026）"""
    from src.scrapers.price_history import get_food_price_timeline, FOOD_PRICE_HISTORY

    timeline = get_food_price_timeline(food_name)
    available_foods = list(FOOD_PRICE_HISTORY.keys())

    return {
        "food_name": food_name,
        "timeline": timeline,
        "available_foods": available_foods,
    }


@app.get("/api/price/category-trends")
def get_category_trends():
    """カテゴリ別の年次価格トレンド（2010-2026）"""
    from src.scrapers.price_history import get_category_yearly_trends

    return {
        "categories": get_category_yearly_trends(),
        "years": list(range(2010, 2027)),
    }


@app.get("/api/price/historical-optimization")
def get_historical_optimization():
    """過去価格での最適化比較（2010-2026年）"""
    from src.optimize import (
        load_food_data,
        get_requirements_for_age_gender,
        optimize_diet,
        calculate_totals,
        get_upper_limits_for_age_gender,
    )
    from src.scrapers.price_history import get_price_ratio

    foods = load_food_data()
    age = 10
    daily = get_requirements_for_age_gender(age, "male")
    upper = get_upper_limits_for_age_gender(age, "male")
    one_third = {k: v / 3 for k, v in daily.items()}
    one_third_upper = {k: v / 3 for k, v in upper.items()}

    # 2010年から2026年まで
    years = [2010, 2012, 2014, 2016, 2018, 2020, 2022, 2024, 2026]
    results = []

    for year in years:
        ratio = get_price_ratio(year)

        # 価格を調整した食品データを作成
        foods_adjusted = foods.copy()
        foods_adjusted["price_per_100g"] = foods["price_per_100g"] * ratio

        amounts = optimize_diet(
            foods_adjusted,
            requirements=one_third,
            upper_limits=one_third_upper,
            max_food_amount_g=800,
        )

        if amounts:
            totals = calculate_totals(foods_adjusted, amounts)
            cost = totals["total_cost"]
        else:
            cost = 0

        results.append({
            "year": year,
            "min_cost": round(cost, 0),
            "price_ratio": round(ratio, 3),
        })

    # 変化率を計算（2010年基準）
    base_cost = results[0]["min_cost"] if results else 0
    if base_cost > 0:
        for r in results:
            r["change_from_2010"] = round(
                (r["min_cost"] / base_cost - 1) * 100, 1
            )
    else:
        for r in results:
            r["change_from_2010"] = 0

    return {
        "age": age,
        "target": "1食分（1日の1/3）",
        "years": results,
        "base_year": 2010,
    }


@app.get("/api/lunch/age-comparison")
def get_age_comparison():
    """年齢別給食基準比較データを取得"""
    from src.optimize import get_school_lunch_requirements, get_requirements_for_age_gender, NUTRIENT_NAMES

    ages = [7, 10, 13]
    result = []

    for age in ages:
        lunch = get_school_lunch_requirements(age)
        daily_male = get_requirements_for_age_gender(age, "male")
        daily_female = get_requirements_for_age_gender(age, "female")

        nutrients = {}
        for key in ["energy_kcal", "protein_g", "calcium_mg", "iron_mg", "vitamin_a_ug", "vitamin_c_mg"]:
            lunch_val = lunch.get(key, 0)
            daily_m = daily_male.get(key, 0)
            daily_f = daily_female.get(key, 0)

            nutrients[key] = {
                "name": NUTRIENT_NAMES.get(key, key),
                "lunch": lunch_val,
                "daily_male": daily_m,
                "daily_female": daily_f,
                "ratio_male": (lunch_val / daily_m * 100) if daily_m > 0 else 0,
                "ratio_female": (lunch_val / daily_f * 100) if daily_f > 0 else 0,
            }

        result.append({
            "age": age,
            "label": f"{age}歳",
            "nutrients": nutrients,
        })

    return result


@app.post("/api/dish/calculate", response_model=DishCalculateResult)
def calculate_dish(request: DishCalculateRequest) -> DishCalculateResult:
    """一品の栄養価を計算"""
    from src.optimize import load_food_data, calculate_totals, NUTRIENT_NAMES, NUTRIENT_UNITS

    foods = load_food_data()
    if foods.empty:
        return DishCalculateResult(
            success=False,
            message="食品データがありません",
        )

    # 食材の量をディクショナリに変換
    amounts = {}
    for ing in request.ingredients:
        food_name = ing.get("food_name")
        amount_g = ing.get("amount_g", 0)
        if food_name and amount_g > 0:
            amounts[food_name] = amount_g

    if not amounts:
        return DishCalculateResult(
            success=False,
            message="有効な食材が指定されていません",
        )

    # 栄養価を計算
    totals = calculate_totals(foods, amounts)
    total_cost = totals.get("total_cost", 0)

    # 結果を整形
    nutrients = []
    for key in ["energy_kcal", "protein_g", "fiber_g", "calcium_mg", "iron_mg",
                "vitamin_a_ug", "vitamin_c_mg", "vitamin_b1_mg", "vitamin_b2_mg"]:
        if key in totals:
            nutrients.append(DishNutrition(
                name=NUTRIENT_NAMES.get(key, key),
                value=round(totals[key], 1),
                unit=NUTRIENT_UNITS.get(key, ""),
            ))

    return DishCalculateResult(
        success=True,
        message=f"{len(amounts)}食材の栄養価を計算しました",
        total_cost=round(total_cost, 0),
        per_serving_cost=round(total_cost / request.servings, 0),
        nutrients=nutrients,
    )
