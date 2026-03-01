"""価格予測・バッファーサービス

既存データ price_history.py の FOOD_PRICE_INDEX, CATEGORY_YEARLY_INDEX,
SEASONAL_FACTORS を活用して価格予測を行う。
"""

import numpy as np
from src.scrapers.price_history import (
    CATEGORY_YEARLY_INDEX,
    SEASONAL_FACTORS,
)
from src.optimize import load_food_data
from .seasonal_service import categorize_food, MONTH_TO_QUARTER
from .menu_models import DailyMenuData

# 基準月（2026年3月時点のデータを前提とした価格予測の起点）
CURRENT_MONTH = 3


def _get_yearly_trend(category: str) -> tuple[float, float]:
    """カテゴリの年次トレンド（線形回帰の傾きと2026年の値）"""
    yearly = CATEGORY_YEARLY_INDEX.get(category)
    if not yearly:
        return 0.0, 1.0

    years = sorted(yearly.keys())
    indices = [yearly[y] for y in years]

    if len(years) < 2:
        return 0.0, indices[0] if indices else 1.0

    # 線形回帰
    x = np.array(years, dtype=float)
    y = np.array(indices, dtype=float)
    coeffs = np.polyfit(x, y, 1)
    slope = coeffs[0]
    current_value = yearly.get(2026, float(np.polyval(coeffs, 2026)))

    return float(slope), float(current_value)


def _get_volatility(category: str) -> float:
    """カテゴリの価格変動性（標準偏差/平均）"""
    yearly = CATEGORY_YEARLY_INDEX.get(category)
    if not yearly:
        return 0.0

    values = list(yearly.values())
    if len(values) < 2:
        return 0.0

    mean = sum(values) / len(values)
    if mean == 0:
        return 0.0

    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return float(variance ** 0.5 / mean)


def predict_price(food_name: str, target_month: int) -> dict:
    """食材の価格予測"""
    foods_df = load_food_data()
    matches = foods_df[foods_df["food_name"] == food_name]

    if matches.empty:
        return {
            "food_name": food_name,
            "base_price": 0,
            "predicted_price": 0,
            "confidence": 0,
            "trend_direction": "unknown",
        }

    base_price = float(matches.iloc[0]["price_per_100g"])
    category = categorize_food(food_name)

    if not category:
        return {
            "food_name": food_name,
            "base_price": round(base_price, 1),
            "predicted_price": round(base_price, 1),
            "confidence": 0.5,
            "trend_direction": "stable",
        }

    # 年次トレンド
    slope, current_index = _get_yearly_trend(category)
    # target_monthが現在から何年先か（2026年3月基準）
    year_offset = (target_month - CURRENT_MONTH) / 12
    trend_factor = 1 + (slope * year_offset / current_index) if current_index > 0 else 1.0

    # 季節係数
    quarter = MONTH_TO_QUARTER.get(target_month, "Q1_Apr")
    seasonal_factor = SEASONAL_FACTORS.get(category, {}).get(quarter, 1.0)

    predicted = base_price * trend_factor * seasonal_factor

    # 信頼度（変動が小さいほど信頼度が高い）
    volatility = _get_volatility(category)
    confidence = max(0.3, min(0.95, 1.0 - volatility * 2))

    trend_direction = "up" if slope > 0.01 else ("down" if slope < -0.01 else "stable")

    return {
        "food_name": food_name,
        "base_price": round(base_price, 1),
        "predicted_price": round(predicted, 1),
        "confidence": round(confidence, 2),
        "trend_direction": trend_direction,
        "seasonal_factor": round(seasonal_factor, 2),
    }


def estimate_menu_cost(menu: DailyMenuData, target_month: int) -> dict:
    """献立の予測コストを計算"""
    items: list[dict] = []
    total_cost = 0.0

    for slot_name, slot in [
        ("staple", menu.staple), ("main_dish", menu.main_dish),
        ("side_dish", menu.side_dish), ("soup", menu.soup),
        ("dessert", menu.dessert),
    ]:
        if not slot:
            continue
        for ing in slot.ingredients:
            if not ing.food_name or ing.amount_g <= 0:
                continue

            prediction = predict_price(ing.food_name, target_month)
            cost = prediction["predicted_price"] * ing.amount_g / 100

            items.append({
                "food_name": ing.food_name,
                "amount_g": ing.amount_g,
                "predicted_price_per_100g": prediction["predicted_price"],
                "cost": round(cost, 1),
                "slot": slot_name,
            })
            total_cost += cost

    # 牛乳コスト
    if menu.milk:
        milk_pred = predict_price("牛乳", target_month)
        milk_cost = milk_pred["predicted_price"] * 206 / 100
        items.append({
            "food_name": "牛乳",
            "amount_g": 206,
            "predicted_price_per_100g": milk_pred["predicted_price"],
            "cost": round(milk_cost, 1),
            "slot": "milk",
        })
        total_cost += milk_cost

    return {
        "total_cost": round(total_cost, 0),
        "items": items,
        "month": target_month,
    }


def get_category_price_history(category: str) -> list[dict]:
    """カテゴリの価格推移"""
    yearly = CATEGORY_YEARLY_INDEX.get(category)
    if not yearly:
        return []

    return [
        {"year": year, "index": index}
        for year, index in sorted(yearly.items())
    ]


# --- F5: 価格変動バッファー ---

def calculate_buffer(food_name: str, target_month: int, buffer_pct: float = 10.0) -> dict:
    """バッファー付き価格を計算"""
    prediction = predict_price(food_name, target_month)
    predicted = prediction["predicted_price"]

    category = categorize_food(food_name)
    volatility = _get_volatility(category) if category else 0.0

    # 変動が大きいカテゴリは自動的にバッファー増加
    auto_buffer = buffer_pct + (volatility * 100)
    buffered = predicted * (1 + auto_buffer / 100)

    return {
        "food_name": food_name,
        "predicted_price": round(predicted, 1),
        "buffered_price": round(buffered, 1),
        "buffer_pct": round(auto_buffer, 1),
        "volatility_score": round(volatility, 3),
    }


def estimate_menu_cost_with_buffer(
    menu: DailyMenuData, target_month: int, buffer_pct: float = 10.0
) -> dict:
    """バッファー付き献立コスト推定"""
    base_estimate = estimate_menu_cost(menu, target_month)

    buffered_total = 0.0
    buffered_items = []

    for item in base_estimate["items"]:
        buf = calculate_buffer(item["food_name"], target_month, buffer_pct)
        buffered_cost = buf["buffered_price"] * item["amount_g"] / 100
        buffered_items.append({
            **item,
            "buffered_price_per_100g": buf["buffered_price"],
            "buffered_cost": round(buffered_cost, 1),
            "applied_buffer_pct": buf["buffer_pct"],
        })
        buffered_total += buffered_cost

    return {
        "total_cost": base_estimate["total_cost"],
        "buffered_total_cost": round(buffered_total, 0),
        "buffer_pct": buffer_pct,
        "items": buffered_items,
        "month": target_month,
    }
