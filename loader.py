# from langchain_community.document_loaders import TextLoader

# def load_logs(file_path):
#     loader = TextLoader(file_path, encoding="utf-8")
#     documents = loader.load()
#     return documents

from langchain_community.document_loaders import PyPDFLoader

def load_logs(file_path):
    # Check if the file is a PDF
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    else:
        # Fallback for text files
        from langchain_community.document_loaders import TextLoader
        loader = TextLoader(file_path, encoding="utf-8")
        
    documents = loader.load()
    return documents