"""厚生労働省 日本人の食事摂取基準（2020年版）データ

Source: https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/kenkou/eiyou/syokuji_kijyun.html

身体活動レベル「ふつう（II）」を基準として使用
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "processed"

# 年齢グループ定義
AGE_GROUPS = [
    {"id": "0-5m", "label": "0-5ヶ月", "min_age": 0, "max_age": 0, "months": (0, 5)},
    {"id": "6-11m", "label": "6-11ヶ月", "min_age": 0, "max_age": 0, "months": (6, 11)},
    {"id": "1-2", "label": "1-2歳", "min_age": 1, "max_age": 2},
    {"id": "3-5", "label": "3-5歳", "min_age": 3, "max_age": 5},
    {"id": "6-7", "label": "6-7歳", "min_age": 6, "max_age": 7},
    {"id": "8-9", "label": "8-9歳", "min_age": 8, "max_age": 9},
    {"id": "10-11", "label": "10-11歳", "min_age": 10, "max_age": 11},
    {"id": "12-14", "label": "12-14歳", "min_age": 12, "max_age": 14},
    {"id": "15-17", "label": "15-17歳", "min_age": 15, "max_age": 17},
    {"id": "18-29", "label": "18-29歳", "min_age": 18, "max_age": 29},
    {"id": "30-49", "label": "30-49歳", "min_age": 30, "max_age": 49},
    {"id": "50-64", "label": "50-64歳", "min_age": 50, "max_age": 64},
    {"id": "65-74", "label": "65-74歳", "min_age": 65, "max_age": 74},
    {"id": "75+", "label": "75歳以上", "min_age": 75, "max_age": 120},
]

# 栄養素キーの定義
NUTRIENT_KEYS = [
    "energy_kcal",       # エネルギー
    "protein_g",         # たんぱく質
    "fat_percent",       # 脂質（エネルギー比率%）
    "carbohydrate_percent", # 炭水化物（エネルギー比率%）
    "fiber_g",           # 食物繊維
    "potassium_mg",      # カリウム
    "calcium_mg",        # カルシウム
    "magnesium_mg",      # マグネシウム
    "phosphorus_mg",     # リン
    "iron_mg",           # 鉄
    "zinc_mg",           # 亜鉛
    "copper_mg",         # 銅
    "vitamin_a_ug",      # ビタミンA (RAE)
    "vitamin_d_ug",      # ビタミンD
    "vitamin_e_mg",      # ビタミンE
    "vitamin_k_ug",      # ビタミンK
    "vitamin_b1_mg",     # ビタミンB1
    "vitamin_b2_mg",     # ビタミンB2
    "niacin_mg",         # ナイアシン (NE)
    "vitamin_b6_mg",     # ビタミンB6
    "vitamin_b12_ug",    # ビタミンB12
    "folate_ug",         # 葉酸
    "pantothenic_mg",    # パントテン酸
    "vitamin_c_mg",      # ビタミンC
    "sodium_mg",         # ナトリウム（食塩相当量から計算）
    "salt_g",            # 食塩相当量
]

# 推奨量・目安量（身体活動レベル「ふつう」）
# None = データなし or 設定なし
DIETARY_REFERENCE_INTAKES = {
    # ========== 男性 ==========
    "male": {
        "1-2": {
            "energy_kcal": 950, "protein_g": 20, "fat_percent": 25, "fiber_g": None,
            "potassium_mg": 900, "calcium_mg": 450, "magnesium_mg": 70, "phosphorus_mg": 500,
            "iron_mg": 4.5, "zinc_mg": 3, "copper_mg": 0.3,
            "vitamin_a_ug": 400, "vitamin_d_ug": 3.0, "vitamin_e_mg": 3.5, "vitamin_k_ug": 50,
            "vitamin_b1_mg": 0.5, "vitamin_b2_mg": 0.6, "niacin_mg": 5, "vitamin_b6_mg": 0.5,
            "vitamin_b12_ug": 0.9, "folate_ug": 90, "pantothenic_mg": 3, "vitamin_c_mg": 40,
            "salt_g": 3.0,
        },
        "3-5": {
            "energy_kcal": 1300, "protein_g": 25, "fat_percent": 25, "fiber_g": 8,
            "potassium_mg": 1000, "calcium_mg": 600, "magnesium_mg": 100, "phosphorus_mg": 700,
            "iron_mg": 5.5, "zinc_mg": 4, "copper_mg": 0.4,
            "vitamin_a_ug": 450, "vitamin_d_ug": 3.5, "vitamin_e_mg": 4.0, "vitamin_k_ug": 60,
            "vitamin_b1_mg": 0.7, "vitamin_b2_mg": 0.8, "niacin_mg": 7, "vitamin_b6_mg": 0.6,
            "vitamin_b12_ug": 1.1, "folate_ug": 110, "pantothenic_mg": 4, "vitamin_c_mg": 50,
            "salt_g": 3.5,
        },
        "6-7": {
            "energy_kcal": 1550, "protein_g": 30, "fat_percent": 25, "fiber_g": 10,
            "potassium_mg": 1300, "calcium_mg": 600, "magnesium_mg": 130, "phosphorus_mg": 900,
            "iron_mg": 6.5, "zinc_mg": 5, "copper_mg": 0.5,
            "vitamin_a_ug": 400, "vitamin_d_ug": 4.5, "vitamin_e_mg": 5.0, "vitamin_k_ug": 80,
            "vitamin_b1_mg": 0.8, "vitamin_b2_mg": 0.9, "niacin_mg": 9, "vitamin_b6_mg": 0.8,
            "vitamin_b12_ug": 1.3, "folate_ug": 140, "pantothenic_mg": 5, "vitamin_c_mg": 60,
            "salt_g": 4.5,
        },
        "8-9": {
            "energy_kcal": 1850, "protein_g": 40, "fat_percent": 25, "fiber_g": 11,
            "potassium_mg": 1600, "calcium_mg": 650, "magnesium_mg": 170, "phosphorus_mg": 1000,
            "iron_mg": 8.0, "zinc_mg": 6, "copper_mg": 0.6,
            "vitamin_a_ug": 500, "vitamin_d_ug": 5.0, "vitamin_e_mg": 5.5, "vitamin_k_ug": 90,
            "vitamin_b1_mg": 1.0, "vitamin_b2_mg": 1.1, "niacin_mg": 11, "vitamin_b6_mg": 0.9,
            "vitamin_b12_ug": 1.6, "folate_ug": 160, "pantothenic_mg": 5, "vitamin_c_mg": 70,
            "salt_g": 5.0,
        },
        "10-11": {
            "energy_kcal": 2250, "protein_g": 50, "fat_percent": 25, "fiber_g": 13,
            "potassium_mg": 2000, "calcium_mg": 700, "magnesium_mg": 210, "phosphorus_mg": 1100,
            "iron_mg": 10.0, "zinc_mg": 7, "copper_mg": 0.7,
            "vitamin_a_ug": 600, "vitamin_d_ug": 6.5, "vitamin_e_mg": 5.5, "vitamin_k_ug": 110,
            "vitamin_b1_mg": 1.2, "vitamin_b2_mg": 1.4, "niacin_mg": 13, "vitamin_b6_mg": 1.1,
            "vitamin_b12_ug": 1.9, "folate_ug": 190, "pantothenic_mg": 6, "vitamin_c_mg": 85,
            "salt_g": 6.0,
        },
        "12-14": {
            "energy_kcal": 2600, "protein_g": 60, "fat_percent": 25, "fiber_g": 17,
            "potassium_mg": 2400, "calcium_mg": 1000, "magnesium_mg": 290, "phosphorus_mg": 1200,
            "iron_mg": 10.0, "zinc_mg": 10, "copper_mg": 0.8,
            "vitamin_a_ug": 800, "vitamin_d_ug": 8.0, "vitamin_e_mg": 6.5, "vitamin_k_ug": 140,
            "vitamin_b1_mg": 1.4, "vitamin_b2_mg": 1.6, "niacin_mg": 15, "vitamin_b6_mg": 1.4,
            "vitamin_b12_ug": 2.4, "folate_ug": 230, "pantothenic_mg": 7, "vitamin_c_mg": 100,
            "salt_g": 7.0,
        },
        "15-17": {
            "energy_kcal": 2800, "protein_g": 65, "fat_percent": 25, "fiber_g": 19,
            "potassium_mg": 2700, "calcium_mg": 800, "magnesium_mg": 360, "phosphorus_mg": 1200,
            "iron_mg": 10.0, "zinc_mg": 12, "copper_mg": 1.0,
            "vitamin_a_ug": 900, "vitamin_d_ug": 9.0, "vitamin_e_mg": 7.0, "vitamin_k_ug": 160,
            "vitamin_b1_mg": 1.5, "vitamin_b2_mg": 1.7, "niacin_mg": 17, "vitamin_b6_mg": 1.5,
            "vitamin_b12_ug": 2.4, "folate_ug": 240, "pantothenic_mg": 7, "vitamin_c_mg": 100,
            "salt_g": 7.5,
        },
        "18-29": {
            "energy_kcal": 2650, "protein_g": 65, "fat_percent": 25, "fiber_g": 21,
            "potassium_mg": 2500, "calcium_mg": 800, "magnesium_mg": 340, "phosphorus_mg": 1000,
            "iron_mg": 7.5, "zinc_mg": 11, "copper_mg": 0.9,
            "vitamin_a_ug": 850, "vitamin_d_ug": 8.5, "vitamin_e_mg": 6.0, "vitamin_k_ug": 150,
            "vitamin_b1_mg": 1.4, "vitamin_b2_mg": 1.6, "niacin_mg": 15, "vitamin_b6_mg": 1.4,
            "vitamin_b12_ug": 2.4, "folate_ug": 240, "pantothenic_mg": 5, "vitamin_c_mg": 100,
            "salt_g": 7.5,
        },
        "30-49": {
            "energy_kcal": 2700, "protein_g": 65, "fat_percent": 25, "fiber_g": 21,
            "potassium_mg": 2500, "calcium_mg": 750, "magnesium_mg": 370, "phosphorus_mg": 1000,
            "iron_mg": 7.5, "zinc_mg": 11, "copper_mg": 0.9,
            "vitamin_a_ug": 900, "vitamin_d_ug": 8.5, "vitamin_e_mg": 6.0, "vitamin_k_ug": 150,
            "vitamin_b1_mg": 1.4, "vitamin_b2_mg": 1.6, "niacin_mg": 15, "vitamin_b6_mg": 1.4,
            "vitamin_b12_ug": 2.4, "folate_ug": 240, "pantothenic_mg": 5, "vitamin_c_mg": 100,
            "salt_g": 7.5,
        },
        "50-64": {
            "energy_kcal": 2600, "protein_g": 65, "fat_percent": 25, "fiber_g": 21,
            "potassium_mg": 2500, "calcium_mg": 750, "magnesium_mg": 370, "phosphorus_mg": 1000,
            "iron_mg": 7.5, "zinc_mg": 11, "copper_mg": 0.9,
            "vitamin_a_ug": 900, "vitamin_d_ug": 8.5, "vitamin_e_mg": 7.0, "vitamin_k_ug": 150,
            "vitamin_b1_mg": 1.3, "vitamin_b2_mg": 1.5, "niacin_mg": 14, "vitamin_b6_mg": 1.4,
            "vitamin_b12_ug": 2.4, "folate_ug": 240, "pantothenic_mg": 5, "vitamin_c_mg": 100,
            "salt_g": 7.5,
        },
        "65-74": {
            "energy_kcal": 2400, "protein_g": 60, "fat_percent": 25, "fiber_g": 20,
            "potassium_mg": 2500, "calcium_mg": 750, "magnesium_mg": 350, "phosphorus_mg": 1000,
            "iron_mg": 7.5, "zinc_mg": 11, "copper_mg": 0.9,
            "vitamin_a_ug": 850, "vitamin_d_ug": 8.5, "vitamin_e_mg": 7.0, "vitamin_k_ug": 150,
            "vitamin_b1_mg": 1.2, "vitamin_b2_mg": 1.4, "niacin_mg": 13, "vitamin_b6_mg": 1.4,
            "vitamin_b12_ug": 2.4, "folate_ug": 240, "pantothenic_mg": 5, "vitamin_c_mg": 100,
            "salt_g": 7.5,
        },
        "75+": {
            "energy_kcal": 2100, "protein_g": 60, "fat_percent": 25, "fiber_g": 20,
            "potassium_mg": 2500, "calcium_mg": 750, "magnesium_mg": 320, "phosphorus_mg": 1000,
            "iron_mg": 7.0, "zinc_mg": 10, "copper_mg": 0.8,
            "vitamin_a_ug": 800, "vitamin_d_ug": 8.5, "vitamin_e_mg": 6.5, "vitamin_k_ug": 150,
            "vitamin_b1_mg": 1.1, "vitamin_b2_mg": 1.3, "niacin_mg": 12, "vitamin_b6_mg": 1.4,
            "vitamin_b12_ug": 2.4, "folate_ug": 240, "pantothenic_mg": 5, "vitamin_c_mg": 100,
            "salt_g": 7.5,
        },
    },
    # ========== 女性 ==========
    "female": {
        "1-2": {
            "energy_kcal": 900, "protein_g": 20, "fat_percent": 25, "fiber_g": None,
            "potassium_mg": 800, "calcium_mg": 400, "magnesium_mg": 70, "phosphorus_mg": 500,
            "iron_mg": 4.5, "zinc_mg": 3, "copper_mg": 0.3,
            "vitamin_a_ug": 350, "vitamin_d_ug": 3.5, "vitamin_e_mg": 3.5, "vitamin_k_ug": 50,
            "vitamin_b1_mg": 0.5, "vitamin_b2_mg": 0.5, "niacin_mg": 5, "vitamin_b6_mg": 0.5,
            "vitamin_b12_ug": 0.9, "folate_ug": 90, "pantothenic_mg": 3, "vitamin_c_mg": 40,
            "salt_g": 3.0,
        },
        "3-5": {
            "energy_kcal": 1250, "protein_g": 25, "fat_percent": 25, "fiber_g": 8,
            "potassium_mg": 1000, "calcium_mg": 550, "magnesium_mg": 100, "phosphorus_mg": 600,
            "iron_mg": 5.5, "zinc_mg": 4, "copper_mg": 0.4,
            "vitamin_a_ug": 450, "vitamin_d_ug": 3.5, "vitamin_e_mg": 4.0, "vitamin_k_ug": 60,
            "vitamin_b1_mg": 0.7, "vitamin_b2_mg": 0.8, "niacin_mg": 7, "vitamin_b6_mg": 0.6,
            "vitamin_b12_ug": 1.1, "folate_ug": 110, "pantothenic_mg": 4, "vitamin_c_mg": 50,
            "salt_g": 3.5,
        },
        "6-7": {
            "energy_kcal": 1450, "protein_g": 30, "fat_percent": 25, "fiber_g": 10,
            "potassium_mg": 1200, "calcium_mg": 550, "magnesium_mg": 130, "phosphorus_mg": 800,
            "iron_mg": 6.5, "zinc_mg": 5, "copper_mg": 0.5,
            "vitamin_a_ug": 400, "vitamin_d_ug": 5.0, "vitamin_e_mg": 5.0, "vitamin_k_ug": 80,
            "vitamin_b1_mg": 0.8, "vitamin_b2_mg": 0.9, "niacin_mg": 8, "vitamin_b6_mg": 0.7,
            "vitamin_b12_ug": 1.3, "folate_ug": 140, "pantothenic_mg": 5, "vitamin_c_mg": 60,
            "salt_g": 4.5,
        },
        "8-9": {
            "energy_kcal": 1700, "protein_g": 40, "fat_percent": 25, "fiber_g": 11,
            "potassium_mg": 1500, "calcium_mg": 750, "magnesium_mg": 160, "phosphorus_mg": 900,
            "iron_mg": 8.5, "zinc_mg": 5, "copper_mg": 0.5,
            "vitamin_a_ug": 500, "vitamin_d_ug": 6.0, "vitamin_e_mg": 5.5, "vitamin_k_ug": 90,
            "vitamin_b1_mg": 0.9, "vitamin_b2_mg": 1.0, "niacin_mg": 10, "vitamin_b6_mg": 0.9,
            "vitamin_b12_ug": 1.6, "folate_ug": 160, "pantothenic_mg": 5, "vitamin_c_mg": 70,
            "salt_g": 5.0,
        },
        "10-11": {
            "energy_kcal": 2100, "protein_g": 50, "fat_percent": 25, "fiber_g": 13,
            "potassium_mg": 1900, "calcium_mg": 750, "magnesium_mg": 220, "phosphorus_mg": 1000,
            "iron_mg": 10.0, "zinc_mg": 7, "copper_mg": 0.7,
            "vitamin_a_ug": 600, "vitamin_d_ug": 8.0, "vitamin_e_mg": 5.5, "vitamin_k_ug": 110,
            "vitamin_b1_mg": 1.1, "vitamin_b2_mg": 1.3, "niacin_mg": 12, "vitamin_b6_mg": 1.1,
            "vitamin_b12_ug": 1.9, "folate_ug": 190, "pantothenic_mg": 6, "vitamin_c_mg": 85,
            "salt_g": 6.0,
        },
        "12-14": {
            "energy_kcal": 2400, "protein_g": 55, "fat_percent": 25, "fiber_g": 16,
            "potassium_mg": 2200, "calcium_mg": 800, "magnesium_mg": 290, "phosphorus_mg": 1000,
            "iron_mg": 10.0, "zinc_mg": 8, "copper_mg": 0.8,
            "vitamin_a_ug": 700, "vitamin_d_ug": 9.5, "vitamin_e_mg": 6.0, "vitamin_k_ug": 150,
            "vitamin_b1_mg": 1.3, "vitamin_b2_mg": 1.4, "niacin_mg": 14, "vitamin_b6_mg": 1.3,
            "vitamin_b12_ug": 2.4, "folate_ug": 230, "pantothenic_mg": 6, "vitamin_c_mg": 100,
            "salt_g": 6.5,
        },
        "15-17": {
            "energy_kcal": 2300, "protein_g": 55, "fat_percent": 25, "fiber_g": 17,
            "potassium_mg": 2000, "calcium_mg": 650, "magnesium_mg": 310, "phosphorus_mg": 900,
            "iron_mg": 10.5, "zinc_mg": 8, "copper_mg": 0.8,
            "vitamin_a_ug": 650, "vitamin_d_ug": 8.5, "vitamin_e_mg": 5.5, "vitamin_k_ug": 150,
            "vitamin_b1_mg": 1.2, "vitamin_b2_mg": 1.4, "niacin_mg": 13, "vitamin_b6_mg": 1.3,
            "vitamin_b12_ug": 2.4, "folate_ug": 240, "pantothenic_mg": 6, "vitamin_c_mg": 100,
            "salt_g": 6.5,
        },
        "18-29": {
            "energy_kcal": 2000, "protein_g": 50, "fat_percent": 25, "fiber_g": 18,
            "potassium_mg": 2000, "calcium_mg": 650, "magnesium_mg": 270, "phosphorus_mg": 800,
            "iron_mg": 10.5, "zinc_mg": 8, "copper_mg": 0.7,
            "vitamin_a_ug": 650, "vitamin_d_ug": 8.5, "vitamin_e_mg": 5.0, "vitamin_k_ug": 150,
            "vitamin_b1_mg": 1.1, "vitamin_b2_mg": 1.2, "niacin_mg": 11, "vitamin_b6_mg": 1.1,
            "vitamin_b12_ug": 2.4, "folate_ug": 240, "pantothenic_mg": 5, "vitamin_c_mg": 100,
            "salt_g": 6.5,
        },
        "30-49": {
            "energy_kcal": 2050, "protein_g": 50, "fat_percent": 25, "fiber_g": 18,
            "potassium_mg": 2000, "calcium_mg": 650, "magnesium_mg": 290, "phosphorus_mg": 800,
            "iron_mg": 10.5, "zinc_mg": 8, "copper_mg": 0.7,
            "vitamin_a_ug": 700, "vitamin_d_ug": 8.5, "vitamin_e_mg": 5.5, "vitamin_k_ug": 150,
            "vitamin_b1_mg": 1.1, "vitamin_b2_mg": 1.2, "niacin_mg": 12, "vitamin_b6_mg": 1.1,
            "vitamin_b12_ug": 2.4, "folate_ug": 240, "pantothenic_mg": 5, "vitamin_c_mg": 100,
            "salt_g": 6.5,
        },
        "50-64": {
            "energy_kcal": 1950, "protein_g": 50, "fat_percent": 25, "fiber_g": 18,
            "potassium_mg": 2000, "calcium_mg": 650, "magnesium_mg": 290, "phosphorus_mg": 800,
            "iron_mg": 6.5, "zinc_mg": 8, "copper_mg": 0.7,
            "vitamin_a_ug": 700, "vitamin_d_ug": 8.5, "vitamin_e_mg": 6.0, "vitamin_k_ug": 150,
            "vitamin_b1_mg": 1.0, "vitamin_b2_mg": 1.1, "niacin_mg": 11, "vitamin_b6_mg": 1.1,
            "vitamin_b12_ug": 2.4, "folate_ug": 240, "pantothenic_mg": 5, "vitamin_c_mg": 100,
            "salt_g": 6.5,
        },
        "65-74": {
            "energy_kcal": 1850, "protein_g": 50, "fat_percent": 25, "fiber_g": 17,
            "potassium_mg": 2000, "calcium_mg": 650, "magnesium_mg": 280, "phosphorus_mg": 800,
            "iron_mg": 6.0, "zinc_mg": 8, "copper_mg": 0.7,
            "vitamin_a_ug": 700, "vitamin_d_ug": 8.5, "vitamin_e_mg": 6.5, "vitamin_k_ug": 150,
            "vitamin_b1_mg": 0.9, "vitamin_b2_mg": 1.1, "niacin_mg": 10, "vitamin_b6_mg": 1.1,
            "vitamin_b12_ug": 2.4, "folate_ug": 240, "pantothenic_mg": 5, "vitamin_c_mg": 100,
            "salt_g": 6.5,
        },
        "75+": {
            "energy_kcal": 1650, "protein_g": 50, "fat_percent": 25, "fiber_g": 17,
            "potassium_mg": 2000, "calcium_mg": 650, "magnesium_mg": 260, "phosphorus_mg": 800,
            "iron_mg": 6.0, "zinc_mg": 8, "copper_mg": 0.7,
            "vitamin_a_ug": 650, "vitamin_d_ug": 8.5, "vitamin_e_mg": 6.5, "vitamin_k_ug": 150,
            "vitamin_b1_mg": 0.8, "vitamin_b2_mg": 1.0, "niacin_mg": 9, "vitamin_b6_mg": 1.1,
            "vitamin_b12_ug": 2.4, "folate_ug": 240, "pantothenic_mg": 5, "vitamin_c_mg": 100,
            "salt_g": 6.5,
        },
    },
}

# 耐容上限量（過剰摂取防止）
UPPER_LIMITS = {
    "male": {
        "1-2": {"vitamin_a_ug": 600, "vitamin_d_ug": 20, "vitamin_e_mg": 150, "iron_mg": 25, "zinc_mg": 7, "calcium_mg": 2500},
        "3-5": {"vitamin_a_ug": 700, "vitamin_d_ug": 30, "vitamin_e_mg": 200, "iron_mg": 25, "zinc_mg": 8, "calcium_mg": 2500},
        "6-7": {"vitamin_a_ug": 950, "vitamin_d_ug": 30, "vitamin_e_mg": 300, "iron_mg": 30, "zinc_mg": 10, "calcium_mg": 2500},
        "8-9": {"vitamin_a_ug": 1200, "vitamin_d_ug": 40, "vitamin_e_mg": 350, "iron_mg": 35, "zinc_mg": 12, "calcium_mg": 2500},
        "10-11": {"vitamin_a_ug": 1500, "vitamin_d_ug": 60, "vitamin_e_mg": 450, "iron_mg": 35, "zinc_mg": 15, "calcium_mg": 2500},
        "12-14": {"vitamin_a_ug": 2100, "vitamin_d_ug": 80, "vitamin_e_mg": 650, "iron_mg": 40, "zinc_mg": 23, "calcium_mg": 2500},
        "15-17": {"vitamin_a_ug": 2600, "vitamin_d_ug": 90, "vitamin_e_mg": 750, "iron_mg": 45, "zinc_mg": 35, "calcium_mg": 2500},
        "18-29": {"vitamin_a_ug": 2700, "vitamin_d_ug": 100, "vitamin_e_mg": 850, "iron_mg": 50, "zinc_mg": 40, "calcium_mg": 2500},
        "30-49": {"vitamin_a_ug": 2700, "vitamin_d_ug": 100, "vitamin_e_mg": 900, "iron_mg": 50, "zinc_mg": 45, "calcium_mg": 2500},
        "50-64": {"vitamin_a_ug": 2700, "vitamin_d_ug": 100, "vitamin_e_mg": 850, "iron_mg": 50, "zinc_mg": 45, "calcium_mg": 2500},
        "65-74": {"vitamin_a_ug": 2700, "vitamin_d_ug": 100, "vitamin_e_mg": 850, "iron_mg": 50, "zinc_mg": 40, "calcium_mg": 2500},
        "75+": {"vitamin_a_ug": 2700, "vitamin_d_ug": 100, "vitamin_e_mg": 750, "iron_mg": 50, "zinc_mg": 40, "calcium_mg": 2500},
    },
    "female": {
        "1-2": {"vitamin_a_ug": 600, "vitamin_d_ug": 20, "vitamin_e_mg": 150, "iron_mg": 25, "zinc_mg": 7, "calcium_mg": 2500},
        "3-5": {"vitamin_a_ug": 700, "vitamin_d_ug": 30, "vitamin_e_mg": 200, "iron_mg": 25, "zinc_mg": 8, "calcium_mg": 2500},
        "6-7": {"vitamin_a_ug": 950, "vitamin_d_ug": 30, "vitamin_e_mg": 300, "iron_mg": 30, "zinc_mg": 10, "calcium_mg": 2500},
        "8-9": {"vitamin_a_ug": 1200, "vitamin_d_ug": 40, "vitamin_e_mg": 350, "iron_mg": 35, "zinc_mg": 12, "calcium_mg": 2500},
        "10-11": {"vitamin_a_ug": 1500, "vitamin_d_ug": 60, "vitamin_e_mg": 450, "iron_mg": 35, "zinc_mg": 15, "calcium_mg": 2500},
        "12-14": {"vitamin_a_ug": 2100, "vitamin_d_ug": 80, "vitamin_e_mg": 600, "iron_mg": 40, "zinc_mg": 20, "calcium_mg": 2500},
        "15-17": {"vitamin_a_ug": 2600, "vitamin_d_ug": 90, "vitamin_e_mg": 650, "iron_mg": 40, "zinc_mg": 30, "calcium_mg": 2500},
        "18-29": {"vitamin_a_ug": 2700, "vitamin_d_ug": 100, "vitamin_e_mg": 650, "iron_mg": 40, "zinc_mg": 35, "calcium_mg": 2500},
        "30-49": {"vitamin_a_ug": 2700, "vitamin_d_ug": 100, "vitamin_e_mg": 700, "iron_mg": 40, "zinc_mg": 35, "calcium_mg": 2500},
        "50-64": {"vitamin_a_ug": 2700, "vitamin_d_ug": 100, "vitamin_e_mg": 700, "iron_mg": 40, "zinc_mg": 35, "calcium_mg": 2500},
        "65-74": {"vitamin_a_ug": 2700, "vitamin_d_ug": 100, "vitamin_e_mg": 650, "iron_mg": 40, "zinc_mg": 35, "calcium_mg": 2500},
        "75+": {"vitamin_a_ug": 2700, "vitamin_d_ug": 100, "vitamin_e_mg": 650, "iron_mg": 40, "zinc_mg": 35, "calcium_mg": 2500},
    },
}

# 学校給食基準（文部科学省）
SCHOOL_LUNCH_STANDARDS = {
    # 小学校低学年（6-7歳）
    "elementary_low": {
        "energy_kcal": 530, "protein_g": 530 * 0.15 / 4,  # 15%
        "fat_percent": 25, "calcium_mg": 290, "iron_mg": 2.0,
        "vitamin_a_ug": 160, "vitamin_b1_mg": 0.3, "vitamin_b2_mg": 0.4,
        "vitamin_c_mg": 20, "fiber_g": 4.0, "magnesium_mg": 40, "zinc_mg": 2.0,
    },
    # 小学校中学年（8-9歳）
    "elementary_mid": {
        "energy_kcal": 650, "protein_g": 650 * 0.15 / 4,
        "fat_percent": 25, "calcium_mg": 350, "iron_mg": 3.0,
        "vitamin_a_ug": 200, "vitamin_b1_mg": 0.4, "vitamin_b2_mg": 0.4,
        "vitamin_c_mg": 25, "fiber_g": 5.0, "magnesium_mg": 50, "zinc_mg": 2.0,
    },
    # 小学校高学年（10-11歳）
    "elementary_high": {
        "energy_kcal": 780, "protein_g": 780 * 0.15 / 4,
        "fat_percent": 25, "calcium_mg": 360, "iron_mg": 4.0,
        "vitamin_a_ug": 240, "vitamin_b1_mg": 0.5, "vitamin_b2_mg": 0.5,
        "vitamin_c_mg": 30, "fiber_g": 5.5, "magnesium_mg": 70, "zinc_mg": 2.0,
    },
    # 中学校（12-14歳）
    "junior_high": {
        "energy_kcal": 830, "protein_g": 830 * 0.15 / 4,
        "fat_percent": 25, "calcium_mg": 450, "iron_mg": 4.5,
        "vitamin_a_ug": 300, "vitamin_b1_mg": 0.5, "vitamin_b2_mg": 0.6,
        "vitamin_c_mg": 35, "fiber_g": 7.0, "magnesium_mg": 120, "zinc_mg": 3.0,
    },
}


def get_age_group_id(age: int) -> str:
    """年齢から年齢グループIDを取得"""
    for group in AGE_GROUPS:
        if "months" in group:
            continue  # 月齢は別扱い
        if group["min_age"] <= age <= group["max_age"]:
            return group["id"]
    # 範囲外の場合
    if age < 1:
        return "1-2"
    return "75+"


def get_requirements(age: int, gender: str = "male") -> dict:
    """年齢と性別に基づいて栄養基準を取得"""
    gender_key = "female" if gender.lower() in ["female", "f", "女", "女性"] else "male"
    age_group_id = get_age_group_id(age)

    base_req = DIETARY_REFERENCE_INTAKES[gender_key].get(
        age_group_id,
        DIETARY_REFERENCE_INTAKES[gender_key]["18-29"]
    )

    # Noneを除外して返す
    return {k: v for k, v in base_req.items() if v is not None}


def get_upper_limits(age: int, gender: str = "male") -> dict:
    """年齢と性別に基づいて耐容上限量を取得"""
    gender_key = "female" if gender.lower() in ["female", "f", "女", "女性"] else "male"
    age_group_id = get_age_group_id(age)

    return UPPER_LIMITS[gender_key].get(
        age_group_id,
        UPPER_LIMITS[gender_key]["18-29"]
    )


def get_school_lunch_requirements(age: int) -> dict:
    """年齢に基づいて給食基準を取得"""
    if age <= 7:
        return SCHOOL_LUNCH_STANDARDS["elementary_low"]
    elif age <= 9:
        return SCHOOL_LUNCH_STANDARDS["elementary_mid"]
    elif age <= 11:
        return SCHOOL_LUNCH_STANDARDS["elementary_high"]
    else:
        return SCHOOL_LUNCH_STANDARDS["junior_high"]


def export_to_json():
    """データをJSONファイルにエクスポート"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    data = {
        "age_groups": AGE_GROUPS,
        "nutrient_keys": NUTRIENT_KEYS,
        "dietary_reference_intakes": DIETARY_REFERENCE_INTAKES,
        "upper_limits": UPPER_LIMITS,
        "school_lunch_standards": SCHOOL_LUNCH_STANDARDS,
        "source": "厚生労働省「日本人の食事摂取基準（2020年版）」",
        "source_url": "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/kenkou/eiyou/syokuji_kijyun.html",
    }

    output_path = DATA_DIR / "dietary_standards.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Exported dietary standards to {output_path}")
    return output_path


def main():
    """データをエクスポート"""
    export_to_json()

    # サンプル出力
    print("\n=== Sample Requirements ===")
    for age in [5, 10, 15, 25, 45, 70]:
        for gender in ["male", "female"]:
            req = get_requirements(age, gender)
            print(f"\n{age}歳 {gender}:")
            print(f"  エネルギー: {req['energy_kcal']}kcal")
            print(f"  たんぱく質: {req['protein_g']}g")
            print(f"  カルシウム: {req['calcium_mg']}mg")


if __name__ == "__main__":
    main()
