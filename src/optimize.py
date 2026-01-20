"""栄養価最適化計算

線形計画法を用いて、最低コストで基準栄養価を満たす
食材の組み合わせを計算する
"""

import pandas as pd
import numpy as np
from scipy.optimize import linprog
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
MERGED_DIR = DATA_DIR / "merged"

# 12-14歳の食事摂取基準（2025年版）
# Source: https://japanese-food.net/top-page/meals-intake-standard-table-2025/dietary-intake-standard12-14-2025
# 身体活動レベル「普通」を使用

DAILY_REQUIREMENTS_MALE = {
    # 基本
    "energy_kcal": 2600,
    "protein_g": 60,
    "fiber_g": 17,
    # ミネラル
    "potassium_mg": 2400,
    "calcium_mg": 1000,
    "magnesium_mg": 290,
    "iron_mg": 9.0,
    "zinc_mg": 8.5,
    # ビタミン
    "vitamin_a_ug": 800,
    "vitamin_d_ug": 9.0,
    "vitamin_e_mg": 6.5,
    "vitamin_k_ug": 140,
    "vitamin_b1_mg": 1.1,
    "vitamin_b2_mg": 1.6,
    "niacin_mg": 15,
    "vitamin_b6_mg": 1.4,
    "vitamin_b12_ug": 4.0,
    "folate_ug": 230,
    "pantothenic_mg": 7,
    "vitamin_c_mg": 90,
}

DAILY_REQUIREMENTS_FEMALE = {
    # 基本
    "energy_kcal": 2400,
    "protein_g": 55,
    "fiber_g": 16,
    # ミネラル
    "potassium_mg": 2200,
    "calcium_mg": 800,
    "magnesium_mg": 290,
    "iron_mg": 8.0,
    "zinc_mg": 8.5,
    # ビタミン
    "vitamin_a_ug": 700,
    "vitamin_d_ug": 9.0,
    "vitamin_e_mg": 6.0,
    "vitamin_k_ug": 150,
    "vitamin_b1_mg": 1.0,
    "vitamin_b2_mg": 1.4,
    "niacin_mg": 14,
    "vitamin_b6_mg": 1.3,
    "vitamin_b12_ug": 4.0,
    "folate_ug": 230,
    "pantothenic_mg": 6,
    "vitamin_c_mg": 90,
}

# デフォルトは男性
DAILY_REQUIREMENTS = DAILY_REQUIREMENTS_MALE

# 栄養素の上限（過剰摂取防止）
DAILY_UPPER_LIMITS = {
    "energy_kcal": 3000,
}

# 栄養素の日本語名
NUTRIENT_NAMES = {
    "energy_kcal": "エネルギー",
    "protein_g": "たんぱく質",
    "fiber_g": "食物繊維",
    "potassium_mg": "カリウム",
    "calcium_mg": "カルシウム",
    "magnesium_mg": "マグネシウム",
    "iron_mg": "鉄",
    "zinc_mg": "亜鉛",
    "vitamin_a_ug": "ビタミンA",
    "vitamin_d_ug": "ビタミンD",
    "vitamin_e_mg": "ビタミンE",
    "vitamin_k_ug": "ビタミンK",
    "vitamin_b1_mg": "ビタミンB1",
    "vitamin_b2_mg": "ビタミンB2",
    "niacin_mg": "ナイアシン",
    "vitamin_b6_mg": "ビタミンB6",
    "vitamin_b12_ug": "ビタミンB12",
    "folate_ug": "葉酸",
    "pantothenic_mg": "パントテン酸",
    "vitamin_c_mg": "ビタミンC",
    "fat_g": "脂質",
    "carbohydrate_g": "炭水化物",
}


def load_food_data() -> pd.DataFrame:
    """結合済み食品データを読み込み"""
    path = MERGED_DIR / "food_price_nutrition.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def optimize_diet(
    foods: pd.DataFrame,
    requirements: dict = None,
    upper_limits: dict = None,
    max_food_amount_g: float = 1500,
) -> dict:
    """最小コストで栄養要件を満たす食材量を計算

    まず全制約を満たす最適化を試み、失敗した場合は
    制約を緩和してベストエフォートの結果を返す。
    """
    if requirements is None:
        requirements = DAILY_REQUIREMENTS
    if upper_limits is None:
        upper_limits = DAILY_UPPER_LIMITS

    if foods.empty:
        return {}

    # まず全制約での最適化を試行
    result = _optimize_strict(foods, requirements, upper_limits, max_food_amount_g)
    if result:
        return result

    # 失敗した場合は緩和版を試行
    return _optimize_relaxed(foods, requirements, upper_limits, max_food_amount_g)


def _optimize_strict(
    foods: pd.DataFrame,
    requirements: dict,
    upper_limits: dict,
    max_food_amount_g: float,
) -> dict:
    """全栄養素制約を満たす最適化（厳密版）"""
    n_foods = len(foods)
    food_names = foods['food_name'].tolist()
    c = foods['price_per_100g'].values

    A_ub = []
    b_ub = []

    for nutrient, req in requirements.items():
        if nutrient in foods.columns:
            coeffs = -foods[nutrient].fillna(0).values
            A_ub.append(coeffs)
            b_ub.append(-req)

    for nutrient, limit in upper_limits.items():
        if nutrient in foods.columns:
            coeffs = foods[nutrient].fillna(0).values
            A_ub.append(coeffs)
            b_ub.append(limit)

    A_ub = np.array(A_ub) if A_ub else None
    b_ub = np.array(b_ub) if b_ub else None
    bounds = [(0, max_food_amount_g / 100) for _ in range(n_foods)]

    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

    if not result.success:
        return {}

    return _extract_amounts(result.x, food_names)


def _optimize_relaxed(
    foods: pd.DataFrame,
    requirements: dict,
    upper_limits: dict,
    max_food_amount_g: float,
) -> dict:
    """制約を緩和した最適化（ベストエフォート版）

    エネルギー目標を達成しつつコストを最小化する。
    他の栄養素は可能な限り摂取する。
    """
    n_foods = len(foods)
    food_names = foods['food_name'].tolist()
    c = foods['price_per_100g'].values

    A_ub = []
    b_ub = []

    # エネルギー下限制約（目標の80%以上）
    if 'energy_kcal' in requirements and 'energy_kcal' in foods.columns:
        energy_coeffs = -foods['energy_kcal'].fillna(0).values
        A_ub.append(energy_coeffs)
        b_ub.append(-requirements['energy_kcal'] * 0.8)

    # エネルギー上限制約
    if 'energy_kcal' in upper_limits and 'energy_kcal' in foods.columns:
        coeffs = foods['energy_kcal'].fillna(0).values
        A_ub.append(coeffs)
        b_ub.append(upper_limits['energy_kcal'])

    A_ub = np.array(A_ub) if A_ub else None
    b_ub = np.array(b_ub) if b_ub else None
    bounds = [(0, max_food_amount_g / 100) for _ in range(n_foods)]

    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

    if not result.success:
        # さらに緩和: エネルギー制約なしでカロリー最大化
        return _optimize_max_nutrition(foods, max_food_amount_g)

    return _extract_amounts(result.x, food_names)


def _optimize_max_nutrition(
    foods: pd.DataFrame,
    max_food_amount_g: float,
) -> dict:
    """栄養価を最大化（制約が厳しすぎる場合のフォールバック）

    コストを無視し、カロリーを最大化する。
    """
    n_foods = len(foods)
    food_names = foods['food_name'].tolist()

    # エネルギーを最大化（負の係数で最小化問題に変換）
    if 'energy_kcal' in foods.columns:
        c = -foods['energy_kcal'].fillna(0).values
    else:
        # エネルギー列がない場合は単純に均等配分
        c = np.ones(n_foods)

    bounds = [(0, max_food_amount_g / 100) for _ in range(n_foods)]

    result = linprog(c, bounds=bounds, method='highs')

    if not result.success:
        return {}

    return _extract_amounts(result.x, food_names)


def _extract_amounts(x: np.ndarray, food_names: list) -> dict:
    """最適化結果から食材量を抽出"""
    amounts = {}
    for i, amount in enumerate(x):
        if amount > 0.01:
            amounts[food_names[i]] = round(amount * 100, 1)
    return amounts


def calculate_totals(foods: pd.DataFrame, amounts: dict) -> dict:
    """選択された食材の合計栄養価とコストを計算"""
    # 全栄養素を初期化
    totals = {'total_cost': 0}
    for col in foods.columns:
        if col not in ['food_name', 'nutrition_name', 'price_per_100g',
                       'source_price', 'source_nutrition', 'date']:
            totals[col] = 0

    for food_name, amount_g in amounts.items():
        food_row = foods[foods['food_name'] == food_name].iloc[0]
        ratio = amount_g / 100

        totals['total_cost'] += food_row['price_per_100g'] * ratio
        for col in totals.keys():
            if col != 'total_cost' and col in food_row:
                val = food_row[col]
                if pd.notna(val):
                    totals[col] += val * ratio

    return {k: round(v, 2) for k, v in totals.items()}


def main():
    print("Loading food data...")
    foods = load_food_data()
    print(f"  Loaded {len(foods)} food items")

    print("\n=== 12-14歳男子（身体活動レベル普通）の最適化 ===")
    print(f"制約栄養素数: {len(DAILY_REQUIREMENTS)}")

    amounts = optimize_diet(foods)

    if amounts:
        print("\n" + "=" * 70)
        print("最適な食材の組み合わせ（1日あたり）")
        print("=" * 70)

        sorted_amounts = sorted(amounts.items(), key=lambda x: x[1], reverse=True)
        for food, amount in sorted_amounts:
            price_row = foods[foods['food_name'] == food].iloc[0]
            cost = price_row['price_per_100g'] * amount / 100
            print(f"  {food}: {amount:.0f}g (¥{cost:.0f})")

        totals = calculate_totals(foods, amounts)

        print("\n" + "-" * 70)
        print("栄養素達成状況:")
        print("-" * 70)
        print(f"  {'栄養素':<20} {'摂取量':>12} {'目標':>12} {'達成率':>10}")
        print("-" * 70)

        for nutrient, req in DAILY_REQUIREMENTS.items():
            actual = totals.get(nutrient, 0)
            ratio = actual / req * 100 if req > 0 else 0
            name = NUTRIENT_NAMES.get(nutrient, nutrient)
            unit = "kcal" if "kcal" in nutrient else ("μg" if "_ug" in nutrient else ("mg" if "_mg" in nutrient else "g"))
            status = "✓" if ratio >= 100 else "✗"
            print(f"  {name:<18} {actual:>10.1f}{unit:>3} {req:>10.1f}{unit:>3} {ratio:>8.0f}% {status}")

        print("-" * 70)
        print(f"  総コスト: ¥{totals['total_cost']:.0f}/日 (約¥{totals['total_cost']*30:.0f}/月)")
        print("=" * 70)
    else:
        print("Optimization failed or no data available")


if __name__ == "__main__":
    main()
