from hybrid_search import hybrid_retrieval
from langchain_ollama import ChatOllama

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