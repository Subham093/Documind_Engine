"""
Basic tests for hybrid_retriever.py.

Run with: pytest tests/test_hybrid_retriever.py -v

Uses a fake vectorstore (no real embeddings/Chroma needed) so these
tests run fast and don't depend on any external service or model
download — only the merge/dedup logic of HybridRetriever itself is
under test here.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.documents import Document
from hybrid_retriever import HybridRetriever


class FakeVectorStore:
    """Returns a fixed, pre-set list of docs regardless of the query —
    enough to test HybridRetriever's merge/dedup behavior in isolation."""

    def __init__(self, docs_to_return):
        self.docs_to_return = docs_to_return

    def similarity_search(self, query, k=3):
        return self.docs_to_return[:k]


def _make_docs(texts):
    return [Document(page_content=t) for t in texts]


def test_merges_vector_and_keyword_results_without_duplicates():
    all_docs = _make_docs([
        "The invoice total is $500.",
        "Payment is due within 30 days.",
        "Contact billing@example.com for questions.",
    ])

    # Vector search "finds" doc 0 and 1; BM25 will independently score
    # against the same corpus, so doc 0 may show up in both — the
    # retriever should still return each unique chunk only once.
    fake_vectorstore = FakeVectorStore(docs_to_return=all_docs[:2])

    retriever = HybridRetriever(
        vectorstore=fake_vectorstore,
        documents=all_docs,
        vector_k=2,
        keyword_k=2,
    )

    results = retriever.invoke("invoice total")

    seen = set()
    for doc in results:
        assert doc.page_content not in seen, "Duplicate chunk returned"
        seen.add(doc.page_content)


def test_respects_configured_k_values():
    all_docs = _make_docs([f"Chunk number {i}" for i in range(10)])
    fake_vectorstore = FakeVectorStore(docs_to_return=all_docs)

    retriever = HybridRetriever(
        vectorstore=fake_vectorstore,
        documents=all_docs,
        vector_k=1,
        keyword_k=1,
    )

    results = retriever.invoke("chunk")

    # At most vector_k + keyword_k results (fewer if there's overlap/dedup)
    assert len(results) <= 2


def test_empty_query_does_not_crash():
    all_docs = _make_docs(["Some content here."])
    fake_vectorstore = FakeVectorStore(docs_to_return=all_docs)

    retriever = HybridRetriever(
        vectorstore=fake_vectorstore,
        documents=all_docs,
        vector_k=1,
        keyword_k=1,
    )

    results = retriever.invoke("")
    assert isinstance(results, list)