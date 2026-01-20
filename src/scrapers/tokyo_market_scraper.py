"""東京都中央卸売市場 野菜市況スクレイパー

Source: https://www.shijou.metro.tokyo.lg.jp/torihiki/week/yasai
週次の野菜価格情報（PDF）を取得する
"""

import re
import requests
import pdfplumber
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
OUTPUT_DIR = DATA_DIR / "processed"

BASE_URL = "https://www.shijou.metro.tokyo.lg.jp"


def download_pdf(url: str, output_path: Path) -> Path:
    """PDFファイルをダウンロード"""
    response = requests.get(url, allow_redirects=True)
    response.raise_for_status()
    output_path.write_bytes(response.content)
    return output_path


def parse_price(value: str) -> float | None:
    """価格文字列を数値に変換"""
    if not value or value.strip() == '':
        return None
    # カンマ除去
    s = value.replace(',', '').strip()
    try:
        return float(s)
    except ValueError:
        return None


def parse_vegetable_prices(pdf_path: Path) -> pd.DataFrame:
    """PDFから野菜価格を抽出

    価格は単位（Kg）あたりの円で記載されている。
    100gあたりに変換する。
    """
    records = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if not tables:
                continue

            table = tables[0]
            current_product = None

            for row in table[2:]:  # Skip header rows
                # Column 0: Product name (only set for first row of product)
                if row[0] and row[0].strip():
                    current_product = row[0].strip().replace(' ', '')

                if not current_product:
                    continue

                # Column 4: Transaction type (せり=auction, 相対=negotiated)
                transaction = row[4] if len(row) > 4 else ''
                if not transaction:
                    continue

                # Column 7: Unit (Kg)
                unit_kg = parse_price(row[7]) if len(row) > 7 else None
                if not unit_kg:
                    continue

                # Column 8: High price, 9: Mid price, 10: Low price
                high_price = parse_price(row[8]) if len(row) > 8 else None
                mid_price = parse_price(row[9]) if len(row) > 9 else None
                low_price = parse_price(row[10]) if len(row) > 10 else None

                # Use mid price, or average of high and low if mid not available
                if mid_price is not None:
                    price_per_unit = mid_price
                elif high_price is not None and low_price is not None:
                    price_per_unit = (high_price + low_price) / 2
                elif high_price is not None:
                    price_per_unit = high_price
                elif low_price is not None:
                    price_per_unit = low_price
                else:
                    continue

                # Convert to price per 100g
                # unit_kg is the unit weight in kg, price is per that unit
                price_per_100g = price_per_unit / (unit_kg * 10)

                records.append({
                    "food_name": current_product,
                    "price_per_100g": round(price_per_100g, 2),
                    "unit": "円/100g",
                    "transaction_type": transaction,
                    "source": "東京都中央卸売市場",
                    "date": "2025-06-01",
                })

    # Group by product and take average price
    if records:
        df = pd.DataFrame(records)
        # Average across transaction types
        df = df.groupby('food_name').agg({
            'price_per_100g': 'mean',
            'unit': 'first',
            'source': 'first',
            'date': 'first',
        }).reset_index()
        df['price_per_100g'] = df['price_per_100g'].round(2)
        return df

    return pd.DataFrame()


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Download June 2025 Week 1 PDF
    pdf_url = f"{BASE_URL}/documents/d/shijou/week_yasai_y2025061-pdf"
    pdf_path = RAW_DIR / "tokyo_market_202506_w1.pdf"

    print(f"Downloading PDF from {pdf_url}")
    download_pdf(pdf_url, pdf_path)

    print("Parsing vegetable prices...")
    df = parse_vegetable_prices(pdf_path)

    output_path = OUTPUT_DIR / "tokyo_market_prices.csv"
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} items to {output_path}")


if __name__ == "__main__":
    main()
