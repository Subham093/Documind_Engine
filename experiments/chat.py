from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_classic.chains import RetrievalQA

# 1. Setup the Brain (Database)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# 2. Setup the Speaker (Local LLM)
llm = ChatOllama(model="llama3.2")

# 3. Create the "Chain"
# This chain takes your question, finds the answer in the DB, 
# and hands it to the LLM to write a sentence.
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_db.as_retriever()
)

# 4. Ask a question
question = "What is the importance of CSR?"
print(f"Asking: {question}...")

response = qa_chain.invoke(question)

print("\n--- AI Answer ---")
print(response['result'])