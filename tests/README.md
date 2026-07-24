# Tests

Basic unit tests for DocuMind's custom logic — not the third-party libraries (LangChain, Chroma, etc.), which are already tested by their own maintainers.

## What's covered

- **`test_document_loader.py`** — routing logic for each supported file type (PDF, TXT, CSV, XLSX), and the unsupported-file-type error path
- **`test_hybrid_retriever.py`** — merge/deduplication logic between vector and keyword search results, using a fake vectorstore so no real embeddings or Chroma instance is needed

## Running the tests

From the project root:

```bash
pytest tests/ -v
```