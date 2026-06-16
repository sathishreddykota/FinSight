# backend/ingestion/sec_scraper.py

import time
from pathlib import Path
from dotenv import load_dotenv
from sec_edgar_downloader import Downloader

load_dotenv()

COMPANIES = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Google": "GOOGL",
    "Meta": "META",
    "Amazon": "AMZN"
}

RAW_DATA_PATH = Path("data/raw/sec_filings")


def download_10k_filings():
    RAW_DATA_PATH.mkdir(parents=True, exist_ok=True)

    dl = Downloader("FinSight", "finsight@research.com")

    print("Starting 10-K filing downloads...\n")

    for company_name, ticker in COMPANIES.items():
        print(f"Downloading {company_name} ({ticker})...")
        try:
            dl.get(
                "10-K",
                ticker,
                after="2021-01-01",
                before="2024-01-01",
                limit=3
            )
            print(f"  ✅ {company_name} done")
            time.sleep(1)
        except Exception as e:
            print(f"  ❌ {company_name} failed: {e}")

    print("\nAll downloads complete!")


def verify_downloads():
    print("\n--- Verification ---")
    base = Path("sec-edgar-filings")
    if not base.exists():
        print("No files found.")
        return
    total = 0
    for name, ticker in COMPANIES.items():
        p = base / ticker / "10-K"
        if p.exists():
            count = len(list(p.iterdir()))
            total += count
            print(f"  {name}: {count} filing(s) ✅")
        else:
            print(f"  {name}: ❌ not found")
    print(f"\nTotal: {total} filings")


if __name__ == "__main__":
    download_10k_filings()
    verify_downloads()