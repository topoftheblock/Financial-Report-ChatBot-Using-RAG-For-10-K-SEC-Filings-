# Financial Intelligence Platform (RAG Chatbot)

This project is a Retrieval-Augmented Generation (RAG) chatbot designed to extract, analyze, and synthesize financial data from SEC 10-K filings. It allows users to query complex financial documents using natural language, calculate specific metrics, and retrieve qualitative insights.

## Project Structure

The project is organized into modular components:

* **`app/`**: Contains the Streamlit frontend.
    * `main.py`: The main entry point for the Streamlit application.
    * `components.py`: Reusable UI components (sidebar, execution trace).
* **`src/`**: Contains the core logic.
    * **`agent/`**: 
        * `generator.py`: Initializes the LangChain agent and executor.
        * `prompt.py`: Contains the system instructions for the LLM.
        * `tools.py`: Defines the tools available to the agent (database search, python calculator).
    * **`ingestion/`**:
        * `parser.py`: Cleans raw SEC HTML files and converts tables and text to Markdown.
        * `chunker.py`: Splits the processed text into manageable chunks and stores them in ChromaDB.
    * `sec_10k_scraper.py`: A utility to download 10-K filings directly from the SEC EDGAR database.
* **`data/`**: Storage for SEC filings.
    * `raw/`: Downloaded HTML filings.
    * `processed/`: Cleaned text/Markdown files ready for ingestion.
    * `metadata.csv`: Records of the downloaded filings.
* **`chroma_financial_db/`**: The local vector database containing embedded document chunks.
* **`.env`**: Stores environment variables (e.g., `OPENAI_API_KEY`).
* **`requirements.txt`**: Python dependencies.

## Setup Instructions

### 1. Prerequisites

Ensure you have Python installed. It is recommended to use a virtual environment (like Anaconda or `venv`).

### 2. Install Dependencies

Install the required packages using pip:

```bash
pip install -r requirements.txt