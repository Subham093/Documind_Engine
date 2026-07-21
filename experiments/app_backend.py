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

# UPDATED: llama-3.3-70b-versatile is being deprecated by Groq
# (decommission date: Aug 16, 2026). Migrated to openai/gpt-oss-120b,
# Groq's own recommended replacement — same model already used in
# NexInbox, so this stays consistent across projects.
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# Initialize Embeddings (Local processing for privacy)
# FIXED: was "all-MiniLM-L6-v2" here but "sentence-transformers/all-MiniLM-L6-v2"
# in app.py — inconsistent model string across files. Standardized to the
# full namespaced form (matches app.py) so both parts of the project
# resolve to the exact same embedding model.
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
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
    except HTTPException:
        # FIXED: the bare "except Exception" below used to catch this too,
        # turning a clean 404 into a generic 500. Re-raise as-is so a
        # missing file still correctly reports "404 Not Found".
        raise
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