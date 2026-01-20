# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

栄養価と価格の最適化プロジェクト - 最も安く基準栄養価を取得するための食材価格・栄養価データベースを構築し、線形計画法などで最適な食材組み合わせを計算する。

## Data Sources

- **鶏卵相場**: https://keimei.ne.jp/ (PDF形式の相場表)
- **東京都中央卸売市場 野菜市況**: https://www.shijou.metro.tokyo.lg.jp/torihiki/week/yasai
- **文部科学省 食品成分データベース**: https://www.mext.go.jp/a_menu/syokuhinseibun/mext_00001.html

## Build and Run Commands

```bash
# Environment setup
pixi install

# Run individual scrapers
pixi run scrape-keimei    # 鶏卵相場PDF
pixi run scrape-tokyo     # 東京市場野菜
pixi run scrape-mext      # 食品成分DB

# Run all scrapers
pixi run scrape-all

# Merge CSVs into unified dataset
pixi run merge

# Run optimization calculation
pixi run optimize
```

## Architecture

```
cook_planer/
├── src/
│   ├── scrapers/          # サイト毎のスクレイパー
│   │   ├── keimei_scraper.py       # 鶏卵相場PDF解析
│   │   ├── tokyo_market_scraper.py # 東京市場野菜市況
│   │   └── mext_nutrition_scraper.py # 食品成分DB
│   ├── merge_data.py      # CSV結合処理
│   └── optimize.py        # 最適化計算（線形計画法）
├── data/
│   ├── raw/               # スクレイピング生データ
│   ├── processed/         # サイト毎のCSV
│   └── merged/            # 結合済みデータ
└── pixi.toml              # 環境定義
```

## Key Dependencies

- `requests`, `beautifulsoup4`: Webスクレイピング
- `pdfplumber`: PDF解析（鶏卵相場、東京市場）
- `openpyxl`: Excel解析（MEXT食品成分表）
- `pandas`: データ処理・CSV操作
- `scipy`: 線形計画法による最適化（`linprog`）
- `playwright`: JSレンダリングページ用（東京市場のリンク取得）

## Food Name Mapping

価格データと栄養データは食品名の形式が異なるため、`merge_data.py`内の`FOOD_NAME_MAPPING`で対応付けを行う。

例:
- `"キャベツ"` → `"（キャベツ類）　キャベツ　結球葉　生"`
- `"鶏卵（Ｍ）"` → `"鶏卵　全卵　生"`

栄養成分表の食品名は全角スペース(`\u3000`)を使用。

## Data Format

基準日: 2025年6月1日

各CSVは以下の形式で統一:
- `food_name`: 食品名
- `price_per_100g`: 100gあたり価格（円）
- `energy_kcal`: エネルギー（kcal/100g）
- `protein_g`: たんぱく質（g/100g）
- `fat_g`: 脂質（g/100g）
- `carbohydrate_g`: 炭水化物（g/100g）
- その他必要な栄養素
