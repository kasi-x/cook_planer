"""データ結合処理

各スクレイパーが生成したCSVを結合し、
価格と栄養価を統合したデータセットを作成する
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
PROCESSED_DIR = DATA_DIR / "processed"
MERGED_DIR = DATA_DIR / "merged"

# 価格データの食品名 → 栄養成分表の食品名マッピング
# 注: 栄養成分表は全角スペース(\u3000)を使用
FOOD_NAME_MAPPING = {
    # ==================== 野菜類 ====================
    "だいこん": "（だいこん類）\u3000だいこん\u3000根\u3000皮つき\u3000生",
    "かぶ": "かぶ\u3000根\u3000皮つき\u3000生",
    "にんじん": "（にんじん類）\u3000にんじん\u3000根\u3000皮つき\u3000生",
    "キャベツ": "（キャベツ類）\u3000キャベツ\u3000結球葉\u3000生",
    "レタス": "（レタス類）\u3000レタス\u3000土耕栽培\u3000結球葉\u3000生",
    "はくさい": "はくさい\u3000結球葉\u3000生",
    "ほうれんそう": "ほうれんそう\u3000葉\u3000通年平均\u3000生",
    "こまつな": "こまつな\u3000葉\u3000生",
    "ねぎ": "（ねぎ類）\u3000根深ねぎ\u3000葉\u3000軟白\u3000生",
    "たまねぎ": "（たまねぎ類）\u3000たまねぎ\u3000りん茎\u3000生",
    "きゅうり": "きゅうり\u3000果実\u3000生",
    "トマト": "（トマト類）\u3000赤色トマト\u3000果実\u3000生",
    "ミニトマト": "（トマト類）\u3000赤色ミニトマト\u3000果実\u3000生",
    "なす": "（なす類）\u3000なす\u3000果実\u3000生",
    "ピーマン": "（ピーマン類）\u3000青ピーマン\u3000果実\u3000生",
    "かぼちゃ": "（かぼちゃ類）\u3000西洋かぼちゃ\u3000果実\u3000生",
    "じゃがいも": "＜いも類＞\u3000じゃがいも\u3000塊茎\u3000皮つき\u3000生",
    "えだまめ": "えだまめ\u3000生",
    "いんげん": "いんげんまめ\u3000さやいんげん\u3000若ざや\u3000生",
    "スナップ実えんどう": "（えんどう類）\u3000スナップえんどう\u3000若ざや\u3000生",
    "ブロッコリー": "ブロッコリー\u3000花序\u3000生",
    "とうもろこし": "（とうもろこし類）\u3000スイートコーン\u3000未熟種子\u3000生",
    "そらまめ": "そらまめ\u3000未熟豆\u3000生",
    "さつまいも": "＜いも類＞\u3000（さつまいも類）\u3000さつまいも\u3000塊根\u3000皮つき\u3000生",
    "さといも": "＜いも類＞\u3000（さといも類）\u3000さといも\u3000球茎\u3000生",
    "ごぼう": "（ごぼう類）\u3000ごぼう\u3000根\u3000生",
    "れんこん": "れんこん\u3000根茎\u3000生",
    "ながいも": "＜いも類＞\u3000（やまのいも類）\u3000ながいも\u3000ながいも\u3000塊根\u3000生",
    "アスパラガス": "アスパラガス\u3000若茎\u3000生",
    "オクラ": "オクラ\u3000果実\u3000生",
    "もやし": "（もやし類）\u3000りょくとうもやし\u3000生",
    "ズッキーニ": "ズッキーニ\u3000果実\u3000生",
    "セロリ": "セロリ\u3000葉柄\u3000生",
    "しょうが": "（しょうが類）\u3000しょうが\u3000根茎\u3000皮なし\u3000生",
    "にんにく": "（にんにく類）\u3000にんにく\u3000りん茎\u3000生",
    "赤ピーマン": "（ピーマン類）\u3000赤ピーマン\u3000果実\u3000生",
    "黄ピーマン": "（ピーマン類）\u3000黄ピーマン\u3000果実\u3000生",
    "チンゲンサイ": "チンゲンサイ\u3000葉\u3000生",

    # ==================== 鶏卵（Lサイズのみ） ====================
    "鶏卵（Ｌ）": "鶏卵\u3000全卵\u3000生",

    # ==================== 穀類（米・パン・麺） ====================
    "米（精白米）": "こめ\u3000［水稲めし］\u3000精白米\u3000うるち米",
    "米（玄米）": "こめ\u3000［水稲めし］\u3000玄米",
    "もち米": "こめ\u3000［水稲めし］\u3000精白米\u3000もち米",
    "食パン": "こむぎ\u3000［パン類］\u3000食パン\u3000リーンタイプ",
    "フランスパン": "こむぎ\u3000［パン類］\u3000フランスパン",
    "ロールパン": "こむぎ\u3000［パン類］\u3000ロールパン",
    "うどん（乾）": "こむぎ\u3000［うどん・そうめん類］\u3000干しうどん\u3000乾",
    "そば（乾）": "そば\u3000干しそば\u3000乾",
    "スパゲッティ（乾）": "こむぎ\u3000［マカロニ・スパゲッティ類］\u3000マカロニ・スパゲッティ\u3000乾",
    "中華麺（生）": "こむぎ\u3000［中華めん類］\u3000中華めん\u3000生",
    "即席めん": "こむぎ\u3000［即席めん類］\u3000即席中華めん\u3000油揚げ味付け",

    # ==================== 肉類 ====================
    # 牛肉
    "牛肉（もも）": "＜畜肉類＞\u3000うし\u3000［和牛肉］\u3000もも\u3000赤肉\u3000生",
    "牛肉（ばら）": "＜畜肉類＞\u3000うし\u3000［和牛肉］\u3000ばら\u3000脂身つき\u3000生",
    "牛肉（ロース）": "＜畜肉類＞\u3000うし\u3000［和牛肉］\u3000リブロース\u3000脂身つき\u3000生",
    "牛肉（ひき肉）": "＜畜肉類＞\u3000うし\u3000［ひき肉］\u3000生",
    # 豚肉
    "豚肉（もも）": "＜畜肉類＞\u3000ぶた\u3000［大型種肉］\u3000もも\u3000赤肉\u3000生",
    "豚肉（ばら）": "＜畜肉類＞\u3000ぶた\u3000［大型種肉］\u3000ばら\u3000脂身つき\u3000生",
    "豚肉（ロース）": "＜畜肉類＞\u3000ぶた\u3000［大型種肉］\u3000ロース\u3000脂身つき\u3000生",
    "豚肉（ひき肉）": "＜畜肉類＞\u3000ぶた\u3000［ひき肉］\u3000生",
    # 鶏肉
    "鶏肉（もも）": "＜鳥肉類＞\u3000にわとり\u3000［若どり・主品目］\u3000もも\u3000皮つき\u3000生",
    "鶏肉（むね）": "＜鳥肉類＞\u3000にわとり\u3000［若どり・主品目］\u3000むね\u3000皮つき\u3000生",
    "鶏肉（ささみ）": "＜鳥肉類＞\u3000にわとり\u3000［若どり・副品目］\u3000ささみ\u3000生",
    "鶏肉（手羽）": "＜鳥肉類＞\u3000にわとり\u3000［若どり・主品目］\u3000手羽\u3000皮つき\u3000生",
    "鶏肉（ひき肉）": "＜鳥肉類＞\u3000にわとり\u3000［二次品目］\u3000ひき肉\u3000生",
    # 加工肉
    "ハム（ロース）": "＜畜肉類＞\u3000ぶた\u3000［ハム類］\u3000ロースハム\u3000ロースハム",
    "ベーコン": "＜畜肉類＞\u3000ぶた\u3000［ベーコン類］\u3000ばらベーコン\u3000ばらベーコン\u3000",
    "ソーセージ": "＜畜肉類＞\u3000ぶた\u3000［ソーセージ類］\u3000ウインナーソーセージ\u3000ウインナーソーセージ",

    # ==================== 魚介類 ====================
    "さけ": "＜魚類＞\u3000（さけ・ます類）\u3000しろさけ\u3000生",
    "さば": "＜魚類＞\u3000（さば類）\u3000まさば\u3000生",
    "あじ": "＜魚類＞\u3000（あじ類）\u3000まあじ\u3000皮つき\u3000生",
    "いわし": "＜魚類＞\u3000（いわし類）\u3000まいわし\u3000生",
    "さんま": "＜魚類＞\u3000さんま\u3000皮つき\u3000生",
    "ぶり": "＜魚類＞\u3000ぶり\u3000成魚\u3000生",
    "まぐろ（赤身）": "＜魚類＞\u3000（まぐろ類）\u3000くろまぐろ\u3000天然\u3000赤身\u3000生",
    "たら": "＜魚類＞\u3000（たら類）\u3000まだら\u3000生",
    "ほっけ": "＜魚類＞\u3000ほっけ\u3000生",
    "かつお": "＜魚類＞\u3000（かつお類）\u3000かつお\u3000春獲り\u3000生",
    # 貝類
    "あさり": "＜貝類＞\u3000あさり\u3000生",
    "しじみ": "＜貝類＞\u3000しじみ\u3000生",
    # 甲殻類
    "えび": "＜えび・かに類＞\u3000（えび類）\u3000くるまえび\u3000養殖\u3000生",
    # 練り物
    "ちくわ": "＜水産練り製品＞\u3000焼き竹輪",
    "かまぼこ": "＜水産練り製品＞\u3000蒸しかまぼこ",

    # ==================== 大豆製品 ====================
    "豆腐（木綿）": "だいず\u3000［豆腐・油揚げ類］\u3000木綿豆腐",
    "豆腐（絹ごし）": "だいず\u3000［豆腐・油揚げ類］\u3000絹ごし豆腐",
    "納豆": "だいず\u3000［納豆類］\u3000糸引き納豆",
    "油揚げ": "だいず\u3000［豆腐・油揚げ類］\u3000油揚げ\u3000生",
    "厚揚げ": "だいず\u3000［豆腐・油揚げ類］\u3000生揚げ",
    "豆乳": "だいず\u3000［その他］\u3000豆乳\u3000豆乳",

    # ==================== 乳製品 ====================
    "牛乳": "＜牛乳及び乳製品＞\u3000（液状乳類）\u3000普通牛乳",
    "ヨーグルト（プレーン）": "＜牛乳及び乳製品＞\u3000（発酵乳・乳酸菌飲料）\u3000ヨーグルト\u3000全脂無糖",
    "チーズ（プロセス）": "＜牛乳及び乳製品＞\u3000（チーズ類）\u3000プロセスチーズ",
    "バター": "（バター類）\u3000無発酵バター\u3000有塩バター",

    # ==================== 油脂 ====================
    "サラダ油": "（植物油脂類）\u3000調合油",
    "オリーブオイル": "（植物油脂類）\u3000オリーブ油",
    "ごま油": "（植物油脂類）\u3000ごま油",

    # ==================== 調味料 ====================
    "味噌": "＜調味料類＞\u3000（みそ類）\u3000米みそ\u3000淡色辛みそ",
    "醤油": "＜調味料類＞\u3000（しょうゆ類）\u3000こいくちしょうゆ",
    "砂糖": "（砂糖類）\u3000車糖\u3000上白糖",
    "塩": "＜調味料類＞\u3000（食塩類）\u3000食塩",

    # ==================== きのこ類 ====================
    "しいたけ（生）": "しいたけ\u3000生しいたけ\u3000菌床栽培\u3000生",
    "えのきたけ": "えのきたけ\u3000生",
    "しめじ": "（しめじ類）\u3000ぶなしめじ\u3000生",
    "まいたけ": "まいたけ\u3000生",
    "エリンギ": "（ひらたけ類）\u3000エリンギ\u3000生",

    # ==================== 海藻類 ====================
    "わかめ（乾燥）": "わかめ\u3000乾燥わかめ\u3000素干し",
    "のり（焼き）": "あまのり\u3000焼きのり",
    "ひじき（乾燥）": "ひじき\u3000ほしひじき\u3000ステンレス釜\u3000乾",

    # ==================== 果物 ====================
    "バナナ": "バナナ\u3000生",
    "りんご": "りんご\u3000皮つき\u3000生",
    "みかん": "（かんきつ類）\u3000うんしゅうみかん\u3000じょうのう\u3000普通\u3000生",
    "オレンジ": "（かんきつ類）\u3000オレンジ\u3000ネーブル\u3000砂じょう\u3000生",
    "キウイ": "キウイフルーツ\u3000緑肉種\u3000生",
    "うめ": "うめ\u3000生",

    # ==================== その他 ====================
    "こんにゃく": "＜いも類＞\u3000こんにゃく\u3000板こんにゃく\u3000精粉こんにゃく",
    "しらたき": "＜いも類＞\u3000こんにゃく\u3000しらたき",
}

# マージする栄養素の一覧
NUTRITION_COLUMNS = [
    'energy_kcal',
    'protein_g',
    'fat_g',
    'fiber_g',
    'carbohydrate_g',
    # ミネラル
    'potassium_mg',
    'calcium_mg',
    'magnesium_mg',
    'phosphorus_mg',
    'iron_mg',
    'zinc_mg',
    'copper_mg',
    # ビタミン
    'vitamin_a_ug',
    'vitamin_d_ug',
    'vitamin_e_mg',
    'vitamin_k_ug',
    'vitamin_b1_mg',
    'vitamin_b2_mg',
    'niacin_mg',
    'vitamin_b6_mg',
    'vitamin_b12_ug',
    'folate_ug',
    'pantothenic_mg',
    'vitamin_c_mg',
]


def load_price_data() -> pd.DataFrame:
    """価格データを読み込み"""
    dfs = []

    # 鶏卵
    keimei_path = PROCESSED_DIR / "keimei_prices.csv"
    if keimei_path.exists():
        df = pd.read_csv(keimei_path)
        # Lサイズのみ抽出
        df = df[df['food_name'] == '鶏卵（Ｌ）']
        dfs.append(df)

    # 野菜
    tokyo_path = PROCESSED_DIR / "tokyo_market_prices.csv"
    if tokyo_path.exists():
        dfs.append(pd.read_csv(tokyo_path))

    # 水産物
    fish_path = PROCESSED_DIR / "tokyo_fish_prices.csv"
    if fish_path.exists():
        dfs.append(pd.read_csv(fish_path))

    # 食肉
    meat_path = PROCESSED_DIR / "tokyo_meat_prices.csv"
    if meat_path.exists():
        dfs.append(pd.read_csv(meat_path))

    # 主食・乳製品など
    maff_path = PROCESSED_DIR / "maff_staple_prices.csv"
    if maff_path.exists():
        dfs.append(pd.read_csv(maff_path))

    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()


def load_nutrition_data() -> pd.DataFrame:
    """栄養価データを読み込み"""
    mext_path = PROCESSED_DIR / "mext_nutrition.csv"
    if mext_path.exists():
        return pd.read_csv(mext_path)
    return pd.DataFrame()


def merge_price_and_nutrition(
    prices: pd.DataFrame,
    nutrition: pd.DataFrame
) -> pd.DataFrame:
    """価格と栄養価を食品名でマージ"""
    if prices.empty or nutrition.empty:
        print("Warning: Price or nutrition data is empty")
        return pd.DataFrame()

    nutrition_lookup = nutrition.set_index('food_name')

    records = []
    matched = set()
    unmatched = []

    for _, price_row in prices.iterrows():
        price_food_name = price_row['food_name']
        nutrition_food_name = FOOD_NAME_MAPPING.get(price_food_name)

        if nutrition_food_name and nutrition_food_name in nutrition_lookup.index:
            nutr = nutrition_lookup.loc[nutrition_food_name]
            record = {
                'food_name': price_food_name,
                'nutrition_name': nutrition_food_name,
                'price_per_100g': price_row['price_per_100g'],
                'source_price': price_row.get('source', ''),
                'source_nutrition': nutr.get('source', ''),
                'date': price_row.get('date', ''),
            }
            # 全栄養素を追加
            for col in NUTRITION_COLUMNS:
                record[col] = nutr.get(col, 0) if pd.notna(nutr.get(col)) else 0

            records.append(record)
            matched.add(price_food_name)
        else:
            if price_food_name not in matched:
                unmatched.append(price_food_name)

    # 未マッチの食品を報告
    if unmatched:
        print(f"Warning: {len(set(unmatched))} foods without nutrition data:")
        for name in sorted(set(unmatched))[:20]:
            print(f"  - {name}")
        if len(set(unmatched)) > 20:
            print(f"  ... and {len(set(unmatched)) - 20} more")

    return pd.DataFrame(records)


def main():
    MERGED_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading price data...")
    prices = load_price_data()
    print(f"  Loaded {len(prices)} price records")

    print("Loading nutrition data...")
    nutrition = load_nutrition_data()
    print(f"  Loaded {len(nutrition)} nutrition records")

    print("Merging data...")
    merged = merge_price_and_nutrition(prices, nutrition)

    # 重複除去（同一食品名は価格の平均を取る）
    if not merged.empty:
        merged = merged.groupby('food_name').agg({
            'nutrition_name': 'first',
            'price_per_100g': 'mean',
            'source_price': 'first',
            'source_nutrition': 'first',
            'date': 'first',
            **{col: 'first' for col in NUTRITION_COLUMNS}
        }).reset_index()
        merged['price_per_100g'] = merged['price_per_100g'].round(2)

    output_path = MERGED_DIR / "food_price_nutrition.csv"
    merged.to_csv(output_path, index=False)
    print(f"Saved {len(merged)} merged records with {len(merged.columns)} columns to {output_path}")

    # カテゴリ別の集計を表示
    print("\n=== Merged foods by category ===")
    categories = {
        "穀類": ["米", "パン", "うどん", "そば", "スパゲッティ", "麺", "もち"],
        "肉類": ["牛肉", "豚肉", "鶏肉", "ハム", "ベーコン", "ソーセージ"],
        "魚介類": ["さけ", "さば", "あじ", "いわし", "まぐろ", "たら", "えび", "あさり", "ちくわ", "かまぼこ"],
        "卵": ["鶏卵"],
        "乳製品": ["牛乳", "ヨーグルト", "チーズ", "バター"],
        "大豆製品": ["豆腐", "納豆", "油揚げ", "厚揚げ", "豆乳"],
        "野菜": ["だいこん", "キャベツ", "レタス", "ほうれんそう", "トマト", "じゃがいも"],
        "きのこ": ["しいたけ", "えのき", "しめじ", "まいたけ", "エリンギ"],
        "果物": ["バナナ", "りんご", "みかん", "オレンジ", "キウイ"],
    }

    for category, keywords in categories.items():
        count = sum(1 for name in merged['food_name'] if any(kw in name for kw in keywords))
        if count > 0:
            print(f"  {category}: {count}品")


if __name__ == "__main__":
    main()
