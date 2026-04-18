# from fastapi import FastAPI
# from loader import load_logs
# from chunking import split_docs
# from store import create_vector_store
# from rag_pipeline import build_rag
# from rag_pipeline import ask_with_hybrid

# app = FastAPI()

# vectorstore = None
# qa_chain = None

# @app.post("/upload")
# def upload_logs(file_path: str):
#     global vectorstore, qa_chain

#     docs = load_logs(file_path)
#     chunks = split_docs(docs)
    
#     vectorstore = create_vector_store(chunks)
#     qa_chain = build_rag(vectorstore)

#     return {"message": "Logs uploaded successfully"}


# # @app.get("/ask")
# # def ask(query: str):
# #     response = qa_chain(query)
# #     return {"answer": response["result"]}

# @app.get("/ask")
# def ask(query: str):
#     answer = ask_with_hybrid(query, vectorstore, documents)
#     return {"answer": answer}

# from fastapi import FastAPI
# from loader import load_logs
# from chunking import split_docs
# from store import create_vector_store
# from rag_pipeline import ask_with_hybrid

# app = FastAPI()

# vectorstore = None
# documents = None


# @app.post("/upload")
# def upload_logs(file_path: str):
#     global vectorstore, documents

#     # Load logs
#     docs = load_logs(file_path)

#     # Save original docs for BM25
#     documents = docs

#     # Split into chunks
#     chunks = split_docs(docs)

#     # Create vector DB
#     vectorstore = create_vector_store(chunks)

#     return {"message": "Logs uploaded successfully"}


# @app.get("/ask")
# def ask(query: str):
#     if vectorstore is None:
#         return {"error": "Upload logs first!"}

#     answer = ask_with_hybrid(query, vectorstore, documents)

#     return {"answer": answer}

# from fastapi import FastAPI
# from pydantic import BaseModel

# from loader import load_logs
# from chunking import split_docs
# from store import create_vector_store
# from rag_pipeline import ask_with_hybrid

# app = FastAPI()

# vectorstore = None
# documents = None


# # ✅ Request model
# class FileInput(BaseModel):
#     file_path: str


# # ✅ Upload API
# @app.post("/upload")
# def upload_logs(data: FileInput):
#     global vectorstore, documents

#     file_path = data.file_path   # 🔥 FIXED LINE

#     # Load logs
#     docs = load_logs(file_path)
#     documents = docs

#     # Split
#     chunks = split_docs(docs)

#     # Store
#     vectorstore = create_vector_store(chunks)

#     return {"message": "Logs uploaded successfully"}

# @app.get("/ask")
# def ask(query: str):
#     if vectorstore is None:
#         # Check if we can load an existing DB if vectorstore is empty
#         return {"error": "No data loaded. Please upload a file path first!"}

#     # This now calls the fixed rag_pipeline that uses the LLM
#     answer = ask_with_hybrid(query, vectorstore, documents)

#     return {"answer": answer}

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# LangChain Imports
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Load environment variables from the .env file
load_dotenv()

app = FastAPI()

# --- Setup the Cloud LLM (Nexus RAG Engine) ---
# It automatically looks for "GROQ_API_KEY" in your .env file

# This pulls the key safely
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# Initialize Embeddings (Local processing for privacy)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = None

class FilePath(BaseModel):
    file_path: str

@app.post("/upload")
async def upload_file(data: FilePath):
    global vector_store
    try:
        # Check if file exists
        if not os.path.exists(data.file_path):
            raise HTTPException(status_code=404, detail=f"File not found at {data.file_path}")

        # Load and Split PDF
        loader = PyPDFLoader(data.file_path)
        docs = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(docs)
        
        # Create Vector Store
        vector_store = Chroma.from_documents(
            documents=chunks, 
            embedding=embeddings, 
            persist_directory="./chroma_db"
        )
        return {"message": "Nexus RAG: PDF processed and loaded successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ask")
async def ask_question(query: str):
    global vector_store
    if vector_store is None:
        return {"answer": "Engine not primed. Please upload a document first."}
    
    try:
        # 1. Similarity Search (Retrieval)
        results = vector_store.similarity_search(query, k=3)
        context = "\n".join([doc.page_content for doc in results])
        
        # 2. Augmented Generation
        prompt = f"""You are the Nexus RAG Assistant. 
        Use the following retrieved context to answer the question accurately.
        If the answer is not in the context, politely state that the information is missing.
        
        Context: {context}
        Question: {query}
        """
        
        response = llm.invoke(prompt)
        return {"answer": response.content}
        
    except Exception as e:
        return {"answer": f"System Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    # Run the server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)