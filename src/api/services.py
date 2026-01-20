"""Business logic for optimization API"""

import pandas as pd

from src.optimize import (
    load_food_data,
    optimize_diet,
    calculate_totals,
    DAILY_UPPER_LIMITS,
    NUTRIENT_NAMES,
    _optimize_strict,
    optimize_calorie_focused,
    optimize_with_score,
    get_requirements_for_age_gender,
    get_requirements_for_meal_type,
    AGE_GROUPS,
)
from .models import (
    FoodItem,
    OptimizeResult,
    NutrientStatus,
    FoodContribution,
    FoodAmount,
    OptimizeStrategy,
    ScoringParams,
    MealType,
)


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
        fixed_foods: dict[str, float] = None,
        strategy: OptimizeStrategy = OptimizeStrategy.BALANCED,
        scoring_params: ScoringParams = None,
        age: int = 23,
        gender: str = "male",
        meal_type: MealType = MealType.DAILY,
    ) -> OptimizeResult:
        """Run optimization on selected foods

        Args:
            fixed_foods: {食品名: 固定量(g)} の辞書
            strategy: 最適化戦略
            scoring_params: カスタムスコアのパラメータ
            age: 年齢
            gender: 性別 (male/female)
            meal_type: 食事タイプ (daily/per_meal/school_lunch)
        """
        if fixed_foods is None:
            fixed_foods = {}
        if scoring_params is None:
            scoring_params = ScoringParams()

        # 食事タイプに基づいて栄養基準を取得
        requirements = get_requirements_for_meal_type(meal_type.value, age, gender)

        if self.foods.empty:
            return OptimizeResult(
                success=False,
                message="食品データがありません",
            )

        # 固定食品も選択食品に含める
        all_selected = set(selected_foods) | set(fixed_foods.keys())
        selected_df = self.foods[self.foods["food_name"].isin(all_selected)]

        if selected_df.empty:
            return OptimizeResult(
                success=False,
                message="選択された食品が見つかりません",
            )

        # 戦略に応じて最適化を実行
        is_strict = False
        strategy_name = ""

        if strategy == OptimizeStrategy.STRICT:
            # 厳密モード: 全栄養素を満たす
            amounts = _optimize_strict(
                selected_df,
                requirements,
                DAILY_UPPER_LIMITS,
                max_food_amount_g,
                fixed_foods,
            )
            is_strict = bool(amounts)
            strategy_name = "厳密モード"
            if not amounts:
                return OptimizeResult(
                    success=False,
                    message="厳密モードでは最適化できませんでした。選択した食品では全栄養素を満たせません。",
                )

        elif strategy == OptimizeStrategy.CALORIE_FOCUSED:
            # カロリー重視モード
            amounts = optimize_calorie_focused(
                selected_df,
                requirements,
                DAILY_UPPER_LIMITS,
                max_food_amount_g,
                fixed_foods,
            )
            strategy_name = "カロリー重視"

        elif strategy == OptimizeStrategy.CUSTOM_SCORE:
            # カスタムスコアモード
            scoring_dict = {
                'deficit_penalty': scoring_params.deficit_penalty,
                'cost_bonus': scoring_params.cost_bonus,
                'calorie_weight': scoring_params.calorie_weight,
                'protein_weight': scoring_params.protein_weight,
                'vitamin_weight': scoring_params.vitamin_weight,
                'mineral_weight': scoring_params.mineral_weight,
            }
            amounts = optimize_with_score(
                selected_df,
                requirements,
                DAILY_UPPER_LIMITS,
                max_food_amount_g,
                fixed_foods,
                scoring_dict,
            )
            strategy_name = "カスタムスコア"

        else:  # BALANCED (default)
            # バランスモード: 厳密を試し、失敗したら緩和
            strict_result = _optimize_strict(
                selected_df,
                requirements,
                DAILY_UPPER_LIMITS,
                max_food_amount_g,
                fixed_foods,
            )
            is_strict = bool(strict_result)
            amounts = optimize_diet(
                selected_df,
                requirements=requirements,
                upper_limits=DAILY_UPPER_LIMITS,
                max_food_amount_g=max_food_amount_g,
                fixed_foods=fixed_foods,
            )
            strategy_name = "バランス"

        if not amounts:
            return OptimizeResult(
                success=False,
                message="最適化に失敗しました。選択した食品では計算できません。",
            )

        totals = calculate_totals(self.foods, amounts)
        total_cost = totals.get("total_cost", 0)

        # 各食品の各栄養素への貢献度を計算
        food_contributions = {}
        food_total_contributions = {}  # 各食品の全栄養素への合計貢献度
        for food_name, amount_g in amounts.items():
            food_row = self.foods[self.foods["food_name"] == food_name].iloc[0]
            ratio = amount_g / 100
            food_contributions[food_name] = {}
            total_contrib = 0
            for key in requirements.keys():
                if key in food_row:
                    val = food_row[key]
                    if pd.notna(val):
                        food_contributions[food_name][key] = val * ratio
                        # 貢献度を正規化して合計
                        req_val = requirements[key]
                        if req_val > 0:
                            total_contrib += min((val * ratio) / req_val, 1.0)
            food_total_contributions[food_name] = total_contrib

        # 全食品の合計貢献度
        total_all_contributions = sum(food_total_contributions.values())

        # food_amounts を計算
        food_amounts = []
        for food_name, amount_g in amounts.items():
            food_row = self.foods[self.foods["food_name"] == food_name].iloc[0]
            cost = food_row["price_per_100g"] * amount_g / 100
            contrib_pct = (
                (food_total_contributions[food_name] / total_all_contributions * 100)
                if total_all_contributions > 0
                else 0
            )
            food_amounts.append(
                FoodAmount(
                    food_name=food_name,
                    amount_g=round(amount_g, 1),
                    cost=round(cost, 0),
                    contribution_percent=round(contrib_pct, 1),
                    source_price=food_row.get("source_price", ""),
                    source_nutrition=food_row.get("source_nutrition", ""),
                )
            )
        # コスト順にソート
        food_amounts.sort(key=lambda x: x.cost, reverse=True)

        nutrients = []
        achieved_count = 0
        for key, required in requirements.items():
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
            message = f"[{strategy_name}] 最適化成功（全栄養素を満たしています）"
        else:
            message = f"[{strategy_name}] {achieved_count}/{len(requirements)}栄養素を満たしています"

        return OptimizeResult(
            success=True,
            message=message,
            amounts=amounts,
            food_amounts=food_amounts,
            total_cost=round(total_cost, 0),
            daily_cost=round(total_cost, 0),
            monthly_cost=round(total_cost * 30, 0),
            nutrients=nutrients,
        )


food_service = FoodService()
