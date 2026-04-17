# Financial RAG Agent - Test Questions Suite

## 1. Basic Qualitative Retrieval
*Tests `semantic_financial_search` for unstructured narrative text and metadata filtering.*

* **Q1:** Summarize the primary supply chain and manufacturing risk factors mentioned in Apple's 2025 10-K.
* **Q2:** What does Nvidia's management highlight as their main strategic initiatives or business goals for 2025?

## 2. Quantitative Retrieval & Table Parsing
*Tests HTML-to-Markdown table extraction and exact number retrieval.*

* **Q3:** Look at Boeing's 2025 10-K. What was their total revenue, and what were their total research and development (R&D) expenses?
* **Q4:** Break down Walmart's 2025 net sales by its different operating segments.

## 3. KPI Calculator Tool
*Tests `calculate_financial_kpi` and the agent's ability to locate two separate metrics for a formula.*

* **Q5:** Calculate Nvidia's net profit margin for the fiscal year 2025.
* **Q6:** Based on Apple's 2025 balance sheet, calculate their Return on Assets (ROA).
* **Q7:** What was Boeing's Debt-to-Equity ratio in 2025?

## 4. Multi-Year Search & YoY Growth
*Tests `multi_year_financial_search` combined with `yoy_growth` KPI calculation.*

* **Q8:** Compare Apple's total net sales for 2024 and 2025. What was the exact year-over-year percentage growth?
* **Q9:** Did Walmart's operating income increase or decrease between 2024 and 2025? Provide the percentage change.

## 5. Conversational Memory & Cross-Company Context
*Tests LangChain memory and the `python_calculator` for ad-hoc math between contexts.*

* **Turn 1:** What was Nvidia's total revenue in 2025?
* **Turn 2 (Follow-up):** How does that compare to Walmart's revenue for the same year? Calculate the absolute difference between the two.
## 6. Query Decomposition & Multi-Agent Passes
*Tests the `rewrite_query` and `route_after_rewrite` functions. The agent should split this single prompt into multiple independent retrieval tasks before synthesizing a final answer.*

* **Q10:** Compare the top three supply chain risks for Apple and Boeing in 2025, and then tell me which of the two companies had a higher net profit margin.
    * *Expected Behavior:* The agent should recognize it needs to run qualitative searches for two different tickers, plus quantitative searches for two different tickers, before calculating the margins and returning a synthesized response.

## 7. Out-of-Scope Data & Hallucination Checks
*Tests the system's strict metadata filtering and prevents the LLM from relying on its pre-trained knowledge when the RAG database lacks the data.*

* **Q11:** What were Tesla's top risk factors in 2025?
    * *Expected Behavior:* Since Tesla (TSLA) is not in your `data/raw` or `metadata.csv`, `semantic_financial_search` should return "No documents found." The agent must honestly reply that it does not have access to Tesla's filings, rather than hallucinating an answer.
* **Q12:** What was Walmart's total revenue in 2019?
    * *Expected Behavior:* The agent applies the `year=2019` filter. The DB returns nothing. The agent must state the data is unavailable.

## 8. HTML-to-Markdown Parser Fidelity (Table Integrity)
*Tests the specific parser feature mentioned in Section 3.2 of your handbook, which merges floating currency symbols (e.g., `$` and `4,521`) to prevent tokenization errors.*

* **Q13:** In Apple's 2025 10-K, what is the exact reported value for 'Cash and cash equivalents' on the balance sheet? Please include the currency symbol exactly as it is formatted in the text.
    * *Expected Behavior:* The agent should retrieve the table chunk and successfully output a fully formatted number (e.g., `$4,521`) rather than struggling to associate a disconnected `$` with the correct numerical token.

## 9. Hypothetical Arithmetic (Python REPL fallback)
*Tests if the agent correctly falls back to the `python_calculator` for ad-hoc math when the request doesn't match the strict parameters of your `calculate_financial_kpi` tool.*

* **Q14:** Find Boeing's total research and development (R&D) expenses for 2025. If they were to increase that specific expense by 18.5% next year, what would their projected R&D budget be?
    * *Expected Behavior:* The agent retrieves the R&D figure via search, realizes the `calculate_financial_kpi` tool doesn't handle hypothetical projections, and correctly writes a script like `(R&D_value * 1.185)` in the `python_calculator` to get the answer.

## 10. Memory Compression Threshold Test
*Tests the `HISTORY_THRESHOLD` (default: 4) defined in `config.py` to ensure the agent doesn't crash from context window overflow during long conversations.*

* **Turn 1:** What does Nvidia do?
* **Turn 2:** Who are their main competitors according to the 10-K?
* **Turn 3:** What was their total revenue in 2025?
* **Turn 4:** How much did they spend on R&D?
* **Turn 5 (The Trigger):** Based on all the numbers we just discussed, what percentage of their revenue goes toward R&D, and does this align with their strategic goals mentioned earlier?
    * *Expected Behavior:* Before executing Turn 5, the agent should trigger `summarize_history` to compress Turns 1-4 into a dense summary. It should retain the specific numbers and themes required to answer Turn 5 without exceeding the LLM's token limit.