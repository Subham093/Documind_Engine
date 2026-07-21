from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. Define the path to your PDF
pdf_path = "data/Role of Corporate Social Responsibility in Social Development11.pdf" # Replace with your actual file name

# 2. Load the PDF
loader = PyPDFLoader(pdf_path)
documents = loader.load()

# 3. Split the text into manageable chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = text_splitter.split_documents(documents)

print(f"Loaded {len(documents)} pages.")
print(f"Split into {len(chunks)} chunks.")

