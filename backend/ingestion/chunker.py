# backend/ingestion/chunker.py

import json
import re
from pathlib import Path
from typing import Generator
from dotenv import load_dotenv

load_dotenv()

# Where SEC filings are saved by sec-edgar-downloader
FILINGS_PATH = Path("sec-edgar-filings")
OUTPUT_PATH  = Path("data/processed/chunks.jsonl")

COMPANIES = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Google": "GOOGL",
    "Meta": "META",
    "Amazon": "AMZN"
}

# Chunk config — tuned for finance docs
CHUNK_SIZE    = 600   # words per chunk
CHUNK_OVERLAP = 100   # word overlap between chunks


def clean_text(text: str) -> str:
    """Remove noise from SEC filing text."""
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    # Remove page numbers and headers
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
    # Remove special characters but keep financial symbols
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\$\%\(\)\n]', ' ', text)
    return text.strip()


def split_into_chunks(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP
) -> list[str]:
    """
    Split text into overlapping word-based chunks.
    Overlap ensures context is not lost at chunk boundaries.
    """
    words = text.split()
    chunks = []
    start  = 0

    while start < len(words):
        end   = start + chunk_size
        chunk = " ".join(words[start:end])
        if len(chunk.strip()) > 100:  # skip tiny chunks
            chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def extract_text_from_filing(filing_path: Path) -> str:
    """
    Extract plain text from SEC filing.
    SEC filings are saved as .txt or .htm files.
    """
    text = ""

    # Look for the main filing document
    for ext in ["*.txt", "*.htm", "*.html"]:
        files = list(filing_path.glob(ext))
        if files:
            try:
                raw = files[0].read_text(encoding="utf-8", errors="ignore")
                # Strip HTML tags if present
                raw = re.sub(r'<[^>]+>', ' ', raw)
                text = clean_text(raw)
                break
            except Exception as e:
                print(f"    Warning: could not read {files[0]}: {e}")

    return text


def process_all_filings() -> int:
    """
    Process all downloaded SEC filings into chunks.
    Each chunk gets rich metadata for retrieval.
    """
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    total_chunks = 0

    with open(OUTPUT_PATH, "w", encoding="utf-8") as out_file:

        for company_name, ticker in COMPANIES.items():
            company_path = FILINGS_PATH / ticker / "10-K"

            if not company_path.exists():
                print(f"  ⚠️  No filings found for {company_name}")
                continue

            print(f"\nProcessing {company_name} ({ticker})...")

            # Each subfolder is one annual filing
            filings = sorted(company_path.iterdir())

            for filing_idx, filing_dir in enumerate(filings):
                if not filing_dir.is_dir():
                    continue

                # Extract year from folder name
                folder_name = filing_dir.name
                year = "unknown"
                # SEC accession format: XXXXXXXXXX-YY-XXXXXX
                # YY = 2-digit year
                year_match = re.search(r'-(\d{2})-', folder_name)
                if year_match:
                    yy = int(year_match.group(1))
                    year = str(2000 + yy)

                print(f"  Filing {filing_idx + 1}: {folder_name} (year: {year})")

                text = extract_text_from_filing(filing_dir)

                if not text:
                    print(f"    ⚠️  No text extracted")
                    continue

                chunks = split_into_chunks(text)
                print(f"    → {len(chunks)} chunks created")

                for chunk_idx, chunk_text in enumerate(chunks):
                    chunk_record = {
                        "id": f"{ticker}_{year}_{chunk_idx:04d}",
                        "text": chunk_text,
                        "metadata": {
                            "company":     company_name,
                            "ticker":      ticker,
                            "year":        year,
                            "doc_type":    "10-K",
                            "chunk_index": chunk_idx,
                            "total_chunks": len(chunks),
                            "source":      str(filing_dir)
                        }
                    }
                    out_file.write(json.dumps(chunk_record) + "\n")
                    total_chunks += 1

    return total_chunks


if __name__ == "__main__":
    print("=== FinSight Chunker ===\n")
    print(f"Chunk size:    {CHUNK_SIZE} words")
    print(f"Chunk overlap: {CHUNK_OVERLAP} words")
    print(f"Output:        {OUTPUT_PATH}\n")

    total = process_all_filings()

    print(f"\n✅ Done! Total chunks created: {total}")
    print(f"Saved to: {OUTPUT_PATH.absolute()}")