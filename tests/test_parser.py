import pytest

from src.ingestion import parser
from src.ingestion.parser import parse_10k_html

MOCK_HTML = """
<html>
<body>
    <div><span style="font-weight: bold">PART I</span></div>
    <div><span style="font-weight: 700">Item 1. Business</span></div>
    <p>This is the business description of the test company.</p>

    <div><span style="font-weight: bold">Item 7. Management's Discussion</span></div>
    <p>Financial overview:</p>
    <table>
        <tr>
            <td></td>
            <td>2024</td>
            <td>2023</td>
        </tr>
        <tr>
            <td>Revenue</td>
            <td>$ 10,000</td>
            <td>$ 8,500</td>
        </tr>
        <tr>
            <td>Cost of Goods Sold</td>
            <td>$ 4,000</td>
            <td>$ 3,500</td>
        </tr>
    </table>
</body>
</html>
"""


@pytest.fixture(autouse=True)
def no_llm_summary(monkeypatch):
    # Table summarization calls the OpenAI API; keep the unit test offline/deterministic.
    monkeypatch.setattr(parser, "_summarize_table_with_llm", lambda table_md: "")


def test_parse_10k_html_rejects_non_html_input(tmp_path):
    bad_file = tmp_path / "not_html.txt"
    bad_file.write_text("hello")

    with pytest.raises(ValueError):
        parse_10k_html(str(bad_file), str(tmp_path / "out"))


def test_parse_10k_html_extracts_headings_and_table(tmp_path):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()

    test_file_path = raw_dir / "test_10k.html"
    test_file_path.write_text(MOCK_HTML, encoding="utf-8")

    # parse_10k_html derives the output directory via os.path.dirname(output_path),
    # so (matching how process_all_raw_html calls it) the path must end in "/".
    parse_10k_html(str(test_file_path), str(processed_dir) + "/")

    output_file = processed_dir / "10-K.md"
    assert output_file.exists()

    parsed_markdown = output_file.read_text(encoding="utf-8")

    # Section headers are promoted to Markdown headings.
    assert "# PART I" in parsed_markdown
    assert "## Item 1. Business" in parsed_markdown
    assert "## Item 7. Management's Discussion" in parsed_markdown

    # The financial table survives as a Markdown table, with figures intact.
    assert "Revenue" in parsed_markdown
    assert "10,000" in parsed_markdown
    assert "8,500" in parsed_markdown
