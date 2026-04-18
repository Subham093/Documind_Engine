# from rank_bm25 import BM25Okapi

# def bm25_search(query, documents):
#     tokenized_docs = [doc.page_content.split() for doc in documents]
#     bm25 = BM25Okapi(tokenized_docs)

#     tokenized_query = query.split()
#     scores = bm25.get_scores(tokenized_query)

#     top_n = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:3]
    
#     return [documents[i] for i in top_n]

from rank_bm25 import BM25Okapi


# Keyword search (BM25)
def bm25_search(query, documents, k=2):
    # Convert docs to text
    corpus = [doc.page_content for doc in documents]

    # Tokenize
    tokenized_corpus = [doc.split() for doc in corpus]

    bm25 = BM25Okapi(tokenized_corpus)

    tokenized_query = query.split()

    scores = bm25.get_scores(tokenized_query)

    # Get top k results
    top_n = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]

    return [documents[i] for i in top_n]


# Hybrid search (vector + keyword)
def hybrid_retrieval(query, vectorstore, documents):
    vector_results = vectorstore.similarity_search(query, k=2)

    keyword_results = bm25_search(query, documents, k=2)

    # Combine results
    combined = vector_results + keyword_results

    return combined[:4]