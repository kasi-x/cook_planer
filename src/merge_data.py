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
    # 野菜類
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
    "ブロッコリー": "ブロッコリー\u3000花序\u3000生",
    "とうもろこし": "（とうもろこし類）\u3000スイートコーン\u3000未熟種子\u3000生",
    "そらまめ": "そらまめ\u3000未熟豆\u3000生",

    # 鶏卵（サイズ問わず同一栄養価として扱う）
    "鶏卵（ＬＬ）": "鶏卵\u3000全卵\u3000生",
    "鶏卵（Ｌ）": "鶏卵\u3000全卵\u3000生",
    "鶏卵（Ｍ）": "鶏卵\u3000全卵\u3000生",
    "鶏卵（ＭＳ）": "鶏卵\u3000全卵\u3000生",
    "鶏卵（Ｓ）": "鶏卵\u3000全卵\u3000生",
    "鶏卵（ＳＳ）": "鶏卵\u3000全卵\u3000生",
    "鶏卵（特高）": "鶏卵\u3000全卵\u3000生",
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

    keimei_path = PROCESSED_DIR / "keimei_prices.csv"
    if keimei_path.exists():
        dfs.append(pd.read_csv(keimei_path))

    tokyo_path = PROCESSED_DIR / "tokyo_market_prices.csv"
    if tokyo_path.exists():
        dfs.append(pd.read_csv(tokyo_path))

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
        else:
            print(f"Warning: No nutrition data found for '{price_food_name}'")

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

    output_path = MERGED_DIR / "food_price_nutrition.csv"
    merged.to_csv(output_path, index=False)
    print(f"Saved {len(merged)} merged records with {len(merged.columns)} columns to {output_path}")


if __name__ == "__main__":
    main()
