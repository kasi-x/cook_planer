"""食料品価格の推移データ

総務省統計局「消費者物価指数」に基づく食料品価格の推移
https://www.stat.go.jp/data/cpi/

年次データ: 2010年〜2026年
季節データ: 4月15日、7月15日、10月15日、1月15日
"""

# 食料品物価指数（2020年=100として）
# 参考: 総務省統計局 消費者物価指数
FOOD_PRICE_INDEX = {
    2010: 96.5,
    2011: 96.2,
    2012: 96.0,
    2013: 95.8,
    2014: 98.5,   # 消費税増税
    2015: 97.2,
    2016: 99.0,
    2017: 99.8,
    2018: 101.2,
    2019: 101.8,  # 消費税増税
    2020: 100.0,  # 基準年（コロナ影響）
    2021: 100.8,
    2022: 104.5,  # 円安・物価上昇開始
    2023: 112.3,  # 物価高騰
    2024: 118.5,
    2025: 122.0,  # 推定
    2026: 125.0,  # 推定（現在）
}

# 季節別価格変動係数（基準=1.0）
# 4月15日=Q1, 7月15日=Q2, 10月15日=Q3, 1月15日=Q4
SEASONAL_FACTORS = {
    "野菜": {
        "Q1_Apr": 1.08,  # 春野菜端境期、やや高め
        "Q2_Jul": 0.92,  # 夏野菜豊作期
        "Q3_Oct": 0.95,  # 秋野菜
        "Q4_Jan": 1.12,  # 冬、高騰
    },
    "果物": {
        "Q1_Apr": 1.05,
        "Q2_Jul": 0.90,  # 夏果物豊富
        "Q3_Oct": 0.95,
        "Q4_Jan": 1.15,  # 冬果物少ない
    },
    "魚介類": {
        "Q1_Apr": 1.02,
        "Q2_Jul": 1.00,
        "Q3_Oct": 0.95,  # 秋の旬
        "Q4_Jan": 1.08,  # 年末需要
    },
    "肉類": {
        "Q1_Apr": 1.00,
        "Q2_Jul": 1.02,  # BBQ需要
        "Q3_Oct": 0.98,
        "Q4_Jan": 1.05,  # 年末需要
    },
    "穀類": {
        "Q1_Apr": 1.00,
        "Q2_Jul": 1.00,
        "Q3_Oct": 0.98,  # 新米
        "Q4_Jan": 1.02,
    },
    "乳卵類": {
        "Q1_Apr": 0.98,
        "Q2_Jul": 1.02,  # 夏は卵やや高め
        "Q3_Oct": 1.00,
        "Q4_Jan": 1.05,  # 冬は卵高騰
    },
    "調味料": {
        "Q1_Apr": 1.00,
        "Q2_Jul": 1.00,
        "Q3_Oct": 1.00,
        "Q4_Jan": 1.00,
    },
}

# カテゴリ別物価上昇率（年次）
# 2010年=1.0としたときの各年の比率
CATEGORY_YEARLY_INDEX = {
    "穀類": {
        2010: 1.00, 2011: 1.02, 2012: 1.01, 2013: 1.00, 2014: 1.05,
        2015: 1.08, 2016: 1.10, 2017: 1.12, 2018: 1.15, 2019: 1.18,
        2020: 1.20, 2021: 1.22, 2022: 1.28, 2023: 1.38, 2024: 1.42,
        2025: 1.45, 2026: 1.48,
    },
    "魚介類": {
        2010: 1.00, 2011: 1.01, 2012: 1.02, 2013: 1.03, 2014: 1.06,
        2015: 1.05, 2016: 1.06, 2017: 1.08, 2018: 1.10, 2019: 1.12,
        2020: 1.10, 2021: 1.12, 2022: 1.18, 2023: 1.25, 2024: 1.30,
        2025: 1.33, 2026: 1.35,
    },
    "肉類": {
        2010: 1.00, 2011: 0.99, 2012: 1.01, 2013: 1.02, 2014: 1.08,
        2015: 1.10, 2016: 1.12, 2017: 1.15, 2018: 1.20, 2019: 1.25,
        2020: 1.28, 2021: 1.30, 2022: 1.38, 2023: 1.48, 2024: 1.52,
        2025: 1.55, 2026: 1.58,
    },
    "乳卵類": {
        2010: 1.00, 2011: 1.01, 2012: 1.02, 2013: 1.02, 2014: 1.05,
        2015: 1.06, 2016: 1.08, 2017: 1.10, 2018: 1.12, 2019: 1.15,
        2020: 1.18, 2021: 1.20, 2022: 1.28, 2023: 1.42, 2024: 1.48,
        2025: 1.50, 2026: 1.52,
    },
    "野菜": {
        2010: 1.00, 2011: 1.02, 2012: 0.98, 2013: 1.05, 2014: 1.08,
        2015: 1.05, 2016: 1.10, 2017: 1.08, 2018: 1.12, 2019: 1.10,
        2020: 1.08, 2021: 1.12, 2022: 1.18, 2023: 1.28, 2024: 1.32,
        2025: 1.35, 2026: 1.38,
    },
    "果物": {
        2010: 1.00, 2011: 1.01, 2012: 1.02, 2013: 1.03, 2014: 1.06,
        2015: 1.08, 2016: 1.10, 2017: 1.12, 2018: 1.15, 2019: 1.18,
        2020: 1.20, 2021: 1.22, 2022: 1.28, 2023: 1.35, 2024: 1.40,
        2025: 1.42, 2026: 1.45,
    },
    "調味料": {
        2010: 1.00, 2011: 1.00, 2012: 1.01, 2013: 1.01, 2014: 1.03,
        2015: 1.05, 2016: 1.06, 2017: 1.08, 2018: 1.10, 2019: 1.12,
        2020: 1.15, 2021: 1.18, 2022: 1.22, 2023: 1.28, 2024: 1.30,
        2025: 1.32, 2026: 1.35,
    },
}

# カテゴリ別物価上昇率（2015年比、2026年）- 互換性のため維持
CATEGORY_PRICE_CHANGE = {
    "穀類": 1.37,      # 米・パンなど
    "魚介類": 1.28,    # 魚・貝類
    "肉類": 1.44,      # 牛・豚・鶏肉
    "乳卵類": 1.43,    # 牛乳・卵
    "野菜": 1.31,      # 野菜・海藻
    "果物": 1.34,
    "調味料": 1.29,
}

# 給食費の推移（月額平均、円）
# 参考: 文部科学省「学校給食実施状況調査」
SCHOOL_LUNCH_COST_HISTORY = {
    "elementary": {  # 小学校
        2010: 4100,
        2012: 4180,
        2014: 4266,
        2015: 4301,
        2016: 4323,
        2018: 4343,
        2020: 4440,
        2021: 4477,
        2022: 4580,
        2023: 4680,
        2024: 4800,
        2025: 4950,
        2026: 5100,
    },
    "junior_high": {  # 中学校
        2010: 4700,
        2012: 4780,
        2014: 4882,
        2015: 4921,
        2016: 4940,
        2018: 4941,
        2020: 5090,
        2021: 5121,
        2022: 5250,
        2023: 5380,
        2024: 5500,
        2025: 5650,
        2026: 5800,
    },
}

# 1食あたりの食材原価（円）推定
# 給食費の約40-50%が食材費
LUNCH_MATERIAL_COST = {
    "elementary": {
        2010: 165,
        2012: 170,
        2014: 175,
        2015: 180,
        2016: 182,
        2018: 185,
        2020: 190,
        2021: 195,
        2022: 205,
        2023: 210,
        2024: 215,
        2025: 222,
        2026: 230,
    },
    "junior_high": {
        2010: 195,
        2012: 200,
        2014: 205,
        2015: 210,
        2016: 212,
        2018: 215,
        2020: 222,
        2021: 230,
        2022: 240,
        2023: 245,
        2024: 250,
        2025: 258,
        2026: 265,
    },
}

# 主要食材の価格推移（100gあたり円）
# 2010年から2026年の推定価格
FOOD_PRICE_HISTORY = {
    "鶏卵": {
        2010: 18, 2012: 19, 2014: 22, 2015: 20, 2016: 18,
        2018: 19, 2020: 21, 2021: 22, 2022: 28, 2023: 35,
        2024: 32, 2025: 30, 2026: 28,
    },
    "鶏もも肉": {
        2010: 95, 2012: 98, 2014: 105, 2015: 108, 2016: 110,
        2018: 115, 2020: 120, 2021: 125, 2022: 135, 2023: 145,
        2024: 150, 2025: 155, 2026: 158,
    },
    "豚もも肉": {
        2010: 140, 2012: 145, 2014: 155, 2015: 160, 2016: 162,
        2018: 168, 2020: 175, 2021: 180, 2022: 195, 2023: 210,
        2024: 220, 2025: 225, 2026: 230,
    },
    "牛乳": {
        2010: 18, 2012: 19, 2014: 20, 2015: 21, 2016: 21,
        2018: 22, 2020: 23, 2021: 24, 2022: 26, 2023: 28,
        2024: 29, 2025: 30, 2026: 31,
    },
    "キャベツ": {
        2010: 5, 2012: 6, 2014: 7, 2015: 6, 2016: 8,
        2018: 6, 2020: 5, 2021: 7, 2022: 8, 2023: 9,
        2024: 7, 2025: 6, 2026: 6,
    },
    "たまねぎ": {
        2010: 8, 2012: 10, 2014: 12, 2015: 10, 2016: 15,
        2018: 12, 2020: 10, 2021: 18, 2022: 25, 2023: 20,
        2024: 18, 2025: 17, 2026: 17,
    },
    "じゃがいも": {
        2010: 12, 2012: 14, 2014: 16, 2015: 15, 2016: 18,
        2018: 16, 2020: 15, 2021: 17, 2022: 20, 2023: 22,
        2024: 20, 2025: 19, 2026: 19,
    },
    "米": {
        2010: 35, 2012: 36, 2014: 38, 2015: 37, 2016: 36,
        2018: 38, 2020: 40, 2021: 42, 2022: 45, 2023: 52,
        2024: 80, 2025: 75, 2026: 70,  # 2024年米不足
    },
    "豆腐": {
        2010: 25, 2012: 26, 2014: 28, 2015: 28, 2016: 29,
        2018: 30, 2020: 32, 2021: 33, 2022: 36, 2023: 40,
        2024: 42, 2025: 43, 2026: 45,
    },
    "さば": {
        2010: 50, 2012: 55, 2014: 60, 2015: 58, 2016: 62,
        2018: 65, 2020: 68, 2021: 72, 2022: 78, 2023: 85,
        2024: 82, 2025: 80, 2026: 80,
    },
}

# 季節別食材価格（代表的な野菜の月別変動）- 2026年基準
SEASONAL_FOOD_PRICES = {
    "キャベツ": {
        "Q1_Apr": 8,   # 春キャベツ端境期
        "Q2_Jul": 5,   # 夏、安い
        "Q3_Oct": 6,   # 秋
        "Q4_Jan": 10,  # 冬、高い
    },
    "たまねぎ": {
        "Q1_Apr": 20,  # 新たまねぎ
        "Q2_Jul": 15,  #
        "Q3_Oct": 12,  # 北海道産
        "Q4_Jan": 18,  # 貯蔵品
    },
    "ほうれん草": {
        "Q1_Apr": 35,  # 端境期
        "Q2_Jul": 45,  # 夏は高い
        "Q3_Oct": 30,  #
        "Q4_Jan": 25,  # 冬が旬
    },
    "トマト": {
        "Q1_Apr": 40,
        "Q2_Jul": 25,  # 夏が旬
        "Q3_Oct": 35,
        "Q4_Jan": 50,  # 冬は高い
    },
    "きゅうり": {
        "Q1_Apr": 40,
        "Q2_Jul": 25,  # 夏が旬
        "Q3_Oct": 35,
        "Q4_Jan": 55,  # 冬は高い
    },
}


def get_seasonal_food_prices_by_year(year: int) -> dict:
    """指定年の季節別食材価格を取得（2026年価格を基準に物価指数で調整）"""
    ratio = get_price_ratio(year)

    result = {}
    for food, prices in SEASONAL_FOOD_PRICES.items():
        result[food] = {
            quarter: round(price * ratio)
            for quarter, price in prices.items()
        }

    return result


def get_all_years_seasonal_prices() -> dict:
    """全年度の季節別食材価格を取得"""
    years = [2010, 2012, 2014, 2016, 2018, 2020, 2022, 2024, 2026]

    result = {}
    for year in years:
        result[year] = get_seasonal_food_prices_by_year(year)

    return result


def get_price_ratio(year: int, base_year: int = 2026) -> float:
    """指定年の価格比率を取得（基準年=1.0）"""
    base_index = FOOD_PRICE_INDEX.get(base_year, 125.0)
    year_index = FOOD_PRICE_INDEX.get(year, base_index)
    return year_index / base_index


def estimate_historical_price(current_price: float, year: int) -> float:
    """現在価格から過去の価格を推定"""
    ratio = get_price_ratio(year)
    return current_price * ratio


def get_seasonal_price(base_price: float, category: str, quarter: str) -> float:
    """季節調整した価格を取得"""
    if category in SEASONAL_FACTORS and quarter in SEASONAL_FACTORS[category]:
        factor = SEASONAL_FACTORS[category][quarter]
        return base_price * factor
    return base_price


def get_quarterly_prices(year: int, category: str = "野菜") -> dict:
    """指定年の四半期別価格指数を取得"""
    base_index = CATEGORY_YEARLY_INDEX.get(category, {}).get(year, 1.0)
    quarters = ["Q1_Apr", "Q2_Jul", "Q3_Oct", "Q4_Jan"]

    result = {}
    for q in quarters:
        seasonal = SEASONAL_FACTORS.get(category, {}).get(q, 1.0)
        result[q] = round(base_index * seasonal, 3)

    return result


def get_food_price_timeline(food_name: str) -> list:
    """食材の価格推移データを取得"""
    if food_name not in FOOD_PRICE_HISTORY:
        return []

    prices = FOOD_PRICE_HISTORY[food_name]
    return [{"year": year, "price": price} for year, price in sorted(prices.items())]


def get_all_years_comparison() -> list:
    """全年度の比較データを取得"""
    years = sorted(FOOD_PRICE_INDEX.keys())
    base_year = 2010
    base_index = FOOD_PRICE_INDEX[base_year]

    result = []
    for year in years:
        index = FOOD_PRICE_INDEX[year]
        result.append({
            "year": year,
            "index": index,
            "change_from_2010": round((index / base_index - 1) * 100, 1),
            "change_from_prev": round((index / FOOD_PRICE_INDEX.get(year - 1, index) - 1) * 100, 1) if year > 2010 else 0,
        })

    return result


def get_lunch_cost_comparison():
    """給食費の年度比較データを取得（全年度）"""
    result = {
        "elementary": [],
        "junior_high": [],
    }

    for school_type in ["elementary", "junior_high"]:
        costs = SCHOOL_LUNCH_COST_HISTORY[school_type]
        material = LUNCH_MATERIAL_COST[school_type]

        for year in sorted(costs.keys()):
            monthly = costs[year]
            per_meal = material.get(year, 0)
            daily = monthly / 22 if monthly > 0 else 0

            result[school_type].append({
                "year": year,
                "monthly_fee": monthly,
                "daily_cost": round(daily, 0),
                "material_cost_per_meal": per_meal,
            })

    return result


def get_price_change_summary():
    """価格変動サマリーを取得"""
    current = FOOD_PRICE_INDEX.get(2026, 125.0)
    five_years_ago = FOOD_PRICE_INDEX.get(2021, 100.8)
    ten_years_ago = FOOD_PRICE_INDEX.get(2016, 99.0)
    fifteen_years_ago = FOOD_PRICE_INDEX.get(2011, 96.2)

    return {
        "current_year": 2026,
        "five_years_ago": {
            "year": 2021,
            "price_ratio": round(current / five_years_ago, 3),
            "change_percent": round((current / five_years_ago - 1) * 100, 1),
        },
        "ten_years_ago": {
            "year": 2016,
            "price_ratio": round(current / ten_years_ago, 3),
            "change_percent": round((current / ten_years_ago - 1) * 100, 1),
        },
        "fifteen_years_ago": {
            "year": 2011,
            "price_ratio": round(current / fifteen_years_ago, 3),
            "change_percent": round((current / fifteen_years_ago - 1) * 100, 1),
        },
        "category_changes": CATEGORY_PRICE_CHANGE,
    }


def get_seasonal_comparison(year: int = 2026) -> dict:
    """四半期別価格比較データを取得"""
    result = {}

    for category in SEASONAL_FACTORS.keys():
        yearly_index = CATEGORY_YEARLY_INDEX.get(category, {}).get(year, 1.0)
        quarters = {}

        for quarter, factor in SEASONAL_FACTORS[category].items():
            quarters[quarter] = {
                "factor": factor,
                "index": round(yearly_index * factor, 3),
                "label": {
                    "Q1_Apr": "4月15日",
                    "Q2_Jul": "7月15日",
                    "Q3_Oct": "10月15日",
                    "Q4_Jan": "1月15日",
                }[quarter]
            }

        result[category] = {
            "yearly_index": yearly_index,
            "quarters": quarters,
        }

    return result


def get_category_yearly_trends() -> dict:
    """カテゴリ別年次トレンドデータを取得"""
    result = {}

    for category, yearly_data in CATEGORY_YEARLY_INDEX.items():
        trend = []
        for year, index in sorted(yearly_data.items()):
            trend.append({
                "year": year,
                "index": index,
                "change_from_2010": round((index - 1.0) * 100, 1),
            })
        result[category] = trend

    return result


if __name__ == "__main__":
    print("=== 食料品価格の推移 ===")
    summary = get_price_change_summary()
    print(f"5年前比: +{summary['five_years_ago']['change_percent']}%")
    print(f"10年前比: +{summary['ten_years_ago']['change_percent']}%")
    print(f"15年前比: +{summary['fifteen_years_ago']['change_percent']}%")

    print("\n=== 年度別物価指数 ===")
    for data in get_all_years_comparison():
        print(f"  {data['year']}年: 指数{data['index']} (2010年比 +{data['change_from_2010']}%)")

    print("\n=== カテゴリ別上昇率（15年間）===")
    for cat, ratio in CATEGORY_PRICE_CHANGE.items():
        print(f"  {cat}: +{(ratio-1)*100:.0f}%")

    print("\n=== 季節別価格変動（2026年・野菜）===")
    seasonal = get_seasonal_comparison(2026)
    for q, data in seasonal["野菜"]["quarters"].items():
        print(f"  {data['label']}: 係数{data['factor']} (指数{data['index']})")

    print("\n=== 給食費の推移 ===")
    lunch = get_lunch_cost_comparison()
    print("小学校（月額）:")
    for data in lunch["elementary"]:
        print(f"  {data['year']}年: ¥{data['monthly_fee']} (1食材料費: ¥{data['material_cost_per_meal']})")
