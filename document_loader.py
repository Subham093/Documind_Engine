"""
Universal document loader for DocuMind.

Supports: .pdf (text-based only — scanned/image-only PDFs are not
supported, see load_any_document below), .txt, .csv, .docx, .xlsx, .xls

Usage:
    from document_loader import load_any_document
    docs = load_any_document("path/to/file.pdf")
"""

import os
import pandas as pd
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    Docx2txtLoader,
)

# Below this many extracted characters, a PDF is treated as having no
# usable text layer (e.g. scanned/image-only) and is rejected with a
# clear error rather than guessed at.
MIN_EXTRACTED_CHARS = 200


def _load_excel(file_path):
    """
    Loads an Excel file (.xlsx or .xls) and converts it into one
    LangChain Document per row — same approach as CSVLoader, so an
    uploaded Excel file behaves identically to an uploaded CSV in terms
    of chunking and retrieval.

    If the workbook has multiple sheets, every sheet is read and each
    row is tagged with its sheet name in the metadata.
    """
    all_sheets = pd.read_excel(file_path, sheet_name=None)  # dict of {sheet_name: DataFrame}

    documents = []
    for sheet_name, df in all_sheets.items():
        for row_index, row in df.iterrows():
            # Format each row as "column_name: value" lines, same style
            # LangChain's CSVLoader uses, so retrieval quality is consistent
            row_text = "\n".join(f"{col}: {row[col]}" for col in df.columns)
            documents.append(
                Document(
                    page_content=row_text,
                    metadata={
                        "source": file_path,
                        "sheet": sheet_name,
                        "row": row_index,
                    },
                )
            )
    return documents


def load_any_document(file_path):
    """
    Loads a document of any supported type and returns a list of
    LangChain Document objects, ready for chunking.

    Raises ValueError with a clear message if the file type is unsupported
    or if no readable text could be extracted at all (including scanned/
    image-only PDFs, which are not supported — see MIN_EXTRACTED_CHARS).
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        docs = PyPDFLoader(file_path).load()
        extracted_text = "".join(d.page_content for d in docs)

        if len(extracted_text.strip()) < MIN_EXTRACTED_CHARS:
            raise ValueError(
                "Could not extract readable text from this PDF. It may be "
                "a scanned/image-only PDF (not currently supported — "
                "DocuMind only reads PDFs with a real text layer), or the "
                "file may be corrupted, password-protected, or genuinely blank."
            )
        return docs

    elif ext == ".txt":
        return TextLoader(file_path, encoding="utf-8").load()

    elif ext == ".csv":
        return CSVLoader(file_path).load()

    elif ext == ".docx":
        return Docx2txtLoader(file_path).load()

    elif ext in (".xlsx", ".xls"):
        return _load_excel(file_path)

    else:
        raise ValueError(
            f"Unsupported file type: '{ext}'. Supported types: .pdf, .txt, .csv, .docx, .xlsx, .xls"
        )