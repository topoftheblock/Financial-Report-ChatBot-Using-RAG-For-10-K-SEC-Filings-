import os
import chromadb
import numexpr as ne
from typing import Literal
from langchain.tools import tool

# Import the centralized logger created in Step 4
from src.utils.logger import get_logger

logger = get_logger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_PATH = os.path.join(BASE_DIR, "chroma_financial_db")
COLLECTION_NAME = "financial_statements"


@tool
def semantic_financial_search(
    query: str, company_ticker: str = None, year: int = None
) -> str:
    """
    Performs a semantic similarity search across financial documents and markdown tables.
    Provide a descriptive semantic 'query' (e.g., 'What are the top risk factors?' or 'Revenue and net income table').
    Optionally filter by 'company_ticker' (e.g., 'AAPL') and 'year' (e.g., 2024).
    """
    logger.info(
        f"semantic_financial_search called - Query: '{query}', Ticker: {company_ticker}, Year: {year}"
    )
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
            where=where_clause if where_clause else None,
        )

        if not results["documents"] or not results["documents"][0]:
            logger.info("semantic_financial_search returned no documents.")
            return "No documents found."

        valid_chunks = []
        for i in range(len(results["documents"][0])):
            meta = results["metadatas"][0][i]
            chunk = results["documents"][0][i]

            source_citation = f"[Source: {meta.get('ticker', 'Unknown')} | Year: {meta.get('year', 'Unknown')} | Section: {meta.get('section', 'Unknown')}]"

            # Extract the table summary from metadata so the agent can read it
            table_summary = meta.get("table_summary", "")
            summary_text = f"\nTable Summary: {table_summary}" if table_summary else ""

            formatted_chunk = f"{source_citation}{summary_text}\nExact Passage: {chunk}"

            valid_chunks.append(formatted_chunk)

        logger.info(
            f"semantic_financial_search retrieved {len(valid_chunks)} chunks successfully."
        )
        return "\n\n---\n\n".join(valid_chunks)

    except Exception as e:
        logger.error("Database error in semantic_financial_search", exc_info=True)
        return f"Database error: {str(e)}"


@tool
def multi_year_financial_search(
    query: str, company_ticker: str, years: list[int]
) -> str:
    """
    Performs a semantic search for a specific metric across MULTIPLE years.
    Ideal for comparing data (like Revenue or EPS) year-over-year.
    Provide the query, company_ticker, and a list of years (e.g., [2024, 2025]).
    """
    logger.info(
        f"multi_year_financial_search called - Query: '{query}', Ticker: {company_ticker}, Years: {years}"
    )
    try:
        chroma_client = chromadb.PersistentClient(path=DB_PATH)
        collection = chroma_client.get_collection(name=COLLECTION_NAME)

        # Build an OR condition for the years, and an AND condition for the ticker
        year_conditions = [{"year": y} for y in years]

        where_clause = {
            "$and": [{"ticker": company_ticker.upper()}, {"$or": year_conditions}]
        }

        results = collection.query(
            query_texts=[query],
            n_results=10,  # Retrieve more to ensure we get chunks from all requested years
            where=where_clause,
        )

        if not results["documents"] or not results["documents"][0]:
            logger.info("multi_year_financial_search returned no documents.")
            return "No documents found for the requested years."

        valid_chunks = []
        for i in range(len(results["documents"][0])):
            meta = results["metadatas"][0][i]
            chunk = results["documents"][0][i]

            source_citation = f"[Source: {meta.get('ticker', 'Unknown')} | Year: {meta.get('year', 'Unknown')} | Section: {meta.get('section', 'Unknown')}]"

            # Extract the table summary from metadata so the agent can read it
            table_summary = meta.get("table_summary", "")
            summary_text = f"\nTable Summary: {table_summary}" if table_summary else ""

            formatted_chunk = f"{source_citation}{summary_text}\nExact Passage: {chunk}"
            valid_chunks.append(formatted_chunk)

        logger.info(
            f"multi_year_financial_search retrieved {len(valid_chunks)} chunks successfully."
        )
        return "\n\n---\n\n".join(valid_chunks)

    except Exception as e:
        logger.error("Database error in multi_year_financial_search", exc_info=True)
        return f"Database error: {str(e)}"


@tool
def calculate_financial_kpi(
    kpi_name: Literal[
        "margin",
        "roe",
        "roa",
        "debt_to_equity",
        "yoy_growth",
        "free_cash_flow",
        "eps",
        "current_ratio",
        "cac",
        "pe_ratio",
    ],
    value1: float,
    value2: float,
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
    - 'eps': value1 = net income, value2 = average outstanding shares
    - 'current_ratio': value1 = current assets, value2 = current liabilities
    - 'cac': value1 = total sales & marketing expenses, value2 = new customers acquired
    - 'pe_ratio': value1 = current share price, value2 = earnings per share
    """
    logger.info(
        f"calculate_financial_kpi called - KPI: {kpi_name}, Val1: {value1}, Val2: {value2}"
    )
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
        elif kpi_name == "eps":
            result = value1 / value2
            return f"${result:,.2f}"
        elif kpi_name == "current_ratio":
            result = value1 / value2
            return f"{result:.2f}x"
        elif kpi_name == "cac":
            result = value1 / value2
            return f"${result:,.2f}"
        elif kpi_name == "pe_ratio":
            result = value1 / value2
            return f"{result:.2f}x"
        else:
            logger.warning(f"Unknown KPI requested: {kpi_name}")
            return "Unknown KPI requested."

    except ZeroDivisionError:
        logger.warning(
            f"Division by zero attempted for KPI {kpi_name} with denominator {value2}"
        )
        return "Error: Division by zero. Check if the denominator (value2) is correct."
    except Exception as e:
        logger.error("Calculation error in calculate_financial_kpi", exc_info=True)
        return f"Calculation error: {str(e)}"


@tool("python_calculator")
def python_calculator(expression: str) -> str:
    """
    A highly secure calculator for computing financial metrics.
    Use this tool to calculate YoY growth, margins, or basic arithmetic.
    Provide only mathematical expressions (e.g., '((1500 - 1200) / 1200) * 100').
    """
    logger.info(f"Secure python_calculator invoked with expression: {expression}")

    try:
        # Sanitize input to remove any accidental markdown formatting or newlines
        clean_expression = expression.replace("`", "").strip()

        # ne.evaluate is strictly limited to mathematical parsing
        # It physically cannot execute system commands, classes, or OS-level functions
        result = ne.evaluate(clean_expression)

        # Extract the scalar value if it's a 0-d array
        final_result = float(result)

        logger.info(f"Calculation successful: {final_result}")
        return str(final_result)

    except Exception:
        logger.error(
            f"Failed to evaluate mathematical expression: {expression}", exc_info=True
        )
        return "Error: Invalid mathematical expression. Please ensure you are only using numbers and basic operators (+, -, *, /)."
