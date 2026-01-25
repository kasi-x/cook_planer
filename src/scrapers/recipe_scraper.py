"""レシピからの食材・分量取得

楽天レシピAPIを使用してレシピ情報を取得し、
食材を既存の栄養データベースとマッチングする
"""

import re
import json
from pathlib import Path
from difflib import SequenceMatcher

import requests
import pandas as pd

DATA_DIR = Path(__file__).parent.parent.parent / "data"
MERGED_DIR = DATA_DIR / "merged"
RECIPE_DATA_DIR = DATA_DIR / "processed" / "recipes"


def load_food_names() -> list[str]:
    """食品名リストを読み込み"""
    csv_path = MERGED_DIR / "food_price_nutrition.csv"
    if not csv_path.exists():
        return []
    df = pd.read_csv(csv_path)
    return df["food_name"].tolist()


# 食材名の正規化マッピング（レシピ表記 → データベース表記）
INGREDIENT_MAPPING = {
    # 肉類
    "鶏むね肉": "鶏肉（むね）",
    "鶏胸肉": "鶏肉（むね）",
    "とりむね肉": "鶏肉（むね）",
    "鶏もも肉": "鶏肉（もも）",
    "とりもも肉": "鶏肉（もも）",
    "鶏ひき肉": "鶏肉（ひき肉）",
    "鶏挽き肉": "鶏肉（ひき肉）",
    "ささみ": "鶏肉（ささみ）",
    "鶏ささみ": "鶏肉（ささみ）",
    "豚ひき肉": "豚肉（ひき肉）",
    "豚挽き肉": "豚肉（ひき肉）",
    "豚もも肉": "豚肉（もも）",
    "豚バラ肉": "豚肉（ばら）",
    "豚バラ": "豚肉（ばら）",
    "牛ひき肉": "牛肉（ひき肉）",
    "牛挽き肉": "牛肉（ひき肉）",
    "牛もも肉": "牛肉（もも）",
    "合いびき肉": "豚肉（ひき肉）",  # 近似
    "合挽き肉": "豚肉（ひき肉）",  # 近似
    # 魚介類
    "鮭": "さけ",
    "サーモン": "さけ",
    "塩鮭": "さけ",
    "塩サケ": "さけ",
    "鯖": "さば",
    "サバ": "さば",
    "塩鯖": "さば",
    "鯵": "あじ",
    "アジ": "あじ",
    "鰯": "いわし",
    "イワシ": "いわし",
    "鮪": "まぐろ（赤身）",
    "マグロ": "まぐろ（赤身）",
    "鱈": "たら",
    "タラ": "たら",
    "海老": "えび",
    "エビ": "えび",
    "むきえび": "えび",
    "いか": "いか",
    "イカ": "いか",
    # 卵・乳製品
    "卵": "鶏卵（Ｌ）",
    "たまご": "鶏卵（Ｌ）",
    "玉子": "鶏卵（Ｌ）",
    "鶏卵": "鶏卵（Ｌ）",
    "牛乳": "牛乳",
    "ミルク": "牛乳",
    "プレーンヨーグルト": "ヨーグルト（プレーン）",
    "ヨーグルト": "ヨーグルト（プレーン）",
    "プロセスチーズ": "チーズ（プロセス）",
    "チーズ": "チーズ（プロセス）",
    "バター": "バター",
    "マーガリン": "バター",  # 近似
    # 豆類
    "木綿豆腐": "豆腐（木綿）",
    "もめん豆腐": "豆腐（木綿）",
    "豆腐": "豆腐（木綿）",
    "絹ごし豆腐": "豆腐（絹ごし）",
    "きぬ豆腐": "豆腐（絹ごし）",
    "納豆": "納豆",
    "油揚げ": "油揚げ",
    "あげ": "油揚げ",
    "厚揚げ": "厚揚げ",
    "豆乳": "豆乳",
    # 野菜類
    "キャベツ": "キャベツ",
    "きゃべつ": "キャベツ",
    "人参": "にんじん",
    "にんじん": "にんじん",
    "ニンジン": "にんじん",
    "玉ねぎ": "たまねぎ",
    "たまねぎ": "たまねぎ",
    "玉葱": "たまねぎ",
    "タマネギ": "たまねぎ",
    "ほうれん草": "ほうれんそう",
    "ほうれんそう": "ほうれんそう",
    "ホウレンソウ": "ほうれんそう",
    "ブロッコリー": "ブロッコリー",
    "大根": "だいこん",
    "だいこん": "だいこん",
    "ダイコン": "だいこん",
    "じゃがいも": "じゃがいも",
    "ジャガイモ": "じゃがいも",
    "馬鈴薯": "じゃがいも",
    "もやし": "もやし",
    "モヤシ": "もやし",
    "トマト": "トマト",
    "とまと": "トマト",
    "レタス": "レタス",
    "きゅうり": "きゅうり",
    "キュウリ": "きゅうり",
    "胡瓜": "きゅうり",
    "ねぎ": "ねぎ",
    "ネギ": "ねぎ",
    "長ねぎ": "ねぎ",
    "白ねぎ": "ねぎ",
    "青ねぎ": "ねぎ",
    "ごぼう": "ごぼう",
    "ゴボウ": "ごぼう",
    "牛蒡": "ごぼう",
    "れんこん": "れんこん",
    "レンコン": "れんこん",
    "蓮根": "れんこん",
    "なす": "なす",
    "ナス": "なす",
    "茄子": "なす",
    "ピーマン": "ピーマン",
    "白菜": "はくさい",
    "はくさい": "はくさい",
    "ハクサイ": "はくさい",
    "かぼちゃ": "かぼちゃ",
    "カボチャ": "かぼちゃ",
    "南瓜": "かぼちゃ",
    "小松菜": "こまつな",
    "こまつな": "こまつな",
    "水菜": "みずな",
    "みずな": "みずな",
    # きのこ類
    "しいたけ": "しいたけ（生）",
    "椎茸": "しいたけ（生）",
    "シイタケ": "しいたけ（生）",
    "えのき": "えのきたけ",
    "エノキ": "えのきたけ",
    "えのきだけ": "えのきたけ",
    "しめじ": "しめじ",
    "シメジ": "しめじ",
    "まいたけ": "まいたけ",
    "舞茸": "まいたけ",
    "マイタケ": "まいたけ",
    "エリンギ": "エリンギ",
    # 穀類
    "米": "米（精白米）",
    "ご飯": "米（精白米）",
    "ごはん": "米（精白米）",
    "白米": "米（精白米）",
    "食パン": "食パン",
    "パン": "食パン",
    # 調味料
    "味噌": "味噌",
    "みそ": "味噌",
    "醤油": "醤油",
    "しょうゆ": "醤油",
    "しょう油": "醤油",
    # 果物
    "バナナ": "バナナ",
    "りんご": "りんご",
    "リンゴ": "りんご",
    "林檎": "りんご",
    "みかん": "みかん",
    "ミカン": "みかん",
    "キウイ": "キウイ",
    "キウイフルーツ": "キウイ",
    # 海藻
    "わかめ": "わかめ（乾燥）",
    "ワカメ": "わかめ（乾燥）",
    "乾燥わかめ": "わかめ（乾燥）",
    "ひじき": "ひじき（乾燥）",
    "乾燥ひじき": "ひじき（乾燥）",
    "焼きのり": "のり（焼き）",
    "海苔": "のり（焼き）",
    # 加工品
    "ハム": "ハム（ロース）",
    "ロースハム": "ハム（ロース）",
    "ベーコン": "ベーコン",
    "ソーセージ": "ソーセージ",
    "ウインナー": "ソーセージ",
}


# 単位の正規化（全てグラムに変換）
UNIT_CONVERSION = {
    "g": 1.0,
    "グラム": 1.0,
    "kg": 1000.0,
    "キログラム": 1000.0,
    "ml": 1.0,  # 液体は近似的に1ml=1g
    "ミリリットル": 1.0,
    "cc": 1.0,
    "l": 1000.0,
    "リットル": 1000.0,
    "個": 60.0,  # 卵基準
    "本": 100.0,  # バナナ等
    "枚": 30.0,  # パン1枚等
    "丁": 300.0,  # 豆腐1丁
    "玉": 200.0,  # 玉ねぎ1玉
    "把": 200.0,  # ほうれん草1把
    "束": 200.0,
    "株": 200.0,
    "房": 150.0,  # ブロッコリー等
    "切れ": 80.0,  # 鮭の切り身等
    "パック": 45.0,  # 納豆1パック
    "袋": 200.0,  # もやし1袋
    "カップ": 200.0,
    "大さじ": 15.0,
    "小さじ": 5.0,
    "少々": 1.0,
    "適量": 5.0,
}


def parse_amount(amount_text: str) -> float | None:
    """分量テキストからグラム数を抽出

    Examples:
        "200g" -> 200.0
        "2個" -> 120.0
        "1/2本" -> 50.0
        "大さじ2" -> 30.0
    """
    if not amount_text:
        return None

    amount_text = amount_text.strip()

    # 数字と単位を分離
    # パターン: 数字（分数含む）+ 単位
    pattern = r'([\d./]+)\s*(.+)?'
    match = re.match(pattern, amount_text)

    if not match:
        # "適量" など単位のみの場合
        for unit, grams in UNIT_CONVERSION.items():
            if unit in amount_text:
                return grams
        return None

    num_str = match.group(1)
    unit_str = match.group(2) or "g"
    unit_str = unit_str.strip()

    # 数値を解析（分数対応）
    try:
        if "/" in num_str:
            parts = num_str.split("/")
            if len(parts) == 2:
                num = float(parts[0]) / float(parts[1])
            else:
                num = float(parts[0])
        else:
            num = float(num_str)
    except ValueError:
        return None

    # 単位を変換
    for unit, multiplier in UNIT_CONVERSION.items():
        if unit in unit_str:
            return num * multiplier

    # 単位が見つからない場合はグラムとして扱う
    return num


def match_ingredient(ingredient_name: str, food_names: list[str]) -> str | None:
    """食材名をデータベースの食品名にマッチング

    1. 完全一致
    2. マッピングテーブル
    3. 部分一致
    4. あいまい検索
    """
    ingredient_name = ingredient_name.strip()

    # 完全一致
    if ingredient_name in food_names:
        return ingredient_name

    # マッピングテーブル
    if ingredient_name in INGREDIENT_MAPPING:
        mapped = INGREDIENT_MAPPING[ingredient_name]
        if mapped in food_names:
            return mapped

    # 部分一致（食材名がデータベース名に含まれる）
    for food_name in food_names:
        if ingredient_name in food_name:
            return food_name

    # あいまい検索（類似度スコア）
    best_match = None
    best_score = 0.5  # 最低閾値

    for food_name in food_names:
        # 簡略化した名前で比較
        simplified_ingredient = re.sub(r'[（）\(\)・、]', '', ingredient_name)
        simplified_food = re.sub(r'[（）\(\)・、]', '', food_name)

        score = SequenceMatcher(None, simplified_ingredient, simplified_food).ratio()
        if score > best_score:
            best_score = score
            best_match = food_name

    return best_match


def parse_recipe_ingredients(
    recipe_text: str,
    food_names: list[str] = None
) -> list[dict]:
    """レシピテキストから食材と分量を抽出

    Args:
        recipe_text: 食材リストのテキスト（1行1食材）
        food_names: マッチング用の食品名リスト

    Returns:
        [{"ingredient": "鶏むね肉", "amount_text": "200g",
          "amount_g": 200, "matched_food": "鶏肉（むね）"}, ...]
    """
    if food_names is None:
        food_names = load_food_names()

    results = []
    lines = recipe_text.strip().split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 「食材名 分量」または「食材名: 分量」形式を解析
        # パターン例: "鶏むね肉 200g", "玉ねぎ: 1/2個", "塩・こしょう 少々"
        patterns = [
            r'^(.+?)[:\s]+(.+)$',  # コロンまたはスペース区切り
            r'^(.+)$',  # 分量なし
        ]

        ingredient = None
        amount_text = None

        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                if len(match.groups()) >= 2:
                    ingredient = match.group(1).strip()
                    amount_text = match.group(2).strip()
                else:
                    ingredient = match.group(1).strip()
                break

        if not ingredient:
            continue

        # 分量を解析
        amount_g = parse_amount(amount_text) if amount_text else None

        # データベースの食品名にマッチング
        matched_food = match_ingredient(ingredient, food_names)

        results.append({
            "ingredient": ingredient,
            "amount_text": amount_text or "",
            "amount_g": amount_g,
            "matched_food": matched_food,
        })

    return results


class RakutenRecipeClient:
    """楽天レシピAPI クライアント"""

    BASE_URL = "https://app.rakuten.co.jp/services/api"

    def __init__(self, app_id: str | None = None):
        """
        Args:
            app_id: 楽天API アプリケーションID
                    環境変数 RAKUTEN_APP_ID からも取得可能
        """
        import os
        self.app_id = app_id or os.environ.get("RAKUTEN_APP_ID")

    def get_categories(self) -> list[dict]:
        """カテゴリ一覧を取得"""
        if not self.app_id:
            return []

        url = f"{self.BASE_URL}/Recipe/CategoryList/20170426"
        params = {"applicationId": self.app_id}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("result", {}).get("large", [])
        except Exception:
            return []

    def get_ranking(self, category_id: str) -> list[dict]:
        """カテゴリ別ランキングを取得"""
        if not self.app_id:
            return []

        url = f"{self.BASE_URL}/Recipe/CategoryRanking/20170426"
        params = {
            "applicationId": self.app_id,
            "categoryId": category_id,
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("result", [])
        except Exception:
            return []


def load_sample_recipes() -> list[dict]:
    """サンプルレシピデータを読み込み"""
    json_path = RECIPE_DATA_DIR / "sample_recipes.json"
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_sample_recipes(recipes: list[dict]) -> None:
    """サンプルレシピデータを保存"""
    RECIPE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    json_path = RECIPE_DATA_DIR / "sample_recipes.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)


# 手動で作成したサンプルレシピ（APIなしでも使用可能）
SAMPLE_RECIPES = [
    {
        "id": "1",
        "name": "親子丼",
        "servings": 2,
        "ingredients": [
            {"name": "鶏もも肉", "amount": "200g"},
            {"name": "玉ねぎ", "amount": "1/2個"},
            {"name": "卵", "amount": "3個"},
            {"name": "ご飯", "amount": "400g"},
            {"name": "醤油", "amount": "大さじ2"},
        ],
    },
    {
        "id": "2",
        "name": "豚の生姜焼き",
        "servings": 2,
        "ingredients": [
            {"name": "豚もも肉", "amount": "300g"},
            {"name": "玉ねぎ", "amount": "1/2個"},
            {"name": "キャベツ", "amount": "100g"},
            {"name": "醤油", "amount": "大さじ2"},
        ],
    },
    {
        "id": "3",
        "name": "鮭のムニエル",
        "servings": 2,
        "ingredients": [
            {"name": "鮭", "amount": "2切れ"},
            {"name": "バター", "amount": "20g"},
            {"name": "レタス", "amount": "50g"},
            {"name": "トマト", "amount": "1個"},
        ],
    },
    {
        "id": "4",
        "name": "肉じゃが",
        "servings": 4,
        "ingredients": [
            {"name": "豚バラ肉", "amount": "200g"},
            {"name": "じゃがいも", "amount": "4個"},
            {"name": "玉ねぎ", "amount": "1個"},
            {"name": "人参", "amount": "1本"},
            {"name": "醤油", "amount": "大さじ3"},
        ],
    },
    {
        "id": "5",
        "name": "麻婆豆腐",
        "servings": 2,
        "ingredients": [
            {"name": "豆腐", "amount": "1丁"},
            {"name": "豚ひき肉", "amount": "150g"},
            {"name": "ねぎ", "amount": "1/2本"},
            {"name": "味噌", "amount": "大さじ1"},
        ],
    },
    {
        "id": "6",
        "name": "鶏の唐揚げ",
        "servings": 2,
        "ingredients": [
            {"name": "鶏もも肉", "amount": "300g"},
            {"name": "醤油", "amount": "大さじ2"},
            {"name": "キャベツ", "amount": "100g"},
        ],
    },
    {
        "id": "7",
        "name": "味噌汁",
        "servings": 4,
        "ingredients": [
            {"name": "豆腐", "amount": "1/2丁"},
            {"name": "わかめ", "amount": "5g"},
            {"name": "ねぎ", "amount": "1/4本"},
            {"name": "味噌", "amount": "大さじ3"},
        ],
    },
    {
        "id": "8",
        "name": "サバの味噌煮",
        "servings": 2,
        "ingredients": [
            {"name": "サバ", "amount": "2切れ"},
            {"name": "味噌", "amount": "大さじ2"},
        ],
    },
    {
        "id": "9",
        "name": "野菜炒め",
        "servings": 2,
        "ingredients": [
            {"name": "豚バラ肉", "amount": "150g"},
            {"name": "キャベツ", "amount": "200g"},
            {"name": "もやし", "amount": "1袋"},
            {"name": "人参", "amount": "1/2本"},
            {"name": "ピーマン", "amount": "2個"},
        ],
    },
    {
        "id": "10",
        "name": "オムライス",
        "servings": 2,
        "ingredients": [
            {"name": "ご飯", "amount": "400g"},
            {"name": "卵", "amount": "4個"},
            {"name": "鶏むね肉", "amount": "100g"},
            {"name": "玉ねぎ", "amount": "1/2個"},
            {"name": "バター", "amount": "20g"},
        ],
    },
    {
        "id": "11",
        "name": "ほうれん草のおひたし",
        "servings": 2,
        "ingredients": [
            {"name": "ほうれん草", "amount": "1把"},
            {"name": "醤油", "amount": "大さじ1"},
        ],
    },
    {
        "id": "12",
        "name": "納豆ご飯",
        "servings": 1,
        "ingredients": [
            {"name": "ご飯", "amount": "200g"},
            {"name": "納豆", "amount": "1パック"},
            {"name": "卵", "amount": "1個"},
            {"name": "ねぎ", "amount": "少々"},
        ],
    },
    {
        "id": "13",
        "name": "きのこソテー",
        "servings": 2,
        "ingredients": [
            {"name": "しめじ", "amount": "1パック"},
            {"name": "えのき", "amount": "1袋"},
            {"name": "まいたけ", "amount": "1パック"},
            {"name": "バター", "amount": "15g"},
        ],
    },
    {
        "id": "14",
        "name": "冷やっこ",
        "servings": 2,
        "ingredients": [
            {"name": "絹ごし豆腐", "amount": "1丁"},
            {"name": "ねぎ", "amount": "少々"},
            {"name": "醤油", "amount": "大さじ1"},
        ],
    },
    {
        "id": "15",
        "name": "バナナヨーグルト",
        "servings": 1,
        "ingredients": [
            {"name": "バナナ", "amount": "1本"},
            {"name": "ヨーグルト", "amount": "100g"},
        ],
    },
    {
        "id": "16",
        "name": "鶏むね肉のソテー",
        "servings": 2,
        "ingredients": [
            {"name": "鶏むね肉", "amount": "300g"},
            {"name": "ブロッコリー", "amount": "100g"},
            {"name": "バター", "amount": "15g"},
        ],
    },
    {
        "id": "17",
        "name": "豚汁",
        "servings": 4,
        "ingredients": [
            {"name": "豚バラ肉", "amount": "150g"},
            {"name": "大根", "amount": "100g"},
            {"name": "人参", "amount": "50g"},
            {"name": "豆腐", "amount": "1/2丁"},
            {"name": "ねぎ", "amount": "1/2本"},
            {"name": "味噌", "amount": "大さじ4"},
        ],
    },
    {
        "id": "18",
        "name": "卵かけご飯",
        "servings": 1,
        "ingredients": [
            {"name": "ご飯", "amount": "200g"},
            {"name": "卵", "amount": "1個"},
            {"name": "醤油", "amount": "小さじ1"},
        ],
    },
    {
        "id": "19",
        "name": "焼き魚定食",
        "servings": 1,
        "ingredients": [
            {"name": "サバ", "amount": "1切れ"},
            {"name": "ご飯", "amount": "200g"},
            {"name": "味噌", "amount": "大さじ1"},
            {"name": "豆腐", "amount": "1/4丁"},
        ],
    },
    {
        "id": "20",
        "name": "チキンサラダ",
        "servings": 2,
        "ingredients": [
            {"name": "鶏ささみ", "amount": "150g"},
            {"name": "レタス", "amount": "100g"},
            {"name": "トマト", "amount": "1個"},
            {"name": "きゅうり", "amount": "1本"},
        ],
    },
    {
        "id": "21",
        "name": "牛丼",
        "servings": 2,
        "ingredients": [
            {"name": "牛もも肉", "amount": "200g"},
            {"name": "玉ねぎ", "amount": "1個"},
            {"name": "ご飯", "amount": "400g"},
            {"name": "醤油", "amount": "大さじ3"},
        ],
    },
    {
        "id": "22",
        "name": "豆腐ステーキ",
        "servings": 2,
        "ingredients": [
            {"name": "木綿豆腐", "amount": "1丁"},
            {"name": "しめじ", "amount": "1/2パック"},
            {"name": "バター", "amount": "15g"},
            {"name": "醤油", "amount": "大さじ1"},
        ],
    },
    {
        "id": "23",
        "name": "ポテトサラダ",
        "servings": 4,
        "ingredients": [
            {"name": "じゃがいも", "amount": "3個"},
            {"name": "人参", "amount": "1/2本"},
            {"name": "きゅうり", "amount": "1本"},
            {"name": "卵", "amount": "2個"},
        ],
    },
    {
        "id": "24",
        "name": "アジの塩焼き",
        "servings": 2,
        "ingredients": [
            {"name": "アジ", "amount": "2尾"},
            {"name": "大根", "amount": "50g"},
            {"name": "醤油", "amount": "小さじ1"},
        ],
    },
    {
        "id": "25",
        "name": "卵焼き",
        "servings": 2,
        "ingredients": [
            {"name": "卵", "amount": "3個"},
            {"name": "醤油", "amount": "小さじ1"},
        ],
    },
    {
        "id": "26",
        "name": "ブロッコリーのおかか和え",
        "servings": 2,
        "ingredients": [
            {"name": "ブロッコリー", "amount": "200g"},
            {"name": "醤油", "amount": "大さじ1"},
        ],
    },
    {
        "id": "27",
        "name": "豚キムチ",
        "servings": 2,
        "ingredients": [
            {"name": "豚バラ肉", "amount": "200g"},
            {"name": "キャベツ", "amount": "150g"},
            {"name": "玉ねぎ", "amount": "1/2個"},
        ],
    },
    {
        "id": "28",
        "name": "鶏そぼろ丼",
        "servings": 2,
        "ingredients": [
            {"name": "鶏ひき肉", "amount": "200g"},
            {"name": "卵", "amount": "2個"},
            {"name": "ご飯", "amount": "400g"},
            {"name": "醤油", "amount": "大さじ2"},
        ],
    },
    {
        "id": "29",
        "name": "厚揚げの煮物",
        "servings": 2,
        "ingredients": [
            {"name": "厚揚げ", "amount": "200g"},
            {"name": "大根", "amount": "100g"},
            {"name": "醤油", "amount": "大さじ2"},
        ],
    },
    {
        "id": "30",
        "name": "温野菜サラダ",
        "servings": 2,
        "ingredients": [
            {"name": "ブロッコリー", "amount": "100g"},
            {"name": "人参", "amount": "1/2本"},
            {"name": "じゃがいも", "amount": "1個"},
            {"name": "キャベツ", "amount": "100g"},
        ],
    },
]


def process_recipe(recipe: dict, food_names: list[str] = None) -> dict:
    """レシピを処理して食材をマッチング"""
    if food_names is None:
        food_names = load_food_names()

    processed_ingredients = []
    for ing in recipe.get("ingredients", []):
        name = ing.get("name", "")
        amount_text = ing.get("amount", "")

        amount_g = parse_amount(amount_text)
        matched_food = match_ingredient(name, food_names)

        processed_ingredients.append({
            "original_name": name,
            "amount_text": amount_text,
            "amount_g": amount_g,
            "matched_food": matched_food,
        })

    return {
        "id": recipe.get("id"),
        "name": recipe.get("name"),
        "servings": recipe.get("servings", 1),
        "ingredients": processed_ingredients,
    }


def get_all_recipes(food_names: list[str] = None) -> list[dict]:
    """全レシピを取得（マッチング済み）"""
    if food_names is None:
        food_names = load_food_names()

    # まずファイルからロード
    recipes = load_sample_recipes()

    # なければサンプルデータを使用
    if not recipes:
        recipes = SAMPLE_RECIPES
        save_sample_recipes(recipes)

    return [process_recipe(r, food_names) for r in recipes]


if __name__ == "__main__":
    # テスト
    food_names = load_food_names()
    print(f"食品データ: {len(food_names)}件")

    print("\n=== 食材マッチングテスト ===")
    test_ingredients = [
        "鶏むね肉", "玉ねぎ", "人参", "卵", "サバ", "豆腐", "納豆", "ほうれん草"
    ]
    for ing in test_ingredients:
        matched = match_ingredient(ing, food_names)
        print(f"  {ing} → {matched}")

    print("\n=== 分量解析テスト ===")
    test_amounts = [
        "200g", "1/2個", "2切れ", "大さじ2", "1パック", "少々", "1丁"
    ]
    for amt in test_amounts:
        grams = parse_amount(amt)
        print(f"  {amt} → {grams}g")

    print("\n=== レシピ処理テスト ===")
    recipes = get_all_recipes(food_names)
    for recipe in recipes[:3]:
        print(f"\n{recipe['name']} ({recipe['servings']}人分)")
        for ing in recipe['ingredients']:
            status = "✓" if ing['matched_food'] else "✗"
            print(f"  {status} {ing['original_name']} {ing['amount_text']} → {ing['matched_food']} ({ing['amount_g']}g)")
