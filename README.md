<!-- 📷 IMAGE PLACEHOLDER — commented out so it won't show broken until a real
     file exists here.
📍 Top of README
🖼️ Wide banner (1280x400px), DocuMind name over a simple document + chat-bubble illustration
💡 Suggested file: docs/images/banner.png
Uncomment once added:
<p align="center"><img src="docs/images/banner.png" alt="DocuMind Banner" width="100%"></p>
-->

<h1 align="center">🧩 DocuMind</h1>
<p align="center"><b>Upload a document. Ask it questions in plain English. Get an answer — with proof of exactly where it came from.</b></p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white">
  <img src="https://img.shields.io/badge/LangChain-LCEL-1C3C3C">
  <img src="https://img.shields.io/badge/Vector%20DB-Chroma-purple">
  <img src="https://img.shields.io/badge/LLM-Groq%20%7C%20gpt--oss--120b-orange">
  <img src="https://img.shields.io/badge/License-MIT-green">
</p>

<!-- ℹ️ Repo is private (shown to interviewers directly rather than linked
     publicly), so GitHub-hosted stats badges (stars/last-commit) can't
     resolve — they're intentionally left out rather than shown broken. -->


> 💡 **New here?** Jump to [What Should I Expect?](#-what-should-i-expect-when-using-this-app) — it explains the whole app like you've never used an AI tool before.

---

## 📚 Table of Contents

1. [What Is This?](#-what-is-this-explain-it-like-im-10)
2. [The Problem It Solves](#-the-problem-it-solves)
3. [Features](#-features)
4. [Screenshots](#️-screenshots)
5. [Demo](#-demo)
6. [Architecture](#️-architecture)
7. [Tech Stack](#-tech-stack)
8. [Project Structure](#️-project-structure)
9. [How It Works — Complete Flow](#-how-it-works--the-complete-flow)
10. [Installation](#️-installation)
11. [Configuration](#-configuration)
12. [**Real-World Scenarios (Read This)**](#-real-world-scenarios-exactly-what-happens)
13. [Memory: What's Remembered](#-memory-whats-remembered-and-for-how-long)
14. [Capability Matrix](#-capability-matrix)
15. [What This App CAN / CANNOT Do](#-what-this-application-can-do)
16. [Edge Cases](#️-edge-cases)
17. [What Should I Expect?](#-what-should-i-expect-when-using-this-app)
18. [Security, Performance & Error Handling](#-security)
19. [Future Improvements](#-future-improvements)
20. [Contributing](#-contributing)
21. [License & Author](#-license)

---

## 📖 What Is This?

Imagine a super-smart friend who reads a book for you, then answers your questions about it — and always shows you the exact sentence they got the answer from, so you can check they're right.

**DocuMind is that friend, but it's a computer program.** You give it one document at a time (PDF, Word file, Excel sheet, CSV, or plain text), and then you chat with it about what's inside.

![Home Page](images/home.png)
*DocuMind right after opening — sidebar with the upload control, Clear Chat, and the Known Limitations panel, before any document is loaded.*

## 🎯 The Problem It Solves

Reading a 40-page report to find one fact is slow, and a basic Ctrl+F only catches *exact words* — not "the same idea phrased differently." DocuMind understands **meaning**, not just text matches, so you can ask in your own words and still get the right answer, as long as it actually exists in the document.

**Who benefits:** students digging through research papers, professionals reviewing contracts/reports, or anyone who'd rather ask than read the whole thing.

---

## ✨ Features

- 📄 **Multi-format uploads** — PDF, TXT, CSV, DOCX, XLSX, XLS
- 🖼️ **Automatic OCR** for scanned/image-only PDFs
- 🔍 **Hybrid search** — combines meaning-based (vector) search with exact keyword (BM25) search
- 💬 **Conversational follow-ups** within a session — "what about the second one?" is understood correctly
- 📎 **Transparent sourcing** — every answer shows the exact chunks it came from
- 🙅 **Refuses to guess** when the answer isn't in the document, or when a question needs the whole file at once (totals/counts)
- 🧹 **Auto-cleanup** — uploaded files are deleted right after processing
- ⚠️ **Honest, built-in limitations panel** in the app itself

---

## 🎥 Demo

> 🎬 Insert a short demo GIF here: upload → Process & Index → ask a question → see the sourced answer
> Suggested file: `docs/images/demo.gif`

---

## 🏗️ Architecture

> 📊 Insert a diagram here showing two paths:
> **Indexing:** `User → Streamlit UI → Document Loader (+ OCR fallback) → Text Splitter → ChromaDB`
> **Asking:** `Question → History-Aware Rewriter → Hybrid Retriever (Vector + BM25) → Groq LLM → Answer + Sources`
> Suggested file: `docs/images/architecture.png`

---

## 🧰 Tech Stack

| Category | Technology | Why it's used |
|---|---|---|
| Frontend | Streamlit | Chat-style web app, pure Python, no separate frontend needed |
| Orchestration | LangChain (LCEL + `langchain-classic`) | Chains question-rewriting → retrieval → answer generation |
| LLM | `openai/gpt-oss-120b` via Groq API | Fast inference; replaced `llama-3.3-70b-versatile`, which Groq is retiring Aug 16, 2026 |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | Turns text into meaning-vectors, runs locally — no document content leaves the server just to be embedded |
| Vector DB | ChromaDB | Stores and searches those vectors |
| Keyword search | `rank_bm25` | Catches exact terms/names/numbers meaning-search alone might miss |
| PDF reading | `pypdf` | Extracts text from normal PDFs |
| OCR | `pytesseract` + `pdf2image` (+ system `tesseract-ocr`, `poppler-utils`) | Reads scanned PDF pages as images |
| Other formats | `docx2txt`, `pandas`, `openpyxl` | Reads DOCX, CSV, Excel |
| Secrets | `python-dotenv` | Loads the Groq API key from `.env`, never hardcoded |
| Testing | `pytest` | Automated checks for the retriever and loader logic |
| Deployment | Hugging Face Spaces | Hosts the public live app |

> ℹ️ **No database, no login system, no user accounts.** Everything lives in your current browser session — see [Memory](#-memory-whats-remembered-and-for-how-long) below.

---

## 🗂️ Project Structure

```text
rag_engine/
│
├── app.py                     # ⭐ The live app — everything below happens here
├── document_loader.py         # ⭐ Reads any supported file type, with OCR fallback
├── hybrid_retriever.py        # ⭐ Vector + BM25 search, merged and de-duplicated
│
├── requirements.txt            # Python packages
├── packages.txt                 # System packages needed for OCR on deployment
├── .env                         # Your Groq API key (never committed)
│
├── asset/                       # App icon
├── chroma_db/                   # Auto-created — current document's vectors live here
├── temp_data/                   # Auto-created — holds an upload briefly, then deletes it
│
├── tests/
│   ├── test_hybrid_retriever.py
│   └── test_document_loader.py
│
└── experiments/                 # 🧪 Earlier prototypes, NOT used by the live app — kept as build history
    ├── app_backend.py           # Alternate FastAPI backend (upload/ask endpoints)
    ├── chat.py                  # Simplest RAG chain, using a local Ollama model
    ├── chunking.py
    ├── hybrid_search.py
    ├── ingest.py
    ├── loader.py
    ├── query.py
    ├── rag_pipeline.py
    └── store.py
```

**How the files interact:** `app.py` is the only file that runs directly. It imports `document_loader.py` to read whatever you upload, and `hybrid_retriever.py` to search through it. Nothing in `experiments/` is called by the running app.

---

## 🔄 How It Works — The Complete Flow

```
User opens the app
       ↓
User uploads a document (PDF / TXT / CSV / DOCX / XLSX / XLS)
       ↓
User clicks "🚀 Process & Index"
       ↓
Any previous document's data is deleted from the vector store
       ↓
Text is extracted (OCR kicks in automatically if it's a scanned PDF)
       ↓
Text is split into ~800-character overlapping chunks
       ↓
Chunks are turned into vectors (meaning-fingerprints) and stored in ChromaDB
       ↓
The temporary uploaded file is deleted from disk
       ↓
User types a question
       ↓
If it's a follow-up, the app rewrites it into a standalone question using chat history
       ↓
The hybrid retriever searches the CURRENT document's vectors (meaning + keyword combined)
       ↓
Retrieved chunks + question are sent to the AI model (Groq)
       ↓
The model writes an answer USING ONLY the retrieved chunks
       ↓
Answer is shown, with an expandable list of the exact chunks used
```

---

## ⚙️ Installation

1. Install Python 3.10+: `python --version`
2. Clone the repo: `git clone https://github.com/Subham093/Documind_Engine.git && cd Documind_Engine`
3. Create a virtual environment: `python -m venv venv`
4. Activate it — Windows: `venv\Scripts\Activate.ps1` · Mac/Linux: `source venv/bin/activate`
5. Install packages: `pip install -r requirements.txt`
6. Install OCR system tools — Windows: install Tesseract + Poppler and add to PATH · Mac: `brew install tesseract poppler` · Linux: `sudo apt install tesseract-ocr poppler-utils`
7. Get a free Groq API key at [console.groq.com](https://console.groq.com)
8. Create a `.env` file (see Configuration below)
9. Run it: `streamlit run app.py` → open `http://localhost:8501`

## 🔐 Configuration

```env
GROQ_API_KEY=your_groq_api_key_here
```

An environment variable is like a sticky note kept *outside* your code, so your secret key never ends up visible on GitHub. `.env` is already listed in `.gitignore` — double-check it stays that way before pushing.

---

## 🧭 Real-World Scenarios 

DocuMind is designed to support different real-world document interaction scenarios, from uploading and indexing a document to asking multiple questions and switching between documents.

Before exploring these scenarios, here's what the typical document-processing flow looks like:

A user begins by uploading a `.pdf` document and clicking **🚀 Process & Index**. DocuMind then starts reading and processing the uploaded document. While this is happening, the application displays a loading state to let the user know that the document is being processed.

![Processing the Document](images/upload1.png)

Once the document has been successfully processed and indexed, DocuMind displays a confirmation message indicating that the document is ready to be queried.

![Successfully Indexed](images/upload2.png)


### Scenario 1 — Upload One Document, Ask a Question

The app extracts its text, splits it into chunks, and stores those chunks as vectors. You ask *"What is the main objective of this paper?"* — the app searches only this document's chunks, retrieves the relevant ones, and the AI writes an answer using only that text, shown alongside its sources.

![Answer With Sources](images/qa-sources.png)
*A real question, answered — with the exact source chunks shown underneath so you can verify it yourself.*

### Scenario 2 — Ask Multiple Questions About the Same Document

✅ **Fully supported.** Ask as many questions as you like without re-uploading. Follow-ups like "and the second one?" work correctly, because the app rewrites them into standalone questions first.

![Multiple Questions About the Same Document](images/followup.png)
*The user asks multiple questions about the same document in a single conversation, including a follow-up question that depends on the previous context.*

### Scenario 3 — Upload a Second Document

❌ **The second document REPLACES the first — it does not add to it.** Clicking Process & Index on `document2.pdf` first wipes `document1.pdf`'s stored vectors, then indexes the new file fresh:

```python
if st.session_state.vector_store is not None:
    st.session_state.vector_store.delete_collection()   # old document's index is wiped
    st.session_state.vector_store = None
# ...then a fresh index is built from only the new document
```

There's no "combined knowledge base" — only one document is searchable at a time.

![Uploading a Second Document](images/seconddoc.png)
*The user uploads and processes a second document. The newly indexed document replaces the previously indexed document, so only the latest document is available for retrieval.*

### Scenario 4 — Ask About the First Document After Uploading a Second

⚠️ **This is the part worth knowing carefully.** Two things happen at once:
- `document1.pdf`'s vector data is **gone** (deleted in Scenario 3)
- But your **chat history is not cleared** on a new upload — only clicking "Clear Chat" clears it

So a question about `document1.pdf` gets rewritten using chat history that still mentions it, but the retriever can only search `document2.pdf`'s vectors — the only ones that exist. The model should correctly respond *"I cannot find this information in the uploaded document."*

> ⚠️ **Known limitation:** once a new document is uploaded, the previous one's content is permanently gone from the searchable index, even though the chat history still mentions it. **To ask about a previous document again, re-upload it** — which will, in turn, replace whatever's currently loaded. Clicking **Clear Chat** before switching documents avoids any confusing carryover.

![Question About the Previous Document](images/scenario4.png)
*After switching documents, a question about information from the previous document cannot be answered because its vectors have been removed from the searchable index.*

### Scenario 5 — Refresh / Close and Reopen the App

Refreshing starts a brand-new session. The vector store resets — the app does **not** automatically reconnect to the `chroma_db/` folder from before. You'll need to re-upload to continue. (Old vector data may still physically sit in `chroma_db/` on disk, but the running app never loads it back in automatically.)

---

## 🧠 Memory: What's Remembered, and For How Long

| Type of Memory | Supported? | Explanation |
|---|---|---|
| Remember current document while using it | ✅ | Yes, until a new upload or a page refresh |
| Ask multiple questions about the same document | ✅ | Fully supported |
| Remember chat history (conversation memory) | ✅ | Persists within a session, even across document uploads (see Scenario 4) |
| Upload multiple documents / combine them | ❌ | One document replaces the next |
| Search across multiple documents | ❌ | Not implemented |
| Ask about an older, already-replaced document | ❌ | Its data is deleted on new upload |
| Remember documents after refreshing the page | ❌ | Session resets, must re-upload |
| Remember documents after closing/reopening the app | ❌ | Same as above |
| Multiple users, properly isolated | ❌ | No login system; concurrent users share the same server-side `chroma_db`/`temp_data` folders |

---

## 📊 Capability Matrix

| User Action | Supported? | Actual Behavior |
|---|---|---|
| Upload one document | ✅ | PDF, TXT, CSV, DOCX, XLSX, XLS |
| Ask multiple questions about it | ✅ | Chat history kept for the session |
| OCR for scanned PDFs | ✅ | Automatic fallback when text extraction is near-empty |
| Upload multiple documents at once | ❌ | Each new upload deletes the previous one |
| Search across multiple documents | ❌ | Not implemented |
| Return to a previously uploaded document | ❌ | Its data is gone once replaced |
| Remember chat history within a session | ✅ | Until "Clear Chat" or a refresh |
| Persistent storage across sessions | ❌ | Refresh/reopen requires re-uploading |
| Multiple users, properly isolated | ❌ | Not designed for concurrent multi-user use |

---

## ✅ What This Application CAN Do

- Accept **one document at a time** — PDF, TXT, CSV, DOCX, XLSX, or XLS
- Automatically use **OCR** for scanned/image-only PDFs
- Answer questions using **hybrid search** (meaning-based + keyword-based)
- Handle **follow-up questions** naturally within a session
- Show the **exact source chunks** behind every answer
- Say **"I don't know"** honestly when the answer isn't present
- Refuse to guess on **counting/totaling questions**, since it never sees the whole file at once
- **Auto-clean** temporary uploaded files after processing

## ❌ What This Application CANNOT Do

- Hold **more than one document** in memory at a time
- Answer questions about a **previously uploaded document** once replaced
- **Combine or search across** multiple documents
- **Remember anything after a refresh** or app restart
- Guarantee it will **never make a mistake** — hallucination risk is reduced, not eliminated
- Reliably answer **"how many/total/sum/list everything"** style questions
- **Isolate multiple simultaneous users** from each other
- Preserve **tables, images, or formatting** from DOCX/PDF files

![Known Limitations Panel](images/limitations.png)
*This isn't a hidden footnote — the app discloses these exact limitations to the user, directly in the sidebar, before they ever hit one.*

---

## ⚠️ Edge Cases

| Situation | What Happens |
|---|---|
| Question asked with no document uploaded | Warning shown: *"Please upload a file first."* |
| Empty or blank PDF | OCR attempted as fallback; if still empty, a clear error is shown |
| Corrupted PDF | Loading fails gracefully — a processing error message, not a crash |
| Password-protected PDF | Fails to extract text, falls through to the "could not extract readable text" error |
| Scanned/image-only PDF | Detected automatically (near-empty text) and switched to OCR |
| PDF with tables | Table structure isn't preserved — becomes plain flowing text |
| Very large file | Takes longer to process; no explicit file-size limit enforced in code |
| Same file uploaded twice | Treated as a fresh upload — replaces whatever was previously indexed |
| Unrelated question | Model is instructed to say it can't find the answer, not guess |
| Groq API failure | Caught and shown as an error message, not a silent crash |

---

## 💡 What Should I Expect When Using This App?

- **Upload:** one file at a time — PDF, TXT, CSV, DOCX, XLSX, or XLS
- **Wait time:** a few seconds to under a minute; scanned PDFs (needing OCR) take noticeably longer
- **Answers:** short (up to 3 sentences for normal questions), always tied to a visible source you can double-check
- **New upload = fresh start**, not "adding to what's there"
- **Unsupported questions** (e.g. "how many total rows?") get an honest "can't answer that from what I have" instead of a guess
- **Invalid/unreadable PDFs** show a clear on-screen error, never a silent failure

---

## 🔒 Security

- API key loaded via `.env`, never hardcoded
- `.env`, `venv/`, and `chroma_db/` excluded from Git via `.gitignore`
- Temp files deleted immediately after processing
- No login system — single-user tool by design, not a multi-tenant platform

## ⚡ Performance

- Chunk size ~800 characters, 80-character overlap
- BM25 keyword index is rebuilt on every question — fine at single-document scale, would need caching at larger scale
- One-document-at-a-time design keeps search fast, at the cost of no multi-document support

## 🧯 Error Handling

- Unsupported file type → clear error naming the supported types
- Unreadable PDF, even after OCR → clear error about possible corruption/password-protection
- Temp file cleanup failures (e.g. Windows file locks) → caught, non-fatal
- General processing errors → shown as friendly messages, never raw crashes

---

## 🚀 Future Improvements

- [ ] Support multiple documents at once, with real cross-document search
- [ ] Auto-reconnect to a previous session's document after refresh
- [ ] Add basic user login/isolation for multi-user use
- [ ] Cache the BM25 index instead of rebuilding it per question
- [ ] Preserve tables from PDFs/DOCX properly
- [ ] Bring the FastAPI backend prototype up to parity and deploy as a real API

---

## 🤝 Contributing

1. Fork the repo
2. Branch: `git checkout -b feature/your-feature`
3. Make changes, add tests in `tests/`
4. Run `pytest tests/ -v`
5. Open a Pull Request

## 🤝 Contributing

Contributions, suggestions, and improvements are welcome!

To contribute:

1. Fork the repository.

2. Create a new feature branch:

   ```bash
   git checkout -b feature/your-feature
3. Make your changes and add or update tests where applicable.

4. Run `pytest tests/ -v`

5. Commit your changes and push the branch.

6. Open a Pull Request with a clear description of your changes.

## 📄 License

Licensed under the **MIT License** — see the `LICENSE` file for details.

#👤 Author
Subham Maheswari Jena

DocuMind was built as a hands-on Retrieval-Augmented Generation (RAG) project to explore document intelligence, semantic search, vector retrieval, and LLM-powered question answering.

I'm continuously improving the project and exploring practical applications of Generative AI, RAG systems, NLP, and AI-powered document processing.

## 🙏 Acknowledgements

This project was built with the help of the following open-source technologies and libraries:

LangChain — LLM application and RAG orchestration
Groq — LLM inference
ChromaDB — Vector storage and retrieval
Hugging Face — Embeddings and NLP models
Streamlit — Interactive web application
rank_bm25 — BM25-based keyword retrieval
Tesseract OCR — Optical character recognition
Poppler — PDF processing and rendering

A huge thanks to the open-source community and the developers maintaining these projects.

## 🔗 Connect With Me
🐙 **GitHub:** [Subham093](https://github.com/Subham093)
📧 **Email**: subhammaheswarijena11339@gmail.com