from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# 1. Point to the same model we used to save the data
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 2. Connect to the existing database in the 'chroma_db' folder
print("Connecting to the Brain...")
vector_db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# 3. Ask a question (Replace this with a topic from your PDF!)
question = "What is the main topic of this document?" 

# 4. Search the database
print("Searching for answer...")
results = vector_db.similarity_search(question, k=1)

# 5. Show the result
print(f"\n--- Result found: ---")
print(results[0].page_content)