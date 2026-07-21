"""
Basic tests for document_loader.py.

Run with: pytest tests/test_document_loader.py -v

These focus on the loader's routing logic and error handling rather
than the underlying third-party parsers (PyPDFLoader, Docx2txtLoader,
etc.), which are already tested by their own libraries.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from document_loader import load_any_document


def test_unsupported_extension_raises_value_error(tmp_path):
    bad_file = tmp_path / "notes.xyz"
    bad_file.write_text("some content")

    with pytest.raises(ValueError, match="Unsupported file type"):
        load_any_document(str(bad_file))


def test_txt_file_loads_successfully(tmp_path):
    txt_file = tmp_path / "sample.txt"
    txt_file.write_text("DocuMind reads plain text files correctly.")

    docs = load_any_document(str(txt_file))

    assert len(docs) >= 1
    assert "DocuMind" in docs[0].page_content


def test_csv_file_loads_one_document_per_row(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("name,age\nAsha,30\nRahul,25\n")

    docs = load_any_document(str(csv_file))

    # CSVLoader produces one Document per data row (2 rows here)
    assert len(docs) == 2
    assert "Asha" in docs[0].page_content


def test_excel_file_loads_one_document_per_row(tmp_path):
    import pandas as pd

    xlsx_file = tmp_path / "data.xlsx"
    df = pd.DataFrame({"name": ["Asha", "Rahul"], "age": [30, 25]})
    df.to_excel(xlsx_file, index=False, sheet_name="Sheet1")

    docs = load_any_document(str(xlsx_file))

    assert len(docs) == 2
    assert all(doc.metadata["sheet"] == "Sheet1" for doc in docs)
    assert "Asha" in docs[0].page_content


def test_nonexistent_file_raises_error(tmp_path):
    missing_path = str(tmp_path / "does_not_exist.txt")

    with pytest.raises(Exception):
        load_any_document(missing_path)