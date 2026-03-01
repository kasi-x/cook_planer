"""調理による栄養変化サービス

MEXT食品成分DBの調理済み食品データ（ゆで/焼き/揚げ等）を活用し、
調理法に応じた栄養価変化を反映する。
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"
MEXT_PATH = DATA_DIR / "processed" / "mext_nutrition.csv"

COOKING_METHODS = ["生", "ゆで", "焼き", "揚げ", "蒸し", "炒め"]

# 調理法キーワードのマッピング（MEXTデータでの表記）
COOKING_METHOD_KEYWORDS = {
    "生": ["生"],
    "ゆで": ["ゆで"],
    "焼き": ["焼き"],
    "揚げ": ["揚げ", "油揚げ", "フライ", "天ぷら"],
    "蒸し": ["蒸し"],
    "炒め": ["炒め", "油いため"],
}

_mext_df: pd.DataFrame | None = None


def _load_mext_data() -> pd.DataFrame:
    """MEXT食品成分データを読み込む。

    初回呼び出し時にCSVを読み込み、以降はモジュールレベルの _mext_df にキャッシュする。
    プロセス再起動までCSV更新は反映されない（起動時1回読み込み方式）。
    """
    global _mext_df
    if _mext_df is None:
        if MEXT_PATH.exists():
            _mext_df = pd.read_csv(MEXT_PATH)
        else:
            _mext_df = pd.DataFrame()
    return _mext_df


def find_cooked_variant(food_name: str, method: str) -> str | None:
    """食品名+調理法 → 調理済み食品名を検索

    例: 「ほうれんそう\u3000葉\u3000通年平均\u3000生」+ method=「ゆで」
      → 「ほうれんそう\u3000葉\u3000通年平均\u3000ゆで」
    """
    if method == "生":
        return food_name

    df = _load_mext_data()
    if df.empty:
        return None

    # 「生」を調理法に置換してみる
    if "生" in food_name:
        for keyword in COOKING_METHOD_KEYWORDS.get(method, [method]):
            candidate = food_name.replace("生", keyword)
            matches = df[df["food_name"] == candidate]
            if not matches.empty:
                return candidate

    # ベース名（「生」を除去）で部分一致検索
    base_name = food_name.replace("\u3000生", "").replace("　生", "").rstrip()
    for keyword in COOKING_METHOD_KEYWORDS.get(method, [method]):
        search_name = f"{base_name}\u3000{keyword}"
        matches = df[df["food_name"].str.startswith(search_name, na=False)]
        if not matches.empty:
            return matches.iloc[0]["food_name"]

    return None


def get_waste_rate(food_name: str) -> float:
    """食品の廃棄率を取得（0-100の百分率）"""
    df = _load_mext_data()
    if df.empty:
        return 0.0

    matches = df[df["food_name"] == food_name]
    if matches.empty:
        return 0.0

    rate = matches.iloc[0].get("waste_rate", 0)
    return float(rate) if pd.notna(rate) else 0.0


def get_cooked_nutrition(food_name: str, method: str) -> dict | None:
    """調理済み食品の栄養価を取得"""
    cooked_name = find_cooked_variant(food_name, method)
    if not cooked_name:
        return None

    df = _load_mext_data()
    if df.empty:
        return None

    matches = df[df["food_name"] == cooked_name]
    if matches.empty:
        return None

    row = matches.iloc[0]
    nutrition_cols = [
        "energy_kcal", "protein_g", "fat_g", "fiber_g", "carbohydrate_g",
        "calcium_mg", "iron_mg", "vitamin_a_ug", "vitamin_c_mg",
        "vitamin_b1_mg", "vitamin_b2_mg",
    ]

    result = {"food_name": cooked_name, "method": method}
    for col in nutrition_cols:
        val = row.get(col, 0)
        result[col] = float(val) if pd.notna(val) else 0.0

    waste_rate = row.get("waste_rate", 0)
    result["waste_rate"] = float(waste_rate) if pd.notna(waste_rate) else 0.0

    return result


def apply_cooking_change(food_name: str, amount_g: float, method: str) -> dict:
    """調理法適用後の食材情報を返す

    Returns:
        dict with cooked_food_name, effective_amount_g (廃棄率考慮), method, nutrition
    """
    waste_rate = get_waste_rate(food_name)
    effective_amount = amount_g * (1 - waste_rate / 100)

    cooked_nutrition = get_cooked_nutrition(food_name, method)
    cooked_name = cooked_nutrition["food_name"] if cooked_nutrition else food_name

    return {
        "original_food_name": food_name,
        "cooked_food_name": cooked_name,
        "method": method,
        "original_amount_g": amount_g,
        "effective_amount_g": round(effective_amount, 1),
        "waste_rate": waste_rate,
        "nutrition": cooked_nutrition,
    }


def get_available_methods(food_name: str) -> list[str]:
    """指定食品で利用可能な調理法を返す"""
    available = ["生"]  # 生は常に可能

    df = _load_mext_data()
    if df.empty:
        return available

    for method in COOKING_METHODS:
        if method == "生":
            continue
        if find_cooked_variant(food_name, method):
            available.append(method)

    return available
