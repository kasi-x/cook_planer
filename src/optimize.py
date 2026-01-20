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
    fixed_foods: dict[str, float] = None,
) -> dict:
    """最小コストで栄養要件を満たす食材量を計算

    まず全制約を満たす最適化を試み、失敗した場合は
    制約を緩和してベストエフォートの結果を返す。

    Args:
        fixed_foods: {食品名: 固定量(g)} の辞書。指定された食品は必ずその量を使用。
    """
    if requirements is None:
        requirements = DAILY_REQUIREMENTS
    if upper_limits is None:
        upper_limits = DAILY_UPPER_LIMITS
    if fixed_foods is None:
        fixed_foods = {}

    if foods.empty:
        return {}

    # まず全制約での最適化を試行
    result = _optimize_strict(foods, requirements, upper_limits, max_food_amount_g, fixed_foods)
    if result:
        return result

    # 失敗した場合は緩和版を試行
    return _optimize_relaxed(foods, requirements, upper_limits, max_food_amount_g, fixed_foods)


def _optimize_strict(
    foods: pd.DataFrame,
    requirements: dict,
    upper_limits: dict,
    max_food_amount_g: float,
    fixed_foods: dict[str, float] = None,
) -> dict:
    """全栄養素制約を満たす最適化（厳密版）"""
    if fixed_foods is None:
        fixed_foods = {}

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

    # 固定食品は上下限を同じ値に設定
    bounds = []
    for name in food_names:
        if name in fixed_foods:
            fixed_val = fixed_foods[name] / 100
            bounds.append((fixed_val, fixed_val))
        else:
            bounds.append((0, max_food_amount_g / 100))

    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

    if not result.success:
        return {}

    return _extract_amounts(result.x, food_names)


def _optimize_relaxed(
    foods: pd.DataFrame,
    requirements: dict,
    upper_limits: dict,
    max_food_amount_g: float,
    fixed_foods: dict[str, float] = None,
) -> dict:
    """制約を緩和した最適化（ベストエフォート版）

    エネルギー目標を達成しつつコストを最小化する。
    他の栄養素は可能な限り摂取する。
    """
    if fixed_foods is None:
        fixed_foods = {}

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

    # 固定食品は上下限を同じ値に設定
    bounds = []
    for name in food_names:
        if name in fixed_foods:
            fixed_val = fixed_foods[name] / 100
            bounds.append((fixed_val, fixed_val))
        else:
            bounds.append((0, max_food_amount_g / 100))

    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

    if not result.success:
        # さらに緩和: エネルギー制約なしでカロリー最大化
        return _optimize_max_nutrition(foods, max_food_amount_g, fixed_foods)

    return _extract_amounts(result.x, food_names)


def _optimize_max_nutrition(
    foods: pd.DataFrame,
    max_food_amount_g: float,
    fixed_foods: dict[str, float] = None,
) -> dict:
    """栄養価を最大化（制約が厳しすぎる場合のフォールバック）

    コストを無視し、カロリーを最大化する。
    """
    if fixed_foods is None:
        fixed_foods = {}

    n_foods = len(foods)
    food_names = foods['food_name'].tolist()

    # エネルギーを最大化（負の係数で最小化問題に変換）
    if 'energy_kcal' in foods.columns:
        c = -foods['energy_kcal'].fillna(0).values
    else:
        # エネルギー列がない場合は単純に均等配分
        c = np.ones(n_foods)

    # 固定食品は上下限を同じ値に設定
    bounds = []
    for name in food_names:
        if name in fixed_foods:
            fixed_val = fixed_foods[name] / 100
            bounds.append((fixed_val, fixed_val))
        else:
            bounds.append((0, max_food_amount_g / 100))

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


# ========== Strategy-based optimization functions ==========

def optimize_calorie_focused(
    foods: pd.DataFrame,
    requirements: dict,
    upper_limits: dict,
    max_food_amount_g: float,
    fixed_foods: dict[str, float] = None,
) -> dict:
    """カロリー重視の最適化

    カロリー目標を確実に達成しつつ、コストを最小化する。
    他の栄養素は制約に含めない。
    """
    if fixed_foods is None:
        fixed_foods = {}

    food_names = foods['food_name'].tolist()
    c = foods['price_per_100g'].values

    A_ub = []
    b_ub = []

    # エネルギー下限制約（目標の95%以上）
    if 'energy_kcal' in requirements and 'energy_kcal' in foods.columns:
        energy_coeffs = -foods['energy_kcal'].fillna(0).values
        A_ub.append(energy_coeffs)
        b_ub.append(-requirements['energy_kcal'] * 0.95)

    # エネルギー上限制約（目標の110%以下）
    if 'energy_kcal' in foods.columns:
        coeffs = foods['energy_kcal'].fillna(0).values
        A_ub.append(coeffs)
        target = requirements.get('energy_kcal', 2600)
        b_ub.append(target * 1.1)

    A_ub = np.array(A_ub) if A_ub else None
    b_ub = np.array(b_ub) if b_ub else None

    bounds = []
    for name in food_names:
        if name in fixed_foods:
            fixed_val = fixed_foods[name] / 100
            bounds.append((fixed_val, fixed_val))
        else:
            bounds.append((0, max_food_amount_g / 100))

    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

    if not result.success:
        return {}

    return _extract_amounts(result.x, food_names)


def optimize_with_score(
    foods: pd.DataFrame,
    requirements: dict,
    upper_limits: dict,
    max_food_amount_g: float,
    fixed_foods: dict[str, float] = None,
    scoring_params: dict = None,
) -> dict:
    """カスタムスコアによる最適化

    不足ペナルティとコストボーナスのバランスで最適化する。
    線形計画法でスラック変数を使用して実装。

    目的関数: minimize(cost * cost_weight - sum(slack_i * deficit_penalty * weight_i))
    制約: nutrient_i + slack_i >= requirement_i (各栄養素)
    """
    if fixed_foods is None:
        fixed_foods = {}
    if scoring_params is None:
        scoring_params = {
            'deficit_penalty': 1.0,
            'cost_bonus': 0.1,
            'calorie_weight': 1.0,
            'protein_weight': 1.0,
            'vitamin_weight': 1.0,
            'mineral_weight': 1.0,
        }

    food_names = foods['food_name'].tolist()
    n_foods = len(foods)

    # 栄養素をカテゴリ分け
    calorie_nutrients = ['energy_kcal']
    protein_nutrients = ['protein_g']
    vitamin_nutrients = [k for k in requirements.keys() if 'vitamin' in k or k in ['niacin_mg', 'folate_ug', 'pantothenic_mg']]
    mineral_nutrients = [k for k in requirements.keys() if k in ['potassium_mg', 'calcium_mg', 'magnesium_mg', 'iron_mg', 'zinc_mg']]
    other_nutrients = [k for k in requirements.keys() if k not in calorie_nutrients + protein_nutrients + vitamin_nutrients + mineral_nutrients]

    def get_weight(nutrient):
        if nutrient in calorie_nutrients:
            return scoring_params.get('calorie_weight', 1.0)
        elif nutrient in protein_nutrients:
            return scoring_params.get('protein_weight', 1.0)
        elif nutrient in vitamin_nutrients:
            return scoring_params.get('vitamin_weight', 1.0)
        elif nutrient in mineral_nutrients:
            return scoring_params.get('mineral_weight', 1.0)
        return 1.0

    # 変数: [食品量(n_foods), スラック変数(n_nutrients)]
    nutrient_keys = [k for k in requirements.keys() if k in foods.columns]
    n_nutrients = len(nutrient_keys)

    # 目的関数係数
    # 食品のコスト係数（最小化）
    cost_weight = scoring_params.get('cost_bonus', 0.1)
    deficit_penalty = scoring_params.get('deficit_penalty', 1.0)

    c = np.zeros(n_foods + n_nutrients)
    c[:n_foods] = foods['price_per_100g'].values * cost_weight

    # スラック変数の係数（不足を最小化 = スラックをできるだけ小さく）
    for i, nutrient in enumerate(nutrient_keys):
        weight = get_weight(nutrient)
        req = requirements[nutrient]
        # 正規化: 不足1%あたりのペナルティ
        c[n_foods + i] = deficit_penalty * weight * (100 / req) if req > 0 else 0

    # 制約: 栄養素 + スラック >= 目標
    # つまり: -栄養素 - スラック <= -目標
    A_ub = []
    b_ub = []

    for i, nutrient in enumerate(nutrient_keys):
        row = np.zeros(n_foods + n_nutrients)
        row[:n_foods] = -foods[nutrient].fillna(0).values
        row[n_foods + i] = -1  # スラック変数
        A_ub.append(row)
        b_ub.append(-requirements[nutrient])

    # 上限制約（エネルギーなど）
    for nutrient, limit in upper_limits.items():
        if nutrient in foods.columns:
            row = np.zeros(n_foods + n_nutrients)
            row[:n_foods] = foods[nutrient].fillna(0).values
            A_ub.append(row)
            b_ub.append(limit)

    A_ub = np.array(A_ub) if A_ub else None
    b_ub = np.array(b_ub) if b_ub else None

    # 境界
    bounds = []
    for name in food_names:
        if name in fixed_foods:
            fixed_val = fixed_foods[name] / 100
            bounds.append((fixed_val, fixed_val))
        else:
            bounds.append((0, max_food_amount_g / 100))

    # スラック変数の境界（0以上）
    for _ in range(n_nutrients):
        bounds.append((0, None))

    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

    if not result.success:
        # フォールバック: 緩和版
        return _optimize_relaxed(foods, requirements, upper_limits, max_food_amount_g, fixed_foods)

    return _extract_amounts(result.x[:n_foods], food_names)


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
