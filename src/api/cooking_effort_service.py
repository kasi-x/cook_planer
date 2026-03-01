"""調理工数サービス

各料理の調理時間・難易度を管理し、1日の調理負荷を可視化する。
"""

from .menu_models import DailyMenuData

# 調理法別の基本調理時間（分/100g）
COOKING_TIME_ESTIMATES: dict[str, float] = {
    "生": 0,
    "ゆで": 5,
    "焼き": 8,
    "揚げ": 10,
    "蒸し": 12,
    "炒め": 6,
}

# 食材別の下処理時間（分）- 代表的な食材
PREP_TIME_ESTIMATES: dict[str, float] = {
    # 野菜（皮むき・カット等）
    "じゃがいも": 5, "にんじん": 4, "たまねぎ": 3, "だいこん": 5,
    "キャベツ": 3, "はくさい": 3, "ほうれんそう": 2, "こまつな": 2,
    "ブロッコリー": 3, "かぼちゃ": 6, "ごぼう": 5, "れんこん": 4,
    "なす": 2, "きゅうり": 2, "トマト": 2, "ピーマン": 2,
    "ねぎ": 2, "もやし": 1, "レタス": 1, "アスパラガス": 2,
    "さつまいも": 4, "さといも": 5, "ながいも": 3,
    # きのこ
    "しいたけ": 2, "えのきたけ": 1, "しめじ": 1, "まいたけ": 1, "エリンギ": 1,
    # 魚介
    "さけ": 3, "さば": 4, "あじ": 5, "いわし": 6, "さんま": 4,
    "えび": 5, "あさり": 3, "たら": 3,
    # 肉
    "鶏肉": 3, "豚肉": 3, "牛肉": 3,
    # 豆腐等
    "豆腐": 2, "油揚げ": 1, "厚揚げ": 1,
}

# 調理法の難易度スコア
# 調理時間の最低値（分）- 少量でもこの時間はかかる
MIN_COOK_TIME = 3

# 調理法の難易度スコア
COOKING_DIFFICULTY: dict[str, int] = {
    "生": 1,
    "ゆで": 2,
    "炒め": 3,
    "焼き": 3,
    "蒸し": 4,
    "揚げ": 5,
}


def _get_prep_time(food_name: str) -> float:
    """食材名から下処理時間を取得"""
    for keyword, time in PREP_TIME_ESTIMATES.items():
        if keyword in food_name:
            return time
    return 2.0  # デフォルト2分


def _get_cooking_method_from_name(dish_name: str) -> str:
    """料理名から推定調理法を取得"""
    if not dish_name:
        return "生"
    for method in ["揚げ", "炒め", "焼き", "蒸し", "ゆで"]:
        if method in dish_name:
            return method
    # キーワードベースの推定
    if any(kw in dish_name for kw in ["フライ", "天ぷら", "から揚げ", "唐揚げ", "コロッケ"]):
        return "揚げ"
    if any(kw in dish_name for kw in ["サラダ", "和え物", "あえ物", "漬け"]):
        return "生"
    if any(kw in dish_name for kw in ["煮", "カレー", "シチュー", "スープ", "みそ汁", "味噌汁"]):
        return "ゆで"
    if any(kw in dish_name for kw in ["グリル", "ステーキ", "ハンバーグ", "ムニエル"]):
        return "焼き"
    return "炒め"  # デフォルト


def estimate_cooking_effort(menu: DailyMenuData) -> dict:
    """献立の調理工数を推定"""
    slots_detail: list[dict] = []
    total_prep = 0.0
    total_cook = 0.0
    total_difficulty_score = 0

    slot_names = {
        "staple": ("主食", menu.staple),
        "main_dish": ("主菜", menu.main_dish),
        "side_dish": ("副菜", menu.side_dish),
        "soup": ("汁物", menu.soup),
        "dessert": ("デザート", menu.dessert),
    }

    for slot_key, (slot_label, slot_item) in slot_names.items():
        if not slot_item or not slot_item.ingredients:
            continue

        method = _get_cooking_method_from_name(slot_item.name)
        cook_time_per_100g = COOKING_TIME_ESTIMATES.get(method, 5)
        difficulty = COOKING_DIFFICULTY.get(method, 3)

        slot_prep = 0.0
        slot_cook = 0.0
        total_weight = 0.0

        for ing in slot_item.ingredients:
            if not ing.food_name or ing.amount_g <= 0:
                continue
            slot_prep += _get_prep_time(ing.food_name)
            total_weight += ing.amount_g

        # 調理時間は重量に比例（最低時間は MIN_COOK_TIME）
        slot_cook = max(MIN_COOK_TIME, cook_time_per_100g * total_weight / 100)

        # 食材数で難易度補正
        ingredient_count = len([i for i in slot_item.ingredients if i.food_name])
        adjusted_difficulty = min(5, difficulty + max(0, ingredient_count - 3))

        total_prep += slot_prep
        total_cook += slot_cook
        total_difficulty_score += adjusted_difficulty

        slots_detail.append({
            "slot": slot_key,
            "slot_label": slot_label,
            "dish_name": slot_item.name,
            "method": method,
            "prep_minutes": round(slot_prep, 0),
            "cook_minutes": round(slot_cook, 0),
            "total_minutes": round(slot_prep + slot_cook, 0),
            "difficulty": adjusted_difficulty,
            "ingredient_count": ingredient_count,
        })

    # 並行調理可能性を考慮した実効時間
    # 汁物とメインは並行調理可能と仮定
    if len(slots_detail) >= 2:
        sorted_slots = sorted(slots_detail, key=lambda x: x["total_minutes"], reverse=True)
        parallel_time = sorted_slots[0]["total_minutes"]
        for s in sorted_slots[1:]:
            parallel_time += s["prep_minutes"]  # 下処理分だけ加算
    else:
        parallel_time = total_prep + total_cook

    num_slots = len(slots_detail)
    avg_difficulty = round(total_difficulty_score / num_slots, 1) if num_slots > 0 else 0

    # 難易度ラベル
    if avg_difficulty <= 2:
        difficulty_label = "簡単"
    elif avg_difficulty <= 3.5:
        difficulty_label = "普通"
    else:
        difficulty_label = "手間がかかる"

    return {
        "total_minutes": round(total_prep + total_cook, 0),
        "parallel_minutes": round(parallel_time, 0),
        "prep_minutes": round(total_prep, 0),
        "cook_minutes": round(total_cook, 0),
        "difficulty": round(avg_difficulty, 1),
        "difficulty_label": difficulty_label,
        "slots_detail": slots_detail,
    }


def suggest_time_reduction(menu: DailyMenuData) -> list[dict]:
    """時短提案"""
    suggestions: list[dict] = []
    effort = estimate_cooking_effort(menu)

    for slot in effort["slots_detail"]:
        if slot["method"] == "揚げ":
            suggestions.append({
                "slot": slot["slot"],
                "dish_name": slot["dish_name"],
                "suggestion": "揚げ物→焼き調理に変更で約5分短縮",
                "time_saved": 5,
            })
        if slot["prep_minutes"] > 10:
            suggestions.append({
                "slot": slot["slot"],
                "dish_name": slot["dish_name"],
                "suggestion": "カット野菜や冷凍食材の利用で下処理時間を短縮",
                "time_saved": round(slot["prep_minutes"] * 0.5, 0),
            })
        if slot["ingredient_count"] > 5:
            suggestions.append({
                "slot": slot["slot"],
                "dish_name": slot["dish_name"],
                "suggestion": f"食材数が多め（{slot['ingredient_count']}品）。事前仕込みを検討",
                "time_saved": 0,
            })

    return suggestions
