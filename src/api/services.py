"""Business logic for optimization API"""

import pandas as pd

from src.optimize import (
    load_food_data,
    optimize_diet,
    calculate_totals,
    DAILY_REQUIREMENTS,
    DAILY_UPPER_LIMITS,
    NUTRIENT_NAMES,
    _optimize_strict,
)
from .models import FoodItem, OptimizeResult, NutrientStatus, FoodContribution


def get_unit(nutrient_key: str) -> str:
    """Get unit for nutrient key"""
    if "kcal" in nutrient_key:
        return "kcal"
    if "_ug" in nutrient_key:
        return "ug"
    if "_mg" in nutrient_key:
        return "mg"
    return "g"


class FoodService:
    """Service for food data operations"""

    def __init__(self):
        self._foods: pd.DataFrame | None = None

    @property
    def foods(self) -> pd.DataFrame:
        if self._foods is None:
            self._foods = load_food_data()
        return self._foods

    def get_all_foods(self) -> list[FoodItem]:
        """Get all food items"""
        if self.foods.empty:
            return []

        return [
            FoodItem(
                food_name=row["food_name"],
                price_per_100g=row["price_per_100g"],
                energy_kcal=row.get("energy_kcal", 0),
                protein_g=row.get("protein_g", 0),
            )
            for _, row in self.foods.iterrows()
        ]

    def optimize(
        self,
        selected_foods: list[str],
        max_food_amount_g: float = 1500,
    ) -> OptimizeResult:
        """Run optimization on selected foods"""
        if self.foods.empty:
            return OptimizeResult(
                success=False,
                message="食品データがありません",
            )

        selected_df = self.foods[self.foods["food_name"].isin(selected_foods)]

        if selected_df.empty:
            return OptimizeResult(
                success=False,
                message="選択された食品が見つかりません",
            )

        # まず厳密な最適化を試行
        strict_result = _optimize_strict(
            selected_df,
            DAILY_REQUIREMENTS,
            DAILY_UPPER_LIMITS,
            max_food_amount_g,
        )
        is_strict = bool(strict_result)

        # 厳密版が失敗した場合は緩和版を使用
        amounts = optimize_diet(
            selected_df,
            requirements=DAILY_REQUIREMENTS,
            upper_limits=DAILY_UPPER_LIMITS,
            max_food_amount_g=max_food_amount_g,
        )

        if not amounts:
            return OptimizeResult(
                success=False,
                message="最適化に失敗しました。選択した食品では計算できません。",
            )

        totals = calculate_totals(self.foods, amounts)
        total_cost = totals.get("total_cost", 0)

        # 各食品の各栄養素への貢献度を計算
        food_contributions = {}
        for food_name, amount_g in amounts.items():
            food_row = self.foods[self.foods["food_name"] == food_name].iloc[0]
            ratio = amount_g / 100
            food_contributions[food_name] = {}
            for key in DAILY_REQUIREMENTS.keys():
                if key in food_row:
                    val = food_row[key]
                    if pd.notna(val):
                        food_contributions[food_name][key] = val * ratio

        nutrients = []
        achieved_count = 0
        for key, required in DAILY_REQUIREMENTS.items():
            actual = totals.get(key, 0)
            ratio = (actual / required * 100) if required > 0 else 0
            achieved = ratio >= 100
            if achieved:
                achieved_count += 1

            # 各食品の貢献度を計算
            contributions = []
            for food_name, amount_g in amounts.items():
                contrib_val = food_contributions.get(food_name, {}).get(key, 0)
                if contrib_val > 0:
                    contrib_pct = (contrib_val / required * 100) if required > 0 else 0
                    contributions.append(
                        FoodContribution(
                            food_name=food_name,
                            amount=round(amount_g, 0),
                            contribution=round(contrib_val, 2),
                            percentage=round(contrib_pct, 1),
                        )
                    )
            # 貢献度の高い順にソート
            contributions.sort(key=lambda x: x.percentage, reverse=True)

            nutrients.append(
                NutrientStatus(
                    name=NUTRIENT_NAMES.get(key, key),
                    actual=round(actual, 1),
                    required=round(required, 1),
                    unit=get_unit(key),
                    ratio=round(ratio, 1),
                    achieved=achieved,
                    contributions=contributions,
                )
            )

        if is_strict:
            message = "最適化成功（全栄養素を満たしています）"
        else:
            message = f"部分的な最適化（{achieved_count}/{len(DAILY_REQUIREMENTS)}栄養素を満たしています）"

        return OptimizeResult(
            success=True,
            message=message,
            amounts=amounts,
            total_cost=round(total_cost, 0),
            daily_cost=round(total_cost, 0),
            monthly_cost=round(total_cost * 30, 0),
            nutrients=nutrients,
        )


food_service = FoodService()
