import pytest

from src.agent import tools

SEEDED_DOCS = [
    {
        "document": "Apple's primary risk factors include supply chain disruption and FX exposure.",
        "metadata": {"ticker": "AAPL", "year": 2025, "section": "Risk Factors"},
    },
    {
        "document": "Apple total net sales were $390 billion in fiscal year 2025.",
        "metadata": {"ticker": "AAPL", "year": 2025, "section": "Net Sales"},
    },
    {
        "document": "Apple total net sales were $383 billion in fiscal year 2024.",
        "metadata": {"ticker": "AAPL", "year": 2024, "section": "Net Sales"},
    },
    {
        "document": "Boeing total net sales were $70 billion in fiscal year 2025.",
        "metadata": {"ticker": "BA", "year": 2025, "section": "Net Sales"},
    },
]


def _matches(metadata: dict, where: dict) -> bool:
    """Mimics ChromaDB's simple 'where' filter semantics for the shapes tools.py builds."""
    if where is None:
        return True
    if "$and" in where:
        return all(_matches(metadata, cond) for cond in where["$and"])
    if "$or" in where:
        return any(_matches(metadata, cond) for cond in where["$or"])
    return all(metadata.get(key) == value for key, value in where.items())


class FakeCollection:
    """Stands in for a ChromaDB collection: applies the real 'where' clause tools.py
    builds against seeded fixture data, without needing a real embedding model."""

    def __init__(self, docs):
        self._docs = docs

    def query(self, query_texts, n_results, where=None):
        matched = [d for d in self._docs if _matches(d["metadata"], where)]
        matched = matched[:n_results]
        return {
            "documents": [[d["document"] for d in matched]],
            "metadatas": [[d["metadata"] for d in matched]],
        }


class FakeClient:
    def __init__(self, docs):
        self._collection = FakeCollection(docs)

    def get_collection(self, name):
        return self._collection


@pytest.fixture
def seeded_client(monkeypatch):
    client = FakeClient(SEEDED_DOCS)
    monkeypatch.setattr(tools.chromadb, "PersistentClient", lambda path: client)
    return client


def test_semantic_search_filters_by_ticker_and_year(seeded_client):
    result = tools.semantic_financial_search.func(
        query="net sales", company_ticker="AAPL", year=2025
    )

    assert "Apple total net sales were $390 billion" in result
    assert "[Source: AAPL | Year: 2025 | Section: Net Sales]" in result
    # Must not leak Boeing's or the prior year's data into an AAPL/2025 query.
    assert "Boeing" not in result
    assert "383 billion" not in result


def test_semantic_search_returns_no_documents_message_for_unmatched_filter(
    seeded_client,
):
    result = tools.semantic_financial_search.func(
        query="net sales", company_ticker="AAPL", year=2099
    )

    assert result == "No documents found."


def test_multi_year_search_spans_requested_years_for_one_ticker(seeded_client):
    result = tools.multi_year_financial_search.func(
        query="net sales", company_ticker="AAPL", years=[2024, 2025]
    )

    assert "390 billion" in result
    assert "383 billion" in result
    assert "Boeing" not in result
