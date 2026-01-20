"""HTML レポート生成

最適化結果をHTMLで可視化する
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / "data"
MERGED_DIR = DATA_DIR / "merged"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

# 食品1個あたりの重量（g）
UNIT_WEIGHTS = {
    "鶏卵（ＬＬ）": 70,
    "鶏卵（Ｌ）": 64,
    "鶏卵（Ｍ）": 58,
    "鶏卵（ＭＳ）": 52,
    "鶏卵（Ｓ）": 46,
    "鶏卵（ＳＳ）": 40,
    "鶏卵（特高）": 76,
    "キャベツ": 1000,
    "はくさい": 2000,
    "レタス": 300,
    "だいこん": 1000,
    "にんじん": 150,
    "たまねぎ": 200,
    "じゃがいも": 150,
    "かぼちゃ": 1500,
    "トマト": 150,
    "ミニトマト": 15,
    "きゅうり": 100,
    "なす": 80,
    "ピーマン": 35,
    "ブロッコリー": 300,
    "ほうれんそう": 200,  # 1束
    "こまつな": 250,  # 1束
    "ねぎ": 100,  # 1本
    "とうもろこし": 350,  # 1本（可食部）
    "えだまめ": 100,  # 1袋
    "いんげん": 100,  # 1袋
    "そらまめ": 100,  # さや付き
    "かぶ": 100,  # 1個
}


def load_data():
    """データを読み込み"""
    merged = pd.read_csv(MERGED_DIR / "food_price_nutrition.csv")
    return merged


def generate_html(foods: pd.DataFrame, amounts: dict, totals: dict, requirements: dict) -> str:
    """HTMLレポートを生成"""
    from optimize import NUTRIENT_NAMES

    # 食材テーブル行を生成
    food_rows = ""
    for food_name, amount in sorted(amounts.items(), key=lambda x: x[1], reverse=True):
        row = foods[foods['food_name'] == food_name].iloc[0]
        cost = row['price_per_100g'] * amount / 100
        # 個数を計算
        unit_weight = UNIT_WEIGHTS.get(food_name)
        if unit_weight:
            count = amount / unit_weight
            count_str = f"（約{count:.1f}個）"
        else:
            count_str = ""
        food_rows += f"""
        <tr>
            <td>{food_name}</td>
            <td class="num">{amount:.0f}g <span class="count">{count_str}</span></td>
            <td class="num">¥{cost:.0f}</td>
        </tr>"""

    # 栄養素達成テーブル
    nutrient_rows = ""
    for nutrient, req in requirements.items():
        actual = totals.get(nutrient, 0)
        ratio = actual / req * 100 if req > 0 else 0
        name = NUTRIENT_NAMES.get(nutrient, nutrient)
        unit = "kcal" if "kcal" in nutrient else ("μg" if "_ug" in nutrient else ("mg" if "_mg" in nutrient else "g"))
        status_class = "achieved" if ratio >= 100 else ("partial" if ratio >= 80 else "not-achieved")
        nutrient_rows += f"""
        <tr class="{status_class}">
            <td>{name}</td>
            <td class="num">{actual:.1f} {unit}</td>
            <td class="num">{req:.1f} {unit}</td>
            <td class="num">{ratio:.0f}%</td>
        </tr>"""

    # 全食材データテーブル
    all_foods_rows = ""
    for _, row in foods.sort_values('price_per_100g').iterrows():
        cost_eff = row['energy_kcal'] / row['price_per_100g'] if row['price_per_100g'] > 0 else 0
        all_foods_rows += f"""
        <tr>
            <td>{row['food_name']}</td>
            <td class="num">¥{row['price_per_100g']:.1f}</td>
            <td class="num">{row['energy_kcal']:.0f}</td>
            <td class="num">{row['protein_g']:.1f}</td>
            <td class="num">{row.get('calcium_mg', 0):.0f}</td>
            <td class="num">{row.get('vitamin_c_mg', 0):.0f}</td>
            <td class="num">{cost_eff:.2f}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>栄養価最適化レポート - 12-14歳（2025年基準）</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Hiragino Sans', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
        }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .target-info {{
            background: #e8f4fd;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 15px 0;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 12px;
        }}
        .summary-item {{
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            color: white;
        }}
        .summary-item.cost {{ background: linear-gradient(135deg, #f093fb, #f5576c); }}
        .summary-item.achieved {{ background: linear-gradient(135deg, #43e97b, #38f9d7); }}
        .summary-item.partial {{ background: linear-gradient(135deg, #f6d365, #fda085); }}
        .summary-item.not-achieved {{ background: linear-gradient(135deg, #ff6b6b, #ee5a5a); }}
        .summary-item .value {{ font-size: 1.8em; font-weight: bold; margin: 5px 0; }}
        .summary-item .label {{ font-size: 0.8em; opacity: 0.9; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ padding: 8px 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #3498db; color: white; position: sticky; top: 0; font-size: 0.9em; }}
        tr:hover {{ background: #f8f9fa; }}
        tr.achieved {{ background: #d4edda; }}
        tr.partial {{ background: #fff3cd; }}
        tr.not-achieved {{ background: #f8d7da; }}
        .num {{ text-align: right; font-family: 'Menlo', monospace; }}
        .count {{ color: #666; font-size: 0.85em; }}
        .highlight {{ background: #fff3cd !important; font-weight: bold; }}
        .footer {{ text-align: center; color: #7f8c8d; margin-top: 30px; padding: 15px; font-size: 0.85em; }}
        .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        @media (max-width: 768px) {{ .two-col {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <h1>🥗 栄養価最適化レポート</h1>
    <p>対象: <strong>12-14歳（男子・身体活動レベル普通）</strong> | 基準日: 2025年6月1日</p>
    <p>生成: {datetime.now().strftime('%Y-%m-%d %H:%M')} | 制約栄養素数: {len(requirements)}</p>

    <h2>📊 結果サマリー</h2>
    <div class="card">
        <div class="summary">
            <div class="summary-item cost">
                <div class="label">1日あたり</div>
                <div class="value">¥{totals['total_cost']:.0f}</div>
                <div class="label">約¥{totals['total_cost']*30:.0f}/月</div>
            </div>
            <div class="summary-item achieved">
                <div class="label">総重量</div>
                <div class="value">{sum(amounts.values()):.0f}g</div>
            </div>
            <div class="summary-item achieved">
                <div class="label">エネルギー</div>
                <div class="value">{totals.get('energy_kcal', 0):.0f}</div>
                <div class="label">kcal</div>
            </div>
            <div class="summary-item achieved">
                <div class="label">たんぱく質</div>
                <div class="value">{totals.get('protein_g', 0):.0f}g</div>
            </div>
        </div>
    </div>

    <div class="two-col">
        <div>
            <h2>🍳 選択された食材</h2>
            <div class="card">
                <table>
                    <thead><tr><th>食品名</th><th>量</th><th>コスト</th></tr></thead>
                    <tbody>
                        {food_rows}
                        <tr class="highlight">
                            <td><strong>合計</strong></td>
                            <td class="num"><strong>{sum(amounts.values()):.0f}g</strong></td>
                            <td class="num"><strong>¥{totals['total_cost']:.0f}</strong></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div>
            <h2>📋 栄養素達成状況</h2>
            <div class="card" style="max-height: 500px; overflow-y: auto;">
                <table>
                    <thead><tr><th>栄養素</th><th>摂取量</th><th>目標</th><th>達成率</th></tr></thead>
                    <tbody>{nutrient_rows}</tbody>
                </table>
            </div>
        </div>
    </div>

    <h2>📈 全食材データ一覧</h2>
    <div class="card" style="overflow-x: auto;">
        <table>
            <thead>
                <tr>
                    <th>食品名</th><th>価格/100g</th><th>kcal</th><th>たんぱく質</th>
                    <th>Ca(mg)</th><th>VitC(mg)</th><th>コスパ</th>
                </tr>
            </thead>
            <tbody>{all_foods_rows}</tbody>
        </table>
    </div>

    <div class="footer">
        <p>データソース: 鶏鳴新聞社、東京都中央卸売市場、文部科学省食品成分表八訂</p>
        <p>食事摂取基準: <a href="https://japanese-food.net/top-page/meals-intake-standard-table-2025/dietary-intake-standard12-14-2025">12-14歳の食事摂取基準（2025年版）</a></p>
    </div>
</body>
</html>"""
    return html


def run_optimization(foods: pd.DataFrame) -> tuple[dict, dict, dict]:
    """最適化を実行"""
    from optimize import optimize_diet, calculate_totals, DAILY_REQUIREMENTS
    amounts = optimize_diet(foods)
    totals = calculate_totals(foods, amounts)
    return amounts, totals, DAILY_REQUIREMENTS


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Loading data...")
    foods = load_data()
    print("Running optimization...")
    amounts, totals, requirements = run_optimization(foods)
    print("Generating HTML report...")
    html = generate_html(foods, amounts, totals, requirements)
    output_path = OUTPUT_DIR / "report.html"
    output_path.write_text(html, encoding='utf-8')
    print(f"Report saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    main()
