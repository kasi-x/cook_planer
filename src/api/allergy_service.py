"""アレルギー管理サービス

特定原材料8品目 + 推奨表示20品目をマスタデータとして管理。
"""

from .menu_models import DailyMenuData
from .food_utils import match_food_keyword

# 特定原材料等28品目
# category: "mandatory" = 表示義務8品目, "recommended" = 推奨表示20品目
ALLERGEN_MASTER: dict[str, dict] = {
    # === 特定原材料（表示義務）8品目 ===
    "えび": {
        "category": "mandatory",
        "related_foods": ["えび", "くるまえび", "ブラックタイガー", "甘えび", "桜えび"],
    },
    "かに": {
        "category": "mandatory",
        "related_foods": ["かに", "ずわいがに", "たらばがに", "カニかま"],
    },
    "くるみ": {
        "category": "mandatory",
        "related_foods": ["くるみ"],
    },
    "小麦": {
        "category": "mandatory",
        "related_foods": [
            "パン", "うどん", "そうめん", "スパゲッティ", "中華麺", "即席めん",
            "小麦粉", "薄力粉", "強力粉", "ちくわ", "かまぼこ",
            "ソーセージ", "ハム", "餃子", "天ぷら",
        ],
    },
    "そば": {
        "category": "mandatory",
        "related_foods": ["そば"],
    },
    "卵": {
        "category": "mandatory",
        "related_foods": ["鶏卵", "卵", "マヨネーズ", "卵焼き", "オムレツ", "プリン"],
    },
    "乳": {
        "category": "mandatory",
        "related_foods": [
            "牛乳", "チーズ", "バター", "ヨーグルト", "生クリーム",
            "アイスクリーム", "練乳", "脱脂粉乳",
        ],
    },
    "落花生": {
        "category": "mandatory",
        "related_foods": ["落花生", "ピーナッツ", "ピーナツ"],
    },
    # === 推奨表示 20品目 ===
    "アーモンド": {
        "category": "recommended",
        "related_foods": ["アーモンド"],
    },
    "あわび": {
        "category": "recommended",
        "related_foods": ["あわび"],
    },
    "いか": {
        "category": "recommended",
        "related_foods": ["いか", "するめ"],
    },
    "いくら": {
        "category": "recommended",
        "related_foods": ["いくら", "すじこ"],
    },
    "オレンジ": {
        "category": "recommended",
        "related_foods": ["オレンジ"],
    },
    "カシューナッツ": {
        "category": "recommended",
        "related_foods": ["カシューナッツ"],
    },
    "キウイフルーツ": {
        "category": "recommended",
        "related_foods": ["キウイ"],
    },
    "牛肉": {
        "category": "recommended",
        "related_foods": ["牛肉"],
    },
    "ごま": {
        "category": "recommended",
        "related_foods": ["ごま", "ごま油"],
    },
    "さけ": {
        "category": "recommended",
        "related_foods": ["さけ", "サーモン", "鮭"],
    },
    "さば": {
        "category": "recommended",
        "related_foods": ["さば"],
    },
    "大豆": {
        "category": "recommended",
        "related_foods": [
            "豆腐", "納豆", "油揚げ", "厚揚げ", "豆乳",
            "味噌", "醤油", "大豆", "きな粉",
        ],
    },
    "鶏肉": {
        "category": "recommended",
        "related_foods": ["鶏肉"],
    },
    "バナナ": {
        "category": "recommended",
        "related_foods": ["バナナ"],
    },
    "豚肉": {
        "category": "recommended",
        "related_foods": ["豚肉", "ハム", "ベーコン", "ソーセージ"],
    },
    "マカダミアナッツ": {
        "category": "recommended",
        "related_foods": ["マカダミアナッツ"],
    },
    "もも": {
        "category": "recommended",
        "related_foods": ["もも", "桃"],
    },
    "やまいも": {
        "category": "recommended",
        "related_foods": ["ながいも", "やまいも", "とろろ"],
    },
    "りんご": {
        "category": "recommended",
        "related_foods": ["りんご"],
    },
    "ゼラチン": {
        "category": "recommended",
        "related_foods": ["ゼラチン"],
    },
}


def get_allergen_list() -> list[dict]:
    """全アレルゲン一覧を返す"""
    return [
        {
            "id": name,
            "name": name,
            "category": info["category"],
            "category_label": "特定原材料" if info["category"] == "mandatory" else "推奨表示",
        }
        for name, info in ALLERGEN_MASTER.items()
    ]


def check_allergens(menu: DailyMenuData, excluded_allergens: list[str] | None = None) -> list[dict]:
    """献立内のアレルゲンを検出"""
    warnings: list[dict] = []

    slots = {
        "staple": menu.staple,
        "main_dish": menu.main_dish,
        "side_dish": menu.side_dish,
        "soup": menu.soup,
        "dessert": menu.dessert,
    }

    # 牛乳チェック
    if menu.milk:
        if excluded_allergens is None or "乳" in excluded_allergens:
            warnings.append({
                "allergen": "乳",
                "severity": "mandatory",
                "source_food": "牛乳",
                "slot": "milk",
            })

    for slot_name, slot_item in slots.items():
        if not slot_item:
            continue
        for ing in slot_item.ingredients:
            if not ing.food_name:
                continue
            for allergen_name, allergen_info in ALLERGEN_MASTER.items():
                for related in allergen_info["related_foods"]:
                    if match_food_keyword(ing.food_name, related):
                        severity = allergen_info["category"]
                        # excluded_allergensが指定されている場合、該当アレルゲンのみ警告
                        if excluded_allergens is None or allergen_name in excluded_allergens:
                            warnings.append({
                                "allergen": allergen_name,
                                "severity": severity,
                                "source_food": ing.food_name,
                                "slot": slot_name,
                            })
                        break  # 同一食材で同じアレルゲン重複回避

    # 重複排除（同じアレルゲン+同じスロット+同じ食材）
    seen = set()
    unique_warnings = []
    for w in warnings:
        key = (w["allergen"], w["slot"], w["source_food"])
        if key not in seen:
            seen.add(key)
            unique_warnings.append(w)

    return unique_warnings


def filter_foods_by_allergens(food_names: list[str], excluded_allergens: list[str]) -> list[str]:
    """アレルゲンを含む食材を除外"""
    filtered = []
    for food_name in food_names:
        has_allergen = False
        for allergen_name in excluded_allergens:
            if allergen_name not in ALLERGEN_MASTER:
                continue
            for related in ALLERGEN_MASTER[allergen_name]["related_foods"]:
                if match_food_keyword(food_name, related):
                    has_allergen = True
                    break
            if has_allergen:
                break
        if not has_allergen:
            filtered.append(food_name)
    return filtered
