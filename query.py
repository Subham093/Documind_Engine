# from langchain_chroma import Chroma
# from langchain_huggingface import HuggingFaceEmbeddings

# # 1. Load the same embedding model we used to build the DB
# embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# # 2. Connect to the existing database
# vector_db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# # 3. Define a question
# question = "What is the summary of the document?" # Change this to test different questions!

# # 4. Search for the most relevant chunk
# # k=1 means "give me the 1 most relevant paragraph"
# results = vector_db.similarity_search(question, k=1)

# # 5. Print the result
# print(f"--- Question: {question} ---")
# print(f"--- Answer found in document: ---")
# print(results[0].page_content)

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