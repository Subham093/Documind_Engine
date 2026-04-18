# from langchain.chains import RetrievalQA
# from langchain.llms import OpenAI
# from hybrid_search import bm25_search

# def build_rag(vectorstore):
#     retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

#     qa = RetrievalQA.from_chain_type(
#         llm=OpenAI(temperature=0),
#         retriever=retriever,
#         return_source_documents=True
#     )

#     return qa

from langchain_openai import OpenAI
from hybrid_search import bm25_search


# # 🔍 Hybrid Retrieval (Vector + Keyword)
# def hybrid_retrieval(query, vectorstore, documents):
#     vector_results = vectorstore.similarity_search(query, k=3)
#     keyword_results = bm25_search(query, documents)

#     # Combine + remove duplicates
#     combined = vector_results + keyword_results

#     unique_docs = []
#     seen = set()

#     for doc in combined:
#         if doc.page_content not in seen:
#             seen.add(doc.page_content)
#             unique_docs.append(doc)

#     return unique_docs[:4]


# # 🧠 Main RAG Function
# def ask_with_hybrid(query, vectorstore, documents):
#     docs = hybrid_retrieval(query, vectorstore, documents)

#     # Create context
#     context = "\n\n".join([doc.page_content for doc in docs])

#     # Custom prompt (VERY IMPORTANT)
#     prompt = f"""
# You are an AI assistant specialized in analyzing system logs.

# Instructions:
# - Understand the log context carefully
# - Identify errors, warnings, or anomalies
# - Provide clear explanation
# - Suggest possible causes and fixes

# Context:
# {context}

# Question:
# {query}

# Answer:
# """

#     llm = OpenAI(temperature=0)

#     response = llm(prompt)

#     return response

from hybrid_search import hybrid_retrieval
#from transformers import pipeline


# Load local model (only once)
#generator = pipeline("text-generation", model="distilgpt2")


from langchain_ollama import ChatOllama
from hybrid_search import hybrid_retrieval

# Initialize the LLM (Llama 3.2 via Ollama)
llm = ChatOllama(model="llama3.2")

def ask_with_hybrid(query, vectorstore, documents):
    # 1. Get the 4 most relevant chunks (2 from Vector, 2 from Keyword)
    relevant_docs = hybrid_retrieval(query, vectorstore, documents)
    
    # 2. Combine the text from those chunks into one string
    context_text = "\n\n".join([doc.page_content for doc in relevant_docs])
    
    # 3. Create a professional "System Prompt"
    prompt = f"""
    You are a helpful AI assistant. Answer the question based ONLY on the context provided below.
    If the answer is not in the context, say "I don't have enough information in the document to answer that."
    
    Context:
    {context_text}
    
    Question: {query}
    
    Answer:"""
    
    # 4. Ask the LLM to generate the answer
    response = llm.invoke(prompt)
    
    return response.content