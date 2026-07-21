"""
Universal document loader for DocuMind.

Supports: .pdf (including scanned/image-only PDFs via OCR fallback),
.txt, .csv, .docx

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

# Below this many extracted characters, a PDF is treated as scanned/image-only
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


def _ocr_pdf(file_path):
    """
    Fallback for scanned/image-only PDFs: converts each page to an image,
    then runs OCR (Tesseract) on it to extract text.
    Only triggered when normal text extraction comes back near-empty.
    """
    from pdf2image import convert_from_path
    import pytesseract

    pages = convert_from_path(file_path)
    documents = []
    for i, page_image in enumerate(pages):
        text = pytesseract.image_to_string(page_image)
        documents.append(
            Document(
                page_content=text,
                metadata={"page": i, "source": file_path, "extracted_via": "ocr"},
            )
        )
    return documents


def load_any_document(file_path):
    """
    Loads a document of any supported type and returns a list of
    LangChain Document objects, ready for chunking.

    Raises ValueError with a clear message if the file type is unsupported
    or if no readable text could be extracted at all.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        docs = PyPDFLoader(file_path).load()
        extracted_text = "".join(d.page_content for d in docs)

        if len(extracted_text.strip()) < MIN_EXTRACTED_CHARS:
            # Likely scanned/image-only — fall back to OCR
            docs = _ocr_pdf(file_path)
            extracted_text = "".join(d.page_content for d in docs)

            if len(extracted_text.strip()) < MIN_EXTRACTED_CHARS:
                raise ValueError(
                    "Could not extract readable text from this PDF, even with OCR. "
                    "The file may be corrupted, password-protected, or genuinely blank."
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