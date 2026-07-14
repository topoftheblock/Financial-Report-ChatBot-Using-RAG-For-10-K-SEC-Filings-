from src.ingestion.chunker import chunk_markdown_file

MOCK_MARKDOWN = """
# PART I

## Item 1. Business
Apple Inc. designs, manufactures, and markets smartphones, personal computers, and wearables.

## Item 7. Management's Discussion
The following table shows our net sales by category:

| Category | 2024 | 2023 |
|---|---|---|
| iPhone | $ 200,000 | $ 190,000 |
| Mac | $ 40,000 | $ 38,000 |
| iPad | $ 25,000 | $ 24,000 |

### Risk Factors
Macroeconomic conditions could affect our margins.
""".strip()

BASE_METADATA = {
    "company": "AAPL",
    "ticker": "AAPL",
    "document_type": "10-K",
    "year": 2024,
}


def test_chunk_markdown_file_tags_base_metadata(tmp_path):
    md_path = tmp_path / "test_parsed_10k.md"
    md_path.write_text(MOCK_MARKDOWN, encoding="utf-8")

    chunks = chunk_markdown_file(str(md_path), BASE_METADATA)

    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.metadata["ticker"] == "AAPL"
        assert chunk.metadata["year"] == 2024
        assert chunk.metadata["document_type"] == "10-K"
        assert "section" in chunk.metadata


def test_chunk_markdown_file_keeps_table_intact_under_its_header(tmp_path):
    md_path = tmp_path / "test_parsed_10k.md"
    md_path.write_text(MOCK_MARKDOWN, encoding="utf-8")

    chunks = chunk_markdown_file(str(md_path), BASE_METADATA)

    table_chunks = [c for c in chunks if "iPhone" in c.page_content]
    assert len(table_chunks) == 1

    table_chunk = table_chunks[0]
    # The table stays tethered to its section header, and no row is split across chunks.
    assert table_chunk.metadata["section"] == "Item 7. Management's Discussion"
    assert "Mac" in table_chunk.page_content
    assert "iPad" in table_chunk.page_content
    assert "200,000" in table_chunk.page_content


def test_chunk_markdown_file_assigns_most_specific_section_name(tmp_path):
    md_path = tmp_path / "test_parsed_10k.md"
    md_path.write_text(MOCK_MARKDOWN, encoding="utf-8")

    chunks = chunk_markdown_file(str(md_path), BASE_METADATA)

    risk_chunks = [c for c in chunks if "Macroeconomic" in c.page_content]
    assert len(risk_chunks) == 1
    # Header 3 ("Risk Factors") is more specific than Header 2, so it wins.
    assert risk_chunks[0].metadata["section"] == "Risk Factors"
