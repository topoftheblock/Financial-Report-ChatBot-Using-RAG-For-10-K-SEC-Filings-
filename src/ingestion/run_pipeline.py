import os
from src.sec_10k_scraper import download_10ks
from src.ingestion.parser import process_all_raw_html
from src.ingestion.chunker import embed_all_processed_files

# Optional: Set absolute path so scripts don't get confused
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def main():
    print("=== STEP 1: Scraping SEC EDGAR ===")
    tickers_to_track = ["BA", "NVDA", "AAPL", "WMT"]
    download_10ks(
        tickers=tickers_to_track, 
        start_year=2024, 
        end_year=2025, 
        output_dir=os.path.join(BASE_DIR, "data")
    )
    
    print("\n=== STEP 2: Parsing HTML to Clean Markdown ===")
    process_all_raw_html()
    
    print("\n=== STEP 3: Chunking & Populating ChromaDB ===")
    embed_all_processed_files()

    print("\n=== PIPELINE COMPLETE ===")
    print("You can now run: python -m streamlit run app/main.py")

if __name__ == "__main__":
    main()