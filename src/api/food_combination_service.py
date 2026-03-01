"""食べ合わせチェックサービス

栄養吸収の相乗効果・阻害効果をチェックする。
"""

from .menu_models import DailyMenuData
from .seasonal_service import categorize_food
from .food_utils import match_food_keyword

# 相乗効果リスト
GOOD_COMBINATIONS: list[dict] = [
    {
        "nutrients": ["iron_mg", "vitamin_c_mg"],
        "description": "鉄分 + ビタミンC → 鉄の吸収を促進",
        "food_examples": {
            "iron_mg": ["ほうれんそう", "こまつな", "ひじき", "あさり", "しじみ", "レバー"],
            "vitamin_c_mg": ["ピーマン", "ブロッコリー", "キウイ", "トマト", "キャベツ", "レモン"],
        },
    },
    {
        "nutrients": ["calcium_mg", "vitamin_d_ug"],
        "description": "カルシウム + ビタミンD → カルシウムの吸収を促進",
        "food_examples": {
            "calcium_mg": ["牛乳", "チーズ", "こまつな", "豆腐", "ヨーグルト", "しらす"],
            "vitamin_d_ug": ["さけ", "さば", "いわし", "しいたけ", "まいたけ", "鶏卵"],
        },
    },
    {
        "nutrients": ["vitamin_a_ug", "fat_g"],
        "description": "β-カロテン(ビタミンA) + 脂質 → 吸収を促進",
        "food_examples": {
            "vitamin_a_ug": ["にんじん", "かぼちゃ", "ほうれんそう", "こまつな", "トマト"],
            "fat_g": ["サラダ油", "オリーブオイル", "ごま油", "バター"],
        },
    },
    {
        "nutrients": ["protein_g", "vitamin_b6_mg"],
        "description": "たんぱく質 + ビタミンB6 → たんぱく質の代謝を促進",
        "food_examples": {
            "protein_g": ["鶏肉", "豚肉", "さけ", "まぐろ", "豆腐"],
            "vitamin_b6_mg": ["バナナ", "にんにく", "さば", "さけ"],
        },
    },
]

# 阻害効果リスト
BAD_COMBINATIONS: list[dict] = [
    {
        "nutrients": ["calcium_mg"],
        "inhibitor": "シュウ酸",
        "description": "カルシウム + シュウ酸（ほうれんそう生）→ カルシウムの吸収を阻害",
        "food_keywords": {
            "nutrient_source": ["牛乳", "チーズ", "豆腐", "こまつな"],
            "inhibitor_source": ["ほうれんそう"],
        },
        "note": "ほうれんそうをゆでるとシュウ酸が減少します",
    },
    {
        "nutrients": ["iron_mg"],
        "inhibitor": "タンニン",
        "description": "鉄分 + タンニン（お茶）→ 鉄の吸収を阻害",
        "food_keywords": {
            "nutrient_source": ["ほうれんそう", "こまつな", "ひじき", "あさり"],
            "inhibitor_source": ["紅茶", "緑茶", "コーヒー"],
        },
        "note": "食事中のお茶は控えめにしましょう",
    },
    {
        "nutrients": ["calcium_mg"],
        "inhibitor": "リン酸",
        "description": "カルシウム + リン酸（加工食品）→ カルシウムの吸収を阻害",
        "food_keywords": {
            "nutrient_source": ["牛乳", "チーズ", "豆腐"],
            "inhibitor_source": ["ソーセージ", "ハム", "ベーコン", "即席めん", "かまぼこ"],
        },
        "note": "加工食品の摂りすぎに注意しましょう",
    },
]


def _collect_ingredients(menu: DailyMenuData) -> list[str]:
    """献立から全食材名を収集"""
    ingredients: list[str] = []
    for slot in [menu.staple, menu.main_dish, menu.side_dish, menu.soup, menu.dessert]:
        if slot:
            for ing in slot.ingredients:
                if ing.food_name:
                    ingredients.append(ing.food_name)
    if menu.milk:
        ingredients.append("牛乳")
    return ingredients


def _food_matches_keyword(food_name: str, keyword: str) -> bool:
    """食品名がキーワードにマッチするか"""
    return match_food_keyword(food_name, keyword)


def check_combinations(menu: DailyMenuData) -> dict:
    """献立内の食べ合わせを分析"""
    ingredients = _collect_ingredients(menu)

    if not ingredients:
        return {
            "good_effects": [],
            "bad_effects": [],
            "suggestions": [],
        }

    good_effects: list[dict] = []
    bad_effects: list[dict] = []
    suggestions: list[str] = []

    # 相乗効果チェック
    for combo in GOOD_COMBINATIONS:
        nutrient_keys = combo["nutrients"]
        found_foods: dict[str, list[str]] = {k: [] for k in nutrient_keys}

        for food in ingredients:
            for nutrient_key, examples in combo["food_examples"].items():
                if any(_food_matches_keyword(food, ex) for ex in examples):
                    found_foods[nutrient_key].append(food)

        # 両方の栄養素に該当する食材がある場合
        if all(len(foods) > 0 for foods in found_foods.values()):
            good_effects.append({
                "type": "good",
                "nutrients": nutrient_keys,
                "foods": {k: v for k, v in found_foods.items()},
                "description": combo["description"],
            })

    # 阻害効果チェック
    for combo in BAD_COMBINATIONS:
        nutrient_sources = []
        inhibitor_sources = []

        for food in ingredients:
            for kw in combo["food_keywords"]["nutrient_source"]:
                if _food_matches_keyword(food, kw):
                    nutrient_sources.append(food)
                    break

            for kw in combo["food_keywords"]["inhibitor_source"]:
                if _food_matches_keyword(food, kw):
                    inhibitor_sources.append(food)
                    break

        if nutrient_sources and inhibitor_sources:
            bad_effects.append({
                "type": "bad",
                "nutrients": combo["nutrients"],
                "foods": {
                    "source": nutrient_sources,
                    "inhibitor": inhibitor_sources,
                },
                "description": combo["description"],
                "note": combo.get("note", ""),
            })

    # 提案
    if not good_effects:
        suggestions.append("ビタミンCを含む食材（ピーマン、ブロッコリー等）を加えると鉄分の吸収が促進されます")

    for bad in bad_effects:
        if bad.get("note"):
            suggestions.append(bad["note"])

    return {
        "good_effects": good_effects,
        "bad_effects": bad_effects,
        "suggestions": suggestions,
    }
