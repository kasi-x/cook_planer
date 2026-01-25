"""栄養価最適化計算

線形計画法を用いて、最低コストで基準栄養価を満たす
食材の組み合わせを計算する
"""

import pandas as pd
import numpy as np
from scipy.optimize import linprog
from pathlib import Path
import json

DATA_DIR = Path(__file__).parent.parent / "data"
MERGED_DIR = DATA_DIR / "merged"
PROCESSED_DIR = DATA_DIR / "processed"


def load_dietary_standards():
    """栄養基準データをJSONから読み込み"""
    json_path = PROCESSED_DIR / "dietary_standards.json"
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    # フォールバック: スクリプトから直接インポート
    from src.scrapers.mhlw_dietary_standards import (
        AGE_GROUPS,
        DIETARY_REFERENCE_INTAKES,
        UPPER_LIMITS,
        SCHOOL_LUNCH_STANDARDS,
    )
    return {
        "age_groups": AGE_GROUPS,
        "dietary_reference_intakes": DIETARY_REFERENCE_INTAKES,
        "upper_limits": UPPER_LIMITS,
        "school_lunch_standards": SCHOOL_LUNCH_STANDARDS,
    }


# 栄養基準データを読み込み
_STANDARDS = None

def get_standards():
    global _STANDARDS
    if _STANDARDS is None:
        _STANDARDS = load_dietary_standards()
    return _STANDARDS


# 年齢グループ定義
AGE_GROUPS = {
    "1-2": {"label": "1-2歳", "min_age": 1, "max_age": 2},
    "3-5": {"label": "3-5歳", "min_age": 3, "max_age": 5},
    "6-7": {"label": "6-7歳", "min_age": 6, "max_age": 7},
    "8-9": {"label": "8-9歳", "min_age": 8, "max_age": 9},
    "10-11": {"label": "10-11歳", "min_age": 10, "max_age": 11},
    "12-14": {"label": "12-14歳", "min_age": 12, "max_age": 14},
    "15-17": {"label": "15-17歳", "min_age": 15, "max_age": 17},
    "18-29": {"label": "18-29歳", "min_age": 18, "max_age": 29},
    "30-49": {"label": "30-49歳", "min_age": 30, "max_age": 49},
    "50-64": {"label": "50-64歳", "min_age": 50, "max_age": 64},
    "65-74": {"label": "65-74歳", "min_age": 65, "max_age": 74},
    "75+": {"label": "75歳以上", "min_age": 75, "max_age": 120},
}


def get_age_group_id(age: int) -> str:
    """年齢から年齢グループIDを取得"""
    for group_id, group_info in AGE_GROUPS.items():
        if group_info["min_age"] <= age <= group_info["max_age"]:
            return group_id
    # 範囲外の場合
    if age < 1:
        return "1-2"
    return "75+"


# 年齢・性別から基準を取得する関数
def get_requirements_for_age_gender(age: int, gender: str = "male") -> dict:
    """年齢と性別に基づいて適切な栄養基準を返す"""
    standards = get_standards()
    gender_key = "female" if gender.lower() in ["female", "f", "女", "女性"] else "male"
    age_group_id = get_age_group_id(age)

    requirements = standards["dietary_reference_intakes"][gender_key].get(
        age_group_id,
        standards["dietary_reference_intakes"][gender_key]["18-29"]
    )

    # Noneと不要なキーを除外
    excluded_keys = {"fat_percent", "carbohydrate_percent", "salt_g", "sodium_mg"}
    return {k: v for k, v in requirements.items() if v is not None and k not in excluded_keys}


def get_upper_limits_for_age_gender(age: int, gender: str = "male") -> dict:
    """年齢と性別に基づいて耐容上限量を取得"""
    standards = get_standards()
    gender_key = "female" if gender.lower() in ["female", "f", "女", "女性"] else "male"
    age_group_id = get_age_group_id(age)

    return standards["upper_limits"][gender_key].get(
        age_group_id,
        standards["upper_limits"][gender_key]["18-29"]
    )


def get_school_lunch_requirements(age: int) -> dict:
    """年齢に基づいて給食基準を取得"""
    standards = get_standards()
    school_standards = standards["school_lunch_standards"]

    if age <= 7:
        return school_standards["elementary_low"]
    elif age <= 9:
        return school_standards["elementary_mid"]
    elif age <= 11:
        return school_standards["elementary_high"]
    else:
        return school_standards["junior_high"]


def get_requirements_for_meal_type(
    meal_type: str,
    age: int = 23,
    gender: str = "male"
) -> dict:
    """食事タイプに基づいて栄養基準を返す

    Args:
        meal_type: "daily" (1日分), "per_meal" (一食分), "school_lunch" (給食基準)
        age: 年齢（daily, per_mealの場合に使用）
        gender: 性別（daily, per_mealの場合に使用）
    """
    if meal_type == "school_lunch":
        req = get_school_lunch_requirements(age)
        # 不要なキーを除外
        excluded_keys = {"fat_percent", "carbohydrate_percent", "salt_g", "sodium_mg"}
        return {k: v for k, v in req.items() if v is not None and k not in excluded_keys}

    daily_req = get_requirements_for_age_gender(age, gender)

    if meal_type == "per_meal":
        # 一食分 = 1日の1/3
        return {k: v / 3 for k, v in daily_req.items()}

    # daily (デフォルト)
    return daily_req


# 18-29歳男性のデフォルト値（後方互換性）
DAILY_REQUIREMENTS = get_requirements_for_age_gender(25, "male")
DAILY_REQUIREMENTS_MALE = DAILY_REQUIREMENTS
DAILY_REQUIREMENTS_FEMALE = get_requirements_for_age_gender(25, "female")

# 栄養素の上限（過剰摂取防止）
DAILY_UPPER_LIMITS = get_upper_limits_for_age_gender(25, "male")

# 栄養素の日本語名
NUTRIENT_NAMES = {
    "energy_kcal": "エネルギー",
    "protein_g": "たんぱく質",
    "fiber_g": "食物繊維",
    "potassium_mg": "カリウム",
    "calcium_mg": "カルシウム",
    "magnesium_mg": "マグネシウム",
    "phosphorus_mg": "リン",
    "iron_mg": "鉄",
    "zinc_mg": "亜鉛",
    "copper_mg": "銅",
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
    "salt_g": "食塩相当量",
}

# 栄養素の単位
NUTRIENT_UNITS = {
    "energy_kcal": "kcal",
    "protein_g": "g",
    "fiber_g": "g",
    "potassium_mg": "mg",
    "calcium_mg": "mg",
    "magnesium_mg": "mg",
    "phosphorus_mg": "mg",
    "iron_mg": "mg",
    "zinc_mg": "mg",
    "copper_mg": "mg",
    "vitamin_a_ug": "μg",
    "vitamin_d_ug": "μg",
    "vitamin_e_mg": "mg",
    "vitamin_k_ug": "μg",
    "vitamin_b1_mg": "mg",
    "vitamin_b2_mg": "mg",
    "niacin_mg": "mg",
    "vitamin_b6_mg": "mg",
    "vitamin_b12_ug": "μg",
    "folate_ug": "μg",
    "pantothenic_mg": "mg",
    "vitamin_c_mg": "mg",
    "salt_g": "g",
}


def load_food_data() -> pd.DataFrame:
    """結合された食品データを読み込み"""
    csv_path = MERGED_DIR / "food_price_nutrition.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Data file not found: {csv_path}")
    return pd.read_csv(csv_path)


def get_food_row(foods: pd.DataFrame, food_name: str) -> pd.Series | None:
    """食品名から該当する行を安全に取得"""
    matches = foods[foods['food_name'] == food_name]
    if matches.empty:
        return None
    return matches.iloc[0]


def _extract_amounts(result_x: np.ndarray, food_names: list) -> dict:
    """最適化結果から食品量を抽出（1g以上のみ）"""
    amounts = {}
    for i, amount in enumerate(result_x):
        if amount >= 1:  # 1g以上のみ採用
            amounts[food_names[i]] = round(amount, 1)
    return amounts


def _optimize_strict(
    foods: pd.DataFrame,
    requirements: dict,
    upper_limits: dict,
    max_food_amount_g: float,
    fixed_foods: dict = None,
    min_foods: dict = None,
) -> dict | None:
    """厳密モード: 全栄養素を満たす最小コスト解を求める"""
    if fixed_foods is None:
        fixed_foods = {}
    if min_foods is None:
        min_foods = {}

    # 固定食品の栄養価を事前計算
    fixed_nutrition = {}
    fixed_cost = 0
    for food_name, amount_g in fixed_foods.items():
        food_row = get_food_row(foods, food_name)
        if food_row is None:
            continue
        ratio = amount_g / 100
        fixed_cost += food_row['price_per_100g'] * ratio
        for nutrient in requirements.keys():
            if nutrient in food_row:
                val = food_row[nutrient]
                if pd.notna(val):
                    fixed_nutrition[nutrient] = fixed_nutrition.get(nutrient, 0) + val * ratio

    # 固定食品を除いた食品リスト
    variable_foods = foods[~foods['food_name'].isin(fixed_foods.keys())].copy()
    if variable_foods.empty:
        # 全食品が固定の場合
        return fixed_foods if fixed_foods else None

    n_foods = len(variable_foods)
    food_names = variable_foods['food_name'].tolist()

    # 目的関数: 100gあたりのコスト（最小化）
    c = variable_foods['price_per_100g'].values / 100

    # 不等式制約
    A_ub = []
    b_ub = []

    # 各栄養素の下限制約（必要量以上）
    # 注: 栄養素データは100gあたり、変数xはグラム単位なので係数を/100する
    for nutrient, required in requirements.items():
        if nutrient not in variable_foods.columns:
            continue
        # 固定食品からの栄養を差し引いた必要量
        remaining_required = required - fixed_nutrition.get(nutrient, 0)
        if remaining_required <= 0:
            continue  # すでに満たしている

        # 係数は100gあたりの値 / 100 = 1gあたりの値
        coeffs = -variable_foods[nutrient].fillna(0).values / 100
        A_ub.append(coeffs)
        b_ub.append(-remaining_required)

    # 上限制約（過剰摂取防止）
    for nutrient, upper in upper_limits.items():
        if nutrient not in variable_foods.columns:
            continue
        # 固定食品からの栄養を差し引いた上限
        remaining_upper = upper - fixed_nutrition.get(nutrient, 0)
        if remaining_upper <= 0:
            continue  # すでに上限超過（解なし）

        # 係数は100gあたりの値 / 100 = 1gあたりの値
        coeffs = variable_foods[nutrient].fillna(0).values / 100
        A_ub.append(coeffs)
        b_ub.append(remaining_upper)

    # 総重量制限（固定食品分を除く）
    fixed_total = sum(fixed_foods.values())
    remaining_max = max_food_amount_g - fixed_total
    A_ub.append(np.ones(n_foods))
    b_ub.append(remaining_max)

    # 変数の範囲（min_foodsがある場合は最小量を設定）
    bounds = []
    for food_name in food_names:
        min_amount = min_foods.get(food_name, 0)
        bounds.append((min_amount, None))

    if not A_ub:
        return None

    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

    if result.success:
        amounts = _extract_amounts(result.x, food_names)
        # min_foodsの最小量を確保（_extract_amountsで1g未満が切られる場合対策）
        for food_name, min_amount in min_foods.items():
            if food_name in food_names and min_amount >= 1:
                if food_name not in amounts or amounts[food_name] < min_amount:
                    amounts[food_name] = round(min_amount, 1)
        # 固定食品を追加
        amounts.update(fixed_foods)
        return amounts
    return None


def optimize_best_effort(
    foods: pd.DataFrame,
    requirements: dict,
    max_food_amount_g: float,
    fixed_foods: dict = None,
    min_foods: dict = None,
    budget_limit: float = None,
) -> dict:
    """ベストエフォートモード: 必ず何かを返す（失敗しない）

    制約を一切設けず、コスパの良い食品を予算内で選ぶ
    """
    if fixed_foods is None:
        fixed_foods = {}
    if min_foods is None:
        min_foods = {}

    # 固定食品の栄養価とコストを計算
    fixed_nutrition = {}
    fixed_cost = 0
    for food_name, amount_g in fixed_foods.items():
        food_row = get_food_row(foods, food_name)
        if food_row is None:
            continue
        ratio = amount_g / 100
        fixed_cost += food_row['price_per_100g'] * ratio
        for nutrient in requirements.keys():
            if nutrient in food_row:
                val = food_row[nutrient]
                if pd.notna(val):
                    fixed_nutrition[nutrient] = fixed_nutrition.get(nutrient, 0) + val * ratio

    # 固定食品を除いた食品リスト
    variable_foods = foods[~foods['food_name'].isin(fixed_foods.keys())].copy()
    if variable_foods.empty:
        return fixed_foods if fixed_foods else {}

    # 残りの重量枠
    fixed_total = sum(fixed_foods.values())
    remaining_weight = max_food_amount_g - fixed_total

    # 残りの予算枠
    if budget_limit is not None:
        remaining_budget = budget_limit - fixed_cost
    else:
        remaining_budget = float('inf')

    # コスパスコアを計算（栄養価/価格）
    def calc_score(row):
        price = row['price_per_100g']
        if price <= 0:
            return 0
        score = 0
        # エネルギーとたんぱく質を重視
        score += (row.get('energy_kcal', 0) or 0) / price * 0.5
        score += (row.get('protein_g', 0) or 0) / price * 10
        score += (row.get('calcium_mg', 0) or 0) / price * 0.1
        score += (row.get('iron_mg', 0) or 0) / price * 5
        return score

    variable_foods['score'] = variable_foods.apply(calc_score, axis=1)
    variable_foods = variable_foods.sort_values('score', ascending=False)

    # コスパの良い食品から順に追加
    amounts = dict(fixed_foods)
    total_cost = fixed_cost
    total_weight = fixed_total

    # まずmin_foodsの最小量を確保
    for food_name, min_amount in min_foods.items():
        if food_name in fixed_foods:
            continue  # 固定食品はスキップ
        food_row = get_food_row(foods, food_name)
        if food_row is None:
            continue
        price_per_g = food_row['price_per_100g'] / 100
        amount = min(min_amount, remaining_weight)
        if amount > 0:
            amounts[food_name] = round(amount, 1)
            total_cost += amount * price_per_g
            total_weight += amount
            remaining_weight -= amount
            remaining_budget -= amount * price_per_g

    for _, row in variable_foods.iterrows():
        food_name = row['food_name']
        if food_name in amounts:
            continue  # すでに追加済み
        price_per_g = row['price_per_100g'] / 100

        # 追加できる最大量を計算
        max_by_weight = remaining_weight
        max_by_budget = remaining_budget / price_per_g if price_per_g > 0 else remaining_weight

        # 最大100gずつ追加
        amount = min(100, max_by_weight, max_by_budget)
        if amount < 10:  # 10g未満は追加しない
            continue

        amounts[food_name] = round(amount, 1)
        total_cost += amount * price_per_g
        total_weight += amount
        remaining_weight -= amount
        remaining_budget -= amount * price_per_g

        if remaining_weight < 10 or remaining_budget < 1:
            break

    return amounts


def optimize_cost_limited(
    foods: pd.DataFrame,
    requirements: dict,
    upper_limits: dict,
    max_food_amount_g: float,
    fixed_foods: dict = None,
    max_cost: float = 500,
    min_foods: dict = None,
) -> dict:
    """コスト制限モード: 予算内で最大の栄養価を得る"""
    if fixed_foods is None:
        fixed_foods = {}
    if min_foods is None:
        min_foods = {}

    # 固定食品の栄養価とコストを計算
    fixed_nutrition = {}
    fixed_cost = 0
    for food_name, amount_g in fixed_foods.items():
        food_row = get_food_row(foods, food_name)
        if food_row is None:
            continue
        ratio = amount_g / 100
        fixed_cost += food_row['price_per_100g'] * ratio
        for nutrient in requirements.keys():
            if nutrient in food_row:
                val = food_row[nutrient]
                if pd.notna(val):
                    fixed_nutrition[nutrient] = fixed_nutrition.get(nutrient, 0) + val * ratio

    # 固定食品を除いた食品リスト
    variable_foods = foods[~foods['food_name'].isin(fixed_foods.keys())].copy()
    if variable_foods.empty:
        return fixed_foods if fixed_foods else {}

    n_foods = len(variable_foods)
    food_names = variable_foods['food_name'].tolist()

    # 目的関数: 栄養価の合計を最大化（最小化のため符号反転）
    # 重要な栄養素に重み付け
    nutrient_scores = np.zeros(n_foods)
    for nutrient, required in requirements.items():
        if nutrient not in variable_foods.columns or required <= 0:
            continue
        remaining = required - fixed_nutrition.get(nutrient, 0)
        if remaining <= 0:
            continue
        weight = 1
        if nutrient == 'energy_kcal':
            weight = 2
        elif nutrient == 'protein_g':
            weight = 3
        nutrient_values = variable_foods[nutrient].fillna(0).values / 100
        nutrient_scores += (nutrient_values / remaining) * weight

    c = -nutrient_scores  # 最大化を最小化に変換

    A_ub = []
    b_ub = []

    # コスト制約
    remaining_budget = max_cost - fixed_cost
    cost_coeffs = variable_foods['price_per_100g'].values / 100
    A_ub.append(cost_coeffs)
    b_ub.append(remaining_budget)

    # 総重量制限
    fixed_total = sum(fixed_foods.values())
    A_ub.append(np.ones(n_foods))
    b_ub.append(max_food_amount_g - fixed_total)

    # 上限制約（緩め）
    for nutrient, upper in upper_limits.items():
        if nutrient not in variable_foods.columns:
            continue
        remaining_upper = upper * 1.5 - fixed_nutrition.get(nutrient, 0)
        if remaining_upper <= 0:
            continue
        coeffs = variable_foods[nutrient].fillna(0).values / 100
        A_ub.append(coeffs)
        b_ub.append(remaining_upper)

    # 変数の範囲（min_foodsがある場合は最小量を設定）
    bounds = []
    for food_name in food_names:
        min_amount = min_foods.get(food_name, 0)
        bounds.append((min_amount, None))

    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

    if result.success:
        amounts = _extract_amounts(result.x, food_names)
        # min_foodsの最小量を確保
        for food_name, min_amount in min_foods.items():
            if food_name in food_names and min_amount >= 1:
                if food_name not in amounts or amounts[food_name] < min_amount:
                    amounts[food_name] = round(min_amount, 1)
        amounts.update(fixed_foods)
        return amounts

    # 失敗した場合はベストエフォートに切り替え
    return optimize_best_effort(foods, requirements, max_food_amount_g, fixed_foods, min_foods, max_cost)


def optimize_calorie_focused(
    foods: pd.DataFrame,
    requirements: dict,
    upper_limits: dict,
    max_food_amount_g: float,
    fixed_foods: dict = None,
    min_foods: dict = None,
) -> dict | None:
    """カロリー重視モード: カロリーを確実に満たしつつコスト最小化"""
    if fixed_foods is None:
        fixed_foods = {}
    if min_foods is None:
        min_foods = {}

    # 固定食品の栄養価を事前計算
    fixed_nutrition = {}
    for food_name, amount_g in fixed_foods.items():
        food_row = get_food_row(foods, food_name)
        if food_row is None:
            continue
        ratio = amount_g / 100
        for nutrient in requirements.keys():
            if nutrient in food_row:
                val = food_row[nutrient]
                if pd.notna(val):
                    fixed_nutrition[nutrient] = fixed_nutrition.get(nutrient, 0) + val * ratio

    # 固定食品を除いた食品リスト
    variable_foods = foods[~foods['food_name'].isin(fixed_foods.keys())].copy()
    if variable_foods.empty:
        return fixed_foods if fixed_foods else None

    n_foods = len(variable_foods)
    food_names = variable_foods['food_name'].tolist()

    # 目的関数: コスト最小化
    c = variable_foods['price_per_100g'].values / 100

    A_ub = []
    b_ub = []

    # エネルギー制約（必須）
    # 注: 栄養素データは100gあたり、変数xはグラム単位なので係数を/100する
    if 'energy_kcal' in requirements and 'energy_kcal' in variable_foods.columns:
        remaining_energy = requirements['energy_kcal'] - fixed_nutrition.get('energy_kcal', 0)
        if remaining_energy > 0:
            coeffs = -variable_foods['energy_kcal'].fillna(0).values / 100
            A_ub.append(coeffs)
            b_ub.append(-remaining_energy)

    # たんぱく質制約（重要）
    if 'protein_g' in requirements and 'protein_g' in variable_foods.columns:
        remaining_protein = requirements['protein_g'] - fixed_nutrition.get('protein_g', 0)
        if remaining_protein > 0:
            coeffs = -variable_foods['protein_g'].fillna(0).values / 100
            A_ub.append(coeffs)
            b_ub.append(-remaining_protein)

    # 上限制約
    for nutrient, upper in upper_limits.items():
        if nutrient not in variable_foods.columns:
            continue
        remaining_upper = upper - fixed_nutrition.get(nutrient, 0)
        if remaining_upper <= 0:
            continue
        coeffs = variable_foods[nutrient].fillna(0).values / 100
        A_ub.append(coeffs)
        b_ub.append(remaining_upper)

    # 総重量制限
    fixed_total = sum(fixed_foods.values())
    A_ub.append(np.ones(n_foods))
    b_ub.append(max_food_amount_g - fixed_total)

    # 変数の範囲（min_foodsがある場合は最小量を設定）
    bounds = []
    for food_name in food_names:
        min_amount = min_foods.get(food_name, 0)
        bounds.append((min_amount, None))

    if not A_ub:
        return None

    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

    if result.success:
        amounts = _extract_amounts(result.x, food_names)
        # min_foodsの最小量を確保
        for food_name, min_amount in min_foods.items():
            if food_name in food_names and min_amount >= 1:
                if food_name not in amounts or amounts[food_name] < min_amount:
                    amounts[food_name] = round(min_amount, 1)
        amounts.update(fixed_foods)
        return amounts
    return None


def optimize_with_score(
    foods: pd.DataFrame,
    requirements: dict,
    upper_limits: dict,
    max_food_amount_g: float,
    fixed_foods: dict = None,
    scoring_params: dict = None,
    min_foods: dict = None,
) -> dict | None:
    """スコア最適化モード: カスタムスコアを最大化"""
    if fixed_foods is None:
        fixed_foods = {}
    if min_foods is None:
        min_foods = {}
    if scoring_params is None:
        scoring_params = {
            'deficit_penalty': 10,
            'cost_bonus': 1,
            'calorie_weight': 2,
            'protein_weight': 1.5,
            'vitamin_weight': 1,
            'mineral_weight': 1,
        }

    # 固定食品の栄養価を事前計算
    fixed_nutrition = {}
    fixed_cost = 0
    for food_name, amount_g in fixed_foods.items():
        food_row = get_food_row(foods, food_name)
        if food_row is None:
            continue
        ratio = amount_g / 100
        fixed_cost += food_row['price_per_100g'] * ratio
        for nutrient in requirements.keys():
            if nutrient in food_row:
                val = food_row[nutrient]
                if pd.notna(val):
                    fixed_nutrition[nutrient] = fixed_nutrition.get(nutrient, 0) + val * ratio

    # 固定食品を除いた食品リスト
    variable_foods = foods[~foods['food_name'].isin(fixed_foods.keys())].copy()
    if variable_foods.empty:
        return fixed_foods if fixed_foods else None

    n_foods = len(variable_foods)
    food_names = variable_foods['food_name'].tolist()

    # 栄養素の重み付け係数を計算
    nutrient_weights = {}
    calorie_nutrients = {'energy_kcal'}
    protein_nutrients = {'protein_g'}
    vitamin_nutrients = {'vitamin_a_ug', 'vitamin_b1_mg', 'vitamin_b2_mg', 'vitamin_b6_mg',
                         'vitamin_b12_ug', 'vitamin_c_mg', 'vitamin_d_ug', 'vitamin_e_mg',
                         'vitamin_k_ug', 'niacin_mg', 'folate_ug', 'pantothenic_mg'}
    mineral_nutrients = {'calcium_mg', 'iron_mg', 'magnesium_mg', 'zinc_mg',
                         'potassium_mg', 'phosphorus_mg', 'copper_mg'}

    for nutrient in requirements.keys():
        if nutrient in calorie_nutrients:
            nutrient_weights[nutrient] = scoring_params.get('calorie_weight', 2)
        elif nutrient in protein_nutrients:
            nutrient_weights[nutrient] = scoring_params.get('protein_weight', 1.5)
        elif nutrient in vitamin_nutrients:
            nutrient_weights[nutrient] = scoring_params.get('vitamin_weight', 1)
        elif nutrient in mineral_nutrients:
            nutrient_weights[nutrient] = scoring_params.get('mineral_weight', 1)
        else:
            nutrient_weights[nutrient] = 1

    # 目的関数: スコア最大化（線形計画法では最小化なので符号反転）
    # スコア = Σ(栄養達成度 × 重み) - コストペナルティ
    deficit_penalty = scoring_params.get('deficit_penalty', 10)
    cost_bonus = scoring_params.get('cost_bonus', 1)

    # 各食品の栄養貢献スコアを計算
    nutrient_scores = np.zeros(n_foods)
    for nutrient, required in requirements.items():
        if nutrient not in variable_foods.columns or required <= 0:
            continue
        remaining = required - fixed_nutrition.get(nutrient, 0)
        if remaining <= 0:
            continue
        # 正規化した栄養価 × 重み
        # 注: 栄養素データは100gあたり、変数xはグラム単位なので係数を/100する
        weight = nutrient_weights.get(nutrient, 1)
        nutrient_values = variable_foods[nutrient].fillna(0).values / 100
        nutrient_scores += (nutrient_values / remaining) * weight * deficit_penalty

    # コストペナルティを引く
    cost_penalty = variable_foods['price_per_100g'].values / 100 * cost_bonus

    # 最大化を最小化に変換
    c = -(nutrient_scores - cost_penalty)

    A_ub = []
    b_ub = []

    # 上限制約
    # 注: 栄養素データは100gあたり、変数xはグラム単位なので係数を/100する
    for nutrient, upper in upper_limits.items():
        if nutrient not in variable_foods.columns:
            continue
        remaining_upper = upper - fixed_nutrition.get(nutrient, 0)
        if remaining_upper <= 0:
            continue
        coeffs = variable_foods[nutrient].fillna(0).values / 100
        A_ub.append(coeffs)
        b_ub.append(remaining_upper)

    # 総重量制限
    fixed_total = sum(fixed_foods.values())
    A_ub.append(np.ones(n_foods))
    b_ub.append(max_food_amount_g - fixed_total)

    # 変数の範囲（min_foodsがある場合は最小量を設定）
    bounds = []
    for food_name in food_names:
        min_amount = min_foods.get(food_name, 0)
        bounds.append((min_amount, None))

    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

    if result.success:
        amounts = _extract_amounts(result.x, food_names)
        # min_foodsの最小量を確保
        for food_name, min_amount in min_foods.items():
            if food_name in food_names and min_amount >= 1:
                if food_name not in amounts or amounts[food_name] < min_amount:
                    amounts[food_name] = round(min_amount, 1)
        amounts.update(fixed_foods)
        return amounts
    return None


def optimize_diet(
    foods: pd.DataFrame,
    requirements: dict = None,
    upper_limits: dict = None,
    max_food_amount_g: float = 1500,
    fixed_foods: dict = None,
    min_foods: dict = None,
) -> dict | None:
    """バランスモード: 厳密解を試し、失敗したら段階的に緩和"""
    if requirements is None:
        requirements = DAILY_REQUIREMENTS
    if upper_limits is None:
        upper_limits = DAILY_UPPER_LIMITS
    if fixed_foods is None:
        fixed_foods = {}
    if min_foods is None:
        min_foods = {}

    # まず厳密モードを試す（上限制約付き）
    result = _optimize_strict(foods, requirements, upper_limits, max_food_amount_g, fixed_foods, min_foods)
    if result:
        return result

    # 上限制約を緩和して試す
    relaxed_upper = {k: v * 1.5 for k, v in upper_limits.items()}
    result = _optimize_strict(foods, requirements, relaxed_upper, max_food_amount_g, fixed_foods, min_foods)
    if result:
        return result

    # 段階的に栄養基準を緩和（95% → 90% → 85% → 80%）
    for ratio in [0.95, 0.9, 0.85, 0.8]:
        relaxed_req = {k: v * ratio for k, v in requirements.items()}
        # 上限も緩和
        result = _optimize_strict(foods, relaxed_req, relaxed_upper, max_food_amount_g, fixed_foods, min_foods)
        if result:
            return result

    # 重要な栄養素のみに制限して試す
    essential_nutrients = ['energy_kcal', 'protein_g', 'calcium_mg', 'iron_mg', 'vitamin_a_ug', 'vitamin_c_mg']
    essential_req = {k: v for k, v in requirements.items() if k in essential_nutrients}
    result = _optimize_strict(foods, essential_req, {}, max_food_amount_g, fixed_foods, min_foods)
    if result:
        return result

    # カロリー重視モード（上限なし）
    result = optimize_calorie_focused(foods, requirements, {}, max_food_amount_g, fixed_foods, min_foods)
    if result:
        return result

    # 最終手段: ベストエフォート（必ず何かを返す）
    return optimize_best_effort(foods, requirements, max_food_amount_g, fixed_foods, min_foods)


def calculate_totals(foods: pd.DataFrame, amounts: dict) -> dict:
    """選択された食材の合計栄養価とコストを計算"""
    # 全栄養素を初期化
    totals = {'total_cost': 0}
    for col in foods.columns:
        if col not in ['food_name', 'nutrition_name', 'price_per_100g',
                       'source_price', 'source_nutrition', 'date']:
            totals[col] = 0

    for food_name, amount_g in amounts.items():
        food_row = get_food_row(foods, food_name)
        if food_row is None:
            continue  # 見つからない食品はスキップ
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
    requirements = get_requirements_for_age_gender(13, "male")
    upper_limits = get_upper_limits_for_age_gender(13, "male")
    print(f"制約栄養素数: {len(requirements)}")

    amounts = optimize_diet(foods, requirements, upper_limits)

    if amounts:
        print("\n" + "=" * 70)
        print("最適な食材の組み合わせ（1日あたり）")
        print("=" * 70)

        sorted_amounts = sorted(amounts.items(), key=lambda x: x[1], reverse=True)
        for food, amount in sorted_amounts:
            price_row = get_food_row(foods, food)
            if price_row is not None:
                cost = price_row['price_per_100g'] * amount / 100
                print(f"  {food}: {amount:.0f}g (¥{cost:.0f})")

        totals = calculate_totals(foods, amounts)

        print("\n" + "-" * 70)
        print("栄養素達成状況:")
        print("-" * 70)
        print(f"  {'栄養素':<20} {'摂取量':>12} {'目標':>12} {'達成率':>10}")
        print("-" * 70)

        for nutrient, req in requirements.items():
            actual = totals.get(nutrient, 0)
            ratio = actual / req * 100 if req > 0 else 0
            name = NUTRIENT_NAMES.get(nutrient, nutrient)
            unit = NUTRIENT_UNITS.get(nutrient, "")
            status = "✓" if ratio >= 100 else ""
            print(f"  {name:<15} {actual:>10.1f}{unit:>4} {req:>10.1f}{unit:>4} {ratio:>8.0f}% {status}")

        print("-" * 70)
        print(f"  総コスト: ¥{totals['total_cost']:.0f}/日 (約¥{totals['total_cost'] * 30:.0f}/月)")
        print("=" * 70)
    else:
        print("最適化に失敗しました。制約が厳しすぎる可能性があります。")


if __name__ == "__main__":
    main()
