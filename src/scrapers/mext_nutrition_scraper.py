"""文部科学省 食品成分データベーススクレイパー

Source: https://www.mext.go.jp/a_menu/syokuhinseibun/mext_00001.html
食品成分表（八訂増補2023年）から栄養価情報を取得する
"""

import requests
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
OUTPUT_DIR = DATA_DIR / "processed"

EXCEL_URL = "https://www.mext.go.jp/content/20230428-mxt_kagsei-mext_00001_012.xlsx"


def download_excel(url: str, output_path: Path) -> Path:
    """Excelファイルをダウンロード"""
    if output_path.exists():
        print(f"Using cached file: {output_path}")
        return output_path

    response = requests.get(url)
    response.raise_for_status()
    output_path.write_bytes(response.content)
    return output_path


def parse_nutrition_data(excel_path: Path) -> pd.DataFrame:
    """Excelから栄養価データを抽出

    100gあたりの栄養価を抽出する
    """
    # 全体シートを読み込み（行12からデータ開始）
    df = pd.read_excel(excel_path, sheet_name='表全体', header=None, skiprows=12)

    # 必要な列を抽出（全62列から主要栄養素を選択）
    columns = {
        # 基本情報
        0: 'food_group',
        1: 'food_number',
        3: 'food_name',
        4: 'waste_rate',
        # エネルギー
        6: 'energy_kcal',
        # 三大栄養素
        9: 'protein_g',
        12: 'fat_g',
        18: 'fiber_g',
        20: 'carbohydrate_g',
        # ミネラル
        24: 'potassium_mg',      # カリウム
        25: 'calcium_mg',        # カルシウム
        26: 'magnesium_mg',      # マグネシウム
        27: 'phosphorus_mg',     # リン
        28: 'iron_mg',           # 鉄
        29: 'zinc_mg',           # 亜鉛
        30: 'copper_mg',         # 銅
        # ビタミン
        42: 'vitamin_a_ug',      # ビタミンA (RAE)
        43: 'vitamin_d_ug',      # ビタミンD
        44: 'vitamin_e_mg',      # ビタミンE (α-トコフェロール)
        48: 'vitamin_k_ug',      # ビタミンK
        49: 'vitamin_b1_mg',     # ビタミンB1
        50: 'vitamin_b2_mg',     # ビタミンB2
        51: 'niacin_mg',         # ナイアシン
        53: 'vitamin_b6_mg',     # ビタミンB6
        54: 'vitamin_b12_ug',    # ビタミンB12
        55: 'folate_ug',         # 葉酸
        56: 'pantothenic_mg',    # パントテン酸
        58: 'vitamin_c_mg',      # ビタミンC
    }

    result = df[[col for col in columns.keys()]].copy()
    result.columns = [columns[col] for col in columns.keys()]

    # 数値変換（括弧付きや'-'を処理）
    numeric_cols = [col for col in result.columns if col not in ['food_group', 'food_number', 'food_name']]
    for col in numeric_cols:
        result[col] = result[col].apply(parse_numeric)

    # 欠損値を除去
    result = result.dropna(subset=['food_name'])

    # ソース情報を追加
    result['source'] = '文部科学省食品成分表八訂'
    result['per_100g'] = True

    return result


def parse_numeric(value):
    """数値を解析（括弧付き推定値、'-'、'Tr'などを処理）"""
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if s in ['-', '－', '―', '', '…']:
        return None
    if s in ['Tr', '(Tr)', '(0)']:
        return 0.0
    # 括弧を除去（推定値）
    s = s.replace('(', '').replace(')', '')
    s = s.replace('*', '')
    try:
        return float(s)
    except ValueError:
        return None


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    excel_path = RAW_DIR / "mext_nutrition.xlsx"

    print(f"Downloading Excel from {EXCEL_URL}")
    download_excel(EXCEL_URL, excel_path)

    print("Parsing nutrition data...")
    df = parse_nutrition_data(excel_path)

    output_path = OUTPUT_DIR / "mext_nutrition.csv"
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} items with {len(df.columns)} columns to {output_path}")


if __name__ == "__main__":
    main()
