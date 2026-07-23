import os
import warnings

# 1. Silence Python deprecation alerts
warnings.filterwarnings("ignore", category=DeprecationWarning)

# 2. Silence Hugging Face Hub log messages and token warnings
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_LOG_LEVEL"] = "ERROR"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import streamlit as st
from dotenv import load_dotenv

# LangChain Imports
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# Hybrid retriever (vector + BM25 keyword search combined)
from hybrid_retriever import HybridRetriever

# NEW: universal loader — handles pdf (+ scanned pdf via OCR), txt, csv, docx
from document_loader import load_any_document

# 1. SETUP

load_dotenv()
st.set_page_config(page_title="DocuMind", page_icon="asset/documind_icon_64.png", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = os.path.join(BASE_DIR, "temp_data")
PERSIST_DIR = os.path.join(BASE_DIR, "chroma_db")

if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)

# 2. MODELS

@st.cache_resource
def load_resources():
    # UPDATED: llama-3.3-70b-versatile is being deprecated by Groq
    # (decommission date: Aug 16, 2026). Migrated to openai/gpt-oss-120b,
    
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return llm, embeddings

llm, embeddings = load_resources()


# 3. STATE MANAGEMENT

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "chunks" not in st.session_state:
    st.session_state.chunks = None
if "sources_history" not in st.session_state:
    st.session_state.sources_history = []


# 4. SIDEBAR

with st.sidebar:
    st.title("📂 DocuMind Control")

    # NEW: accepts pdf, txt, csv, docx, xlsx, xls now (was pdf-only before)
    uploaded_file = st.file_uploader(
        "Upload a document",
        type=["pdf", "txt", "csv", "docx", "xlsx", "xls"]
    )

    if uploaded_file:
        if st.button("🚀 Process & Index"):
            try:
                with st.spinner("DocuMind is reading the document..."):

                    # Step 1 — Save uploaded file to temp_data folder
                    file_path = os.path.join(TMP_DIR, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    # Step 2 — Windows safe fix: clear old vectorstore
                    if st.session_state.vector_store is not None:
                        st.session_state.vector_store.delete_collection()
                        st.session_state.vector_store = None

                    # Step 3 — Load the document (any supported type)
                    # This raises ValueError with a clear message if the
                    # file can't be read (e.g. scanned PDF that even OCR
                    # can't handle, or an unsupported type).
                    docs = load_any_document(file_path)

                    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=800,
                        chunk_overlap=80
                    )
                    chunks = text_splitter.split_documents(docs)

                    # Step 4 — Create fresh vector store
                    st.session_state.vector_store = Chroma.from_documents(
                        documents=chunks,
                        embedding=embeddings,
                        persist_directory=PERSIST_DIR
                    )

                    st.session_state.chunks = chunks
                    st.session_state.sources_history = []  # reset for new doc

                    st.success(f"Successfully indexed: {uploaded_file.name}")

            except ValueError as e:
                # Clear, expected errors (unsupported type, unreadable file)
                st.error(f"⚠️ {str(e)}")
            except Exception as e:
                st.error(f"Processing Error: {str(e)}")
            finally:
                # NEW: clean up the temp file regardless of success/failure.
                # Once a document is chunked and embedded into Chroma, the
                # raw file in temp_data/ serves no further purpose — keeping
                # it around just wastes disk space. Without this, uploading
                # 100 files means 100 files permanently stuck on disk.
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass  # non-fatal — file may be briefly locked on Windows

    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.session_state.sources_history = []
        st.rerun()

    # NEW: visible, honest scope disclosure in the UI itself
    with st.expander("⚠️ Known Limitations"):
        st.markdown("""
        **PDF (text-based):** Only reads the text layer — images, charts,
        and diagrams inside the PDF are not read. Multi-column layouts may
        occasionally be read out of order. Tables may lose row/column
        structure.

        **PDF (scanned/image-only):** Uses OCR to read text, which is not
        perfect — poor scan quality, handwriting, or unusual fonts can
        cause misreads.

        **TXT:** Assumes UTF-8 encoding; other encodings may fail or show
        garbled text.

        **CSV / Excel:** Can look up specific rows/values, but **cannot
        reliably count total rows, sum/average a column, sort, or filter
        the whole sheet** — retrieval only sees a few rows at a time, never
        the entire file. Excel formulas are read as their last saved value,
        not recalculated.

        **DOCX:** Extracts plain text only — tables, images, headers/footers,
        comments, and tracked changes are not preserved.

        **All file types:** Only a small number of relevant chunks are
        retrieved per question. Questions needing the *entire* document at
        once (full counts, full summaries, "list everything") won't be
        fully accurate — the app will tell you when it can't answer this
        kind of question rather than guessing.
        """)


# 5. RAG LOGIC

def get_response(user_query, vector_store, chunks):

    retriever = HybridRetriever(vectorstore=vector_store, documents=chunks)

    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    # STRONGER — forces LLM to stay inside the document only, and to be
    # honest about a structural limitation: retrieval only ever sees a
    # handful of chunks, never the whole document, so counting/aggregate
    # questions cannot be reliably answered from what it's given.
    system_prompt = (
        "You are DocuMind AI. You ONLY answer questions based on the context provided below. "
        "If the answer is NOT found in the context, you MUST say exactly: "
        "'I cannot find this information in the uploaded document.' "
        "Do NOT use your own knowledge. Do NOT make up answers. "
        "\n\n"
        "IMPORTANT LIMITATION: You only ever see a small retrieved excerpt of "
        "the document, never the entire file at once. If the user asks a "
        "question that requires seeing the WHOLE document to answer correctly "
        "— such as 'how many total rows/entries are there', 'how many columns "
        "are there', 'what is the sum/average/total of X', 'list everything "
        "in this document', or any other counting/aggregation request — do "
        "NOT attempt to answer using only the excerpt you were given. "
        "Instead, respond with exactly: "
        "'This question needs the full document to answer accurately, but I "
        "only have access to a relevant excerpt, not the entire file. For "
        "exact counts, totals, or full-document questions, please check the "
        "original file directly.' "
        "For all other questions that are about the CONTENT or MEANING of "
        "the document (not counts/totals), answer normally using the context "
        "below. Use three sentences maximum for normal answers. "
        "\n\n"
        "{context}"
    )

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    return rag_chain.invoke({
        "input": user_query,
        "chat_history": st.session_state.chat_history
    })

# 6. CHAT UI

st.title("🧩 DocuMind")

ai_message_index = 0
for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    else:
        with st.chat_message("assistant"):
            st.markdown(message.content)
            if ai_message_index < len(st.session_state.sources_history):
                sources = st.session_state.sources_history[ai_message_index]
                if sources:
                    with st.expander(f"📄 View {len(sources)} source chunk(s) used"):
                        for i, chunk_text in enumerate(sources, start=1):
                            st.markdown(f"**Chunk {i}:**")
                            st.text(chunk_text)
                            st.divider()
            ai_message_index += 1

if query := st.chat_input("Ask me anything..."):
    with st.chat_message("user"):
        st.markdown(query)

    if st.session_state.vector_store:
        response = get_response(query, st.session_state.vector_store, st.session_state.chunks)
        assistant_answer = response["answer"]

        retrieved_docs = response.get("context", [])
        source_texts = [doc.page_content for doc in retrieved_docs]

        with st.chat_message("assistant"):
            st.markdown(assistant_answer)
            if source_texts:
                with st.expander(f"📄 View {len(source_texts)} source chunk(s) used"):
                    for i, chunk_text in enumerate(source_texts, start=1):
                        st.markdown(f"**Chunk {i}:**")
                        st.text(chunk_text)
                        st.divider()

        st.session_state.chat_history.extend([
            HumanMessage(content=query),
            AIMessage(content=assistant_answer),
        ])
        st.session_state.sources_history.append(source_texts)
    else:
        st.warning("Please upload a file first.")