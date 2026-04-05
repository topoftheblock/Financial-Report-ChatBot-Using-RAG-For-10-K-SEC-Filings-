import os
import chromadb
from typing import Optional, Dict, Any
from langchain.tools import tool
from langchain_experimental.tools.python.tool import PythonAstREPLTool
from pydantic import BaseModel, Field

# Ensure we point to the exact same ChromaDB path built by the chunker
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_PATH = os.path.join(BASE_DIR, "chroma_financial_db")
COLLECTION_NAME = "financial_statements"

def perform_metadata_search(query: str, filters: dict, n_results: int = 5) -> str:
    """Helper function to execute queries against ChromaDB with robust post-filtering"""
    try:
        chroma_client = chromadb.PersistentClient(path=DB_PATH)
        collection = chroma_client.get_collection(name=COLLECTION_NAME)
        
        # 1. Pre-filter: Only pass the 'ticker' to ChromaDB to completely avoid the $and syntax bug
        chroma_filter = {}
        if "ticker" in filters:
            chroma_filter = {"ticker": filters["ticker"]}
            
        # 2. Fetch a larger pool of results to ensure we have enough after Python filtering
        results = collection.query(
            query_texts=[query],
            n_results=30,
            where=chroma_filter if chroma_filter else None
        )
        
        if not results['documents'] or not results['documents'][0]:
            return "No financial documents found matching the query."
            
        # 3. Post-filter in Python: Match exact year and document type
        valid_chunks = []
        for i in range(len(results['documents'][0])):
            meta = results['metadatas'][0][i]
            chunk = results['documents'][0][i]
            
            # Check if this chunk matches ALL requested filters
            match = True
            for k, v in filters.items():
                if meta.get(k) != v:
                    match = False
                    break
                    
            if match:
                valid_chunks.append(chunk)
                if len(valid_chunks) == n_results:
                    break
                    
        if not valid_chunks:
            return f"No financial documents found matching the exact filters: {filters}"
            
        return "\n\n---\n\n".join(valid_chunks)
        
    except Exception as e:
        return f"Error connecting to database: {str(e)}"

class TableSearchInput(BaseModel):
    query: str = Field(description="The specific financial metric or table sought (e.g., 'Total Revenue', 'Operating Margins').")
    company_ticker: str = Field(description="The stock ticker of the company (e.g., 'AAPL', 'MSFT').")
    year: int = Field(description="The 4-digit financial year (e.g., 2023).")
    document_type: str = Field(description="The type of SEC filing (e.g., '10-K', '10-Q'). Default is '10-K'.", default="10-K")

@tool("search_financial_tables", args_schema=TableSearchInput)
def search_financial_tables(query: str, company_ticker: str, year: int, document_type: str = "10-K") -> str:
    """
    Search strictly within financial tables and numerical data. 
    Requires strict metadata filtering to prevent retrieving the wrong year or company.
    """
    # Flat dictionary for robust Python post-filtering
    filters = {
        "ticker": company_ticker.upper(),
        "year": year,
        "document_type": document_type.upper()
    }
    return perform_metadata_search(query=query, filters=filters, n_results=5)

@tool("search_unstructured_text")
def search_unstructured_text(query: str, company_ticker: Optional[str] = None) -> str:
    """
    Perform a semantic hybrid search over unstructured text like MD&A, Risk Factors, and Business Summaries.
    Use this for qualitative questions.
    """
    filters = {}
    if company_ticker:
        filters["ticker"] = company_ticker.upper()
        
    return perform_metadata_search(query=query, filters=filters, n_results=5)

def get_financial_tools() -> list:
    """Returns the list of tools available to the agent."""
    
    calculator_tool = PythonAstREPLTool(
        name="python_calculator",
        description="A Python shell. Use this to execute python commands to calculate math, percentages, or differences. Input should be a valid python command. Print the final answer."
    )
    
    return [
        search_financial_tables,
        search_unstructured_text,
        calculator_tool
    ]