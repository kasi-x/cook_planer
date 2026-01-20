"""鶏卵相場PDFスクレイパー

Source: https://keimei.ne.jp/
PDFファイルから鶏卵の価格情報を抽出する
"""

import pdfplumber
import pandas as pd
import requests
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
OUTPUT_DIR = DATA_DIR / "processed"


def download_pdf(url: str, output_path: Path) -> Path:
    """PDFファイルをダウンロード"""
    response = requests.get(url)
    response.raise_for_status()
    output_path.write_bytes(response.content)
    return output_path


def parse_egg_prices(pdf_path: Path, target_month: str = "6月") -> pd.DataFrame:
    """PDFから鶏卵価格を抽出

    Args:
        pdf_path: PDFファイルパス
        target_month: 取得対象月（例: "6月"）
    """
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        table = tables[0]

        # Row 2: ヘッダー ['月', 'ＬＬ', 'Ｌ', 'Ｍ', 'ＭＳ', 'Ｓ', 'ＳＳ', '特高']
        headers = table[2]
        size_names = headers[1:]  # サイズ名

        # Row 3: 月別データ（各セルに改行区切りで複数月のデータ）
        data_row = table[3]
        months = data_row[0].split('\n')

        # 対象月のインデックスを取得
        try:
            month_idx = months.index(target_month)
        except ValueError:
            print(f"Month {target_month} not found in data")
            return pd.DataFrame()

        # 各サイズの価格を抽出
        records = []
        for i, size in enumerate(size_names):
            if size is None:
                continue
            prices = data_row[i + 1].split('\n')
            price_per_kg = float(prices[month_idx])
            price_per_100g = price_per_kg / 10  # kg -> 100g

            records.append({
                "food_name": f"鶏卵（{size}）",
                "price_per_100g": round(price_per_100g, 2),
                "unit": "円/100g",
                "source": "鶏鳴新聞社",
                "date": "2025-06-01",
            })

    return pd.DataFrame(records)


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # TODO: 実際のPDF URLを設定
    pdf_url = "https://keimei.ne.jp/wp/wp-content/uploads/2026/01/44e1554f9c1aec190aa0fce86cfed451.pdf"
    pdf_path = RAW_DIR / "keimei_egg_prices.pdf"

    print(f"Downloading PDF from {pdf_url}")
    download_pdf(pdf_url, pdf_path)

    print("Parsing egg prices...")
    df = parse_egg_prices(pdf_path)

    output_path = OUTPUT_DIR / "keimei_prices.csv"
    df.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
