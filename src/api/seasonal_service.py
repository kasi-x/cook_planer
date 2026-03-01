"""季節の食べもの判定サービス"""

from src.scrapers.price_history import SEASONAL_FACTORS
from .menu_models import DailyMenuData
from .food_utils import match_food_keyword

# 食品カテゴリマッピング（merge_data.pyのカテゴリ定義を再利用）
FOOD_CATEGORY_MAP: dict[str, str] = {
    # 穀類
    "米": "穀類", "パン": "穀類", "うどん": "穀類", "そば": "穀類",
    "スパゲッティ": "穀類", "麺": "穀類", "もち": "穀類",
    # 肉類
    "牛肉": "肉類", "豚肉": "肉類", "鶏肉": "肉類",
    "ハム": "肉類", "ベーコン": "肉類", "ソーセージ": "肉類",
    # 魚介類
    "さけ": "魚介類", "さば": "魚介類", "あじ": "魚介類", "いわし": "魚介類",
    "さんま": "魚介類", "ぶり": "魚介類", "まぐろ": "魚介類", "たら": "魚介類",
    "えび": "魚介類", "あさり": "魚介類", "しじみ": "魚介類",
    "ちくわ": "魚介類", "かまぼこ": "魚介類", "ほっけ": "魚介類", "かつお": "魚介類",
    # 乳卵類
    "鶏卵": "乳卵類", "牛乳": "乳卵類", "ヨーグルト": "乳卵類",
    "チーズ": "乳卵類", "バター": "乳卵類",
    # 野菜
    "だいこん": "野菜", "かぶ": "野菜", "にんじん": "野菜", "キャベツ": "野菜",
    "レタス": "野菜", "はくさい": "野菜", "ほうれんそう": "野菜", "こまつな": "野菜",
    "ねぎ": "野菜", "たまねぎ": "野菜", "きゅうり": "野菜", "トマト": "野菜",
    "ミニトマト": "野菜", "なす": "野菜", "ピーマン": "野菜", "かぼちゃ": "野菜",
    "じゃがいも": "野菜", "えだまめ": "野菜", "いんげん": "野菜",
    "ブロッコリー": "野菜", "とうもろこし": "野菜", "そらまめ": "野菜",
    "さつまいも": "野菜", "さといも": "野菜", "ごぼう": "野菜", "れんこん": "野菜",
    "ながいも": "野菜", "アスパラガス": "野菜", "オクラ": "野菜", "もやし": "野菜",
    "ズッキーニ": "野菜", "セロリ": "野菜", "しょうが": "野菜", "にんにく": "野菜",
    "赤ピーマン": "野菜", "黄ピーマン": "野菜", "チンゲンサイ": "野菜",
    "スナップ実えんどう": "野菜",
    # きのこ（野菜カテゴリに含める）
    "しいたけ": "野菜", "えのきたけ": "野菜", "しめじ": "野菜",
    "まいたけ": "野菜", "エリンギ": "野菜",
    # 果物
    "バナナ": "果物", "りんご": "果物", "みかん": "果物",
    "オレンジ": "果物", "キウイ": "果物", "うめ": "果物",
    # 大豆製品（調味料カテゴリ）
    "豆腐": "調味料", "納豆": "調味料", "油揚げ": "調味料",
    "厚揚げ": "調味料", "豆乳": "調味料",
    # 調味料
    "味噌": "調味料", "醤油": "調味料", "砂糖": "調味料", "塩": "調味料",
    "サラダ油": "調味料", "オリーブオイル": "調味料", "ごま油": "調味料",
    # 海藻（野菜カテゴリ）
    "わかめ": "野菜", "のり": "野菜", "ひじき": "野菜",
    # その他
    "こんにゃく": "野菜", "しらたき": "野菜",
}

# 月→四半期マッピング
MONTH_TO_QUARTER = {
    4: "Q1_Apr", 5: "Q1_Apr", 6: "Q1_Apr",
    7: "Q2_Jul", 8: "Q2_Jul", 9: "Q2_Jul",
    10: "Q3_Oct", 11: "Q3_Oct", 12: "Q3_Oct",
    1: "Q4_Jan", 2: "Q4_Jan", 3: "Q4_Jan",
}

QUARTER_LABELS = {
    "Q1_Apr": "春（4-6月）",
    "Q2_Jul": "夏（7-9月）",
    "Q3_Oct": "秋（10-12月）",
    "Q4_Jan": "冬（1-3月）",
}


def categorize_food(food_name: str) -> str | None:
    """食品名からカテゴリを判定"""
    for keyword, category in FOOD_CATEGORY_MAP.items():
        if match_food_keyword(food_name, keyword):
            return category
    return None


def get_seasonal_foods(month: int) -> list[dict]:
    """指定月の旬食材一覧を返す。seasonal_factor > 1.0 なら旬とは逆（高い）、< 1.0 なら旬（安い）"""
    quarter = MONTH_TO_QUARTER.get(month, "Q1_Apr")
    results = []

    for food_name, category in FOOD_CATEGORY_MAP.items():
        if category not in SEASONAL_FACTORS:
            continue
        factor = SEASONAL_FACTORS[category].get(quarter, 1.0)
        # 季節係数 < 1.0 = 旬（安くて豊富）
        is_in_season = factor < 1.0
        results.append({
            "name": food_name,
            "category": category,
            "seasonal_factor": factor,
            "quarter": quarter,
            "quarter_label": QUARTER_LABELS[quarter],
            "in_season": is_in_season,
        })

    # 旬の食材を先に、factor昇順で並べる
    results.sort(key=lambda x: (not x["in_season"], x["seasonal_factor"]))
    return results


def get_seasonal_recommendation(menu: DailyMenuData, month: int) -> dict:
    """献立内の旬食材使用率を計算"""
    quarter = MONTH_TO_QUARTER.get(month, "Q1_Apr")

    all_ingredients: list[str] = []
    for slot in [menu.staple, menu.main_dish, menu.side_dish, menu.soup, menu.dessert]:
        if slot:
            for ing in slot.ingredients:
                if ing.food_name:
                    all_ingredients.append(ing.food_name)

    if not all_ingredients:
        return {
            "seasonal_ratio": 0.0,
            "seasonal_items": [],
            "non_seasonal_items": [],
            "suggestions": ["食材を追加してください"],
        }

    seasonal_items = []
    non_seasonal_items = []

    for food_name in all_ingredients:
        category = categorize_food(food_name)
        if not category or category not in SEASONAL_FACTORS:
            continue
        factor = SEASONAL_FACTORS[category].get(quarter, 1.0)
        if factor < 1.0:
            seasonal_items.append({
                "name": food_name,
                "category": category,
                "seasonal_factor": factor,
            })
        elif factor > 1.0:
            non_seasonal_items.append({
                "name": food_name,
                "category": category,
                "seasonal_factor": factor,
            })

    total = len(seasonal_items) + len(non_seasonal_items)
    ratio = (len(seasonal_items) / total * 100) if total > 0 else 0

    suggestions = []
    if ratio < 50:
        # 旬の食材カテゴリを提案
        in_season_categories = set()
        for cat, factors in SEASONAL_FACTORS.items():
            if factors.get(quarter, 1.0) < 1.0:
                in_season_categories.add(cat)
        if in_season_categories:
            suggestions.append(
                f"旬のカテゴリ（{', '.join(in_season_categories)}）の食材を増やすとコスト削減できます"
            )

    return {
        "seasonal_ratio": round(ratio, 1),
        "seasonal_items": seasonal_items,
        "non_seasonal_items": non_seasonal_items,
        "suggestions": suggestions,
    }
