"""
Hybrid retriever: combines vector similarity search (semantic meaning)
with BM25 keyword search (exact word/term matching), then merges and
deduplicates the results.

Why this exists: pure vector search is great at "meaning" but can miss
exact terms — names, part numbers, specific phrases — that a keyword
search catches instantly. Combining both covers more ground than either
alone.
"""

from typing import List, Any
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from rank_bm25 import BM25Okapi


class HybridRetriever(BaseRetriever):
    """
    A LangChain-compatible retriever that fetches results from both
    a vector store and a BM25 keyword index, then merges them.

    Drop-in replacement for `vectorstore.as_retriever()` — works with
    create_history_aware_retriever() and create_retrieval_chain() exactly
    the same way.
    """

    vectorstore: Any
    documents: List[Document]
    vector_k: int = 3
    keyword_k: int = 2

    class Config:
        arbitrary_types_allowed = True

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:

        # 1. Semantic search — top matches by meaning
        vector_results = self.vectorstore.similarity_search(query, k=self.vector_k)

        # 2. Keyword search (BM25) — top matches by exact term overlap
        #    Rebuilt per query since chunk counts are small (single-PDF
        #    scale). For large multi-document corpora, this index should
        #    be built once and cached instead of rebuilt every call.
        corpus = [doc.page_content for doc in self.documents]
        tokenized_corpus = [doc.split() for doc in corpus]
        bm25 = BM25Okapi(tokenized_corpus)
        tokenized_query = query.split()
        scores = bm25.get_scores(tokenized_query)

        top_n_indices = sorted(
            range(len(scores)), key=lambda i: scores[i], reverse=True
        )[: self.keyword_k]
        keyword_results = [self.documents[i] for i in top_n_indices]

        # 3. Merge + deduplicate (a chunk found by both methods should
        #    only appear once)
        combined = vector_results + keyword_results
        seen_content = set()
        deduped_results = []
        for doc in combined:
            if doc.page_content not in seen_content:
                seen_content.add(doc.page_content)
                deduped_results.append(doc)

        return deduped_results