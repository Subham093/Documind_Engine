from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from ingest import chunks  # This pulls in the chunks we already processed

# 1. Initialize the local embedding model
# This model runs on YOUR computer. No internet, no fees.
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 2. Create the database
# This stores your vectors in a folder named 'chroma_db'
print("Creating the brain (Vector Database)... please wait...")

vector_db = Chroma.from_documents(
    documents=chunks, 
    embedding=embeddings,
    persist_directory="./chroma_db"
)

print("Vector database created successfully! Look for the 'chroma_db' folder.")