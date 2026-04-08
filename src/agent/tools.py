import os
import chromadb
from typing import Literal
from langchain.tools import tool
from langchain_experimental.tools.python.tool import PythonAstREPLTool

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_PATH = os.path.join(BASE_DIR, "chroma_financial_db")
COLLECTION_NAME = "financial_statements"

@tool
def semantic_financial_search(query: str, company_ticker: str = None, year: int = None) -> str:
    """
    Performs a semantic similarity search across financial documents and markdown tables.
    Provide a descriptive semantic 'query' (e.g., 'What are the top risk factors?' or 'Revenue and net income table').
    Optionally filter by 'company_ticker' (e.g., 'AAPL') and 'year' (e.g., 2024).
    """
    try:
        chroma_client = chromadb.PersistentClient(path=DB_PATH)
        collection = chroma_client.get_collection(name=COLLECTION_NAME)
        
        # Build ChromaDB metadata filters dynamically based on LLM input
        where_clause = {}
        conditions = []
        
        if company_ticker:
            conditions.append({"ticker": company_ticker.upper()})
        if year:
            conditions.append({"year": year})
            
        if len(conditions) > 1:
            where_clause = {"$and": conditions}
        elif len(conditions) == 1:
            where_clause = conditions[0]
        else:
            where_clause = None

        # Execute semantic vector search
        results = collection.query(
            query_texts=[query], 
            n_results=5, 
            where=where_clause if where_clause else None
        )
        
        if not results['documents'] or not results['documents'][0]:
            return "No documents found."
            
        valid_chunks = []
        for i in range(len(results['documents'][0])):
            meta = results['metadatas'][0][i]
            chunk = results['documents'][0][i]
            
            # Keep the citation formatting so the Reviewer instruction still works
            # CHANGED: 'Item' was replaced with 'section' to pull the correct header metadata
            source_citation = f"[Source: {meta.get('Ticker', 'Unknown')} | Year: {meta.get('Year', 'Unknown')} | Section: {meta.get('Section', 'Unknown')}]"
            formatted_chunk = f"{source_citation}\nExact Passage: {chunk}"
            
            valid_chunks.append(formatted_chunk)
                    
        return "\n\n---\n\n".join(valid_chunks)
    except Exception as e:
        return f"Database error: {str(e)}"

@tool
def multi_year_financial_search(query: str, company_ticker: str, years: list[int]) -> str:
    """
    Performs a semantic search for a specific metric across MULTIPLE years.
    Ideal for comparing data (like Revenue or EPS) year-over-year.
    Provide the query, company_ticker, and a list of years (e.g., [2024, 2025]).
    """
    try:
        chroma_client = chromadb.PersistentClient(path=DB_PATH)
        collection = chroma_client.get_collection(name=COLLECTION_NAME)
        
        # Build an OR condition for the years, and an AND condition for the ticker
        year_conditions = [{"year": y} for y in years]
        
        where_clause = {
            "$and": [
                {"ticker": company_ticker.upper()},
                {"$or": year_conditions}
            ]
        }

        results = collection.query(
            query_texts=[query], 
            n_results=10, # Retrieve more to ensure we get chunks from all requested years
            where=where_clause
        )
        
        if not results['documents'] or not results['documents'][0]:
            return "No documents found for the requested years."
            
        valid_chunks = []
        for i in range(len(results['documents'][0])):
            meta = results['metadatas'][0][i]
            chunk = results['documents'][0][i]
            
            source_citation = f"[Source: {meta.get('Ticker', 'Unknown')} | Year: {meta.get('Year', 'Unknown')} | Section: {meta.get('Section', 'Unknown')}]"
            formatted_chunk = f"{source_citation}\nExact Passage: {chunk}"
            valid_chunks.append(formatted_chunk)
                    
        return "\n\n---\n\n".join(valid_chunks)
    except Exception as e:
        return f"Database error: {str(e)}"

@tool
def calculate_financial_kpi(
    kpi_name: Literal["margin", "roe", "roa", "debt_to_equity", "yoy_growth", "free_cash_flow"],
    value1: float,
    value2: float
) -> str:
    """
    Calculates standard financial KPIs using exact arithmetic. 
    Provide the kpi_name and the two raw numeric values required.
    
    Mapping:
    - 'margin': value1 = profit (gross/operating/net), value2 = total revenue
    - 'roe': value1 = net income, value2 = shareholder equity
    - 'roa': value1 = net income, value2 = total assets
    - 'debt_to_equity': value1 = total debt, value2 = total equity
    - 'yoy_growth': value1 = current year value, value2 = previous year value
    - 'free_cash_flow': value1 = operating cash flow, value2 = capital expenditures
    """
    try:
        if kpi_name == "margin":
            result = (value1 / value2) * 100
            return f"{result:.2f}%"
        elif kpi_name in ["roe", "roa"]:
            result = (value1 / value2) * 100
            return f"{result:.2f}%"
        elif kpi_name == "debt_to_equity":
            result = value1 / value2
            return f"{result:.2f}x"
        elif kpi_name == "yoy_growth":
            result = ((value1 - value2) / value2) * 100
            return f"{result:.2f}%"
        elif kpi_name == "free_cash_flow":
            result = value1 - value2
            return f"${result:,.2f}"
        else:
            return "Unknown KPI requested."
    except ZeroDivisionError:
        return "Error: Division by zero. Check if the denominator (value2) is correct."
    except Exception as e:
        return f"Calculation error: {str(e)}"

python_calculator = PythonAstREPLTool(
    name="python_calculator",
    description="Python shell. Use this to execute math, percentages, or differences. Input valid python."
)