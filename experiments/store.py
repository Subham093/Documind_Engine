from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

def create_vector_store(chunks):
    # Use the same embedding model everywhere
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Save the chunks into a local folder named 'chroma_db'
    vectorstore = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory="./chroma_db"
    )
    
    return vectorstore