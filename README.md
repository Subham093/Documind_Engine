<!-- 📷 IMAGE PLACEHOLDER — banner is commented out so it doesn't show as a broken image until you add a real file here. 📍 Top of README 🖼️ A wide banner (1280x400px) with the DocuMind name over a simple document + chat-bubble illustration 💡 Suggested file: docs/images/banner.png Once you've added that file, uncomment the two lines below: <p align="center"> <img src="docs/images/banner.png" alt="DocuMind Banner" width="100%"> </p> --> <h1 align="center">🧩 DocuMind</h1> <p align="center"><b>Upload a document. Ask it questions in plain English. Get honest, grounded answers — with proof of where they came from.</b></p> <p align="center"> <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white"> <img src="https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white"> <img src="https://img.shields.io/badge/LangChain-Framework-1C3C3C"> <img src="https://img.shields.io/badge/Vector%20DB-Chroma-purple"> <img src="https://img.shields.io/badge/LLM-Groq%20%7C%20gpt--oss--120b-orange"> <img src="https://img.shields.io/badge/License-MIT-green"> </p> <!-- ℹ️ The three badges below (license/stars/last-commit) only work once this is pushed to a REAL public GitHub repo. Replace YOUR_USERNAME/documind with your actual GitHub username and repo name, then uncomment: --> <!-- <p align="center"> <img src="https://img.shields.io/github/license/YOUR_USERNAME/documind"> <img src="https://img.shields.io/github/stars/YOUR_USERNAME/documind?style=social"> <img src="https://img.shields.io/github/last-commit/YOUR_USERNAME/documind"> </p> -->

💡 New here? Start with the What Should I Expect section — it explains the whole app like you've never used an AI tool before.

## 📖 What Is This? (Explain-it-like-I'm-10 version)

Imagine a super-smart friend who reads a book for you and then answers your questions about it — and always shows you the exact sentence they got the answer from, so you can check they're right.

**DocuMind is that friend, but it's a computer program.** You give it one document at a time (PDF, Word file, Excel sheet, CSV, or plain text), and then you chat with it about what's inside.

> ⚠️ **Read this whole README before using the app.** It tells you exactly what will happen at each step — no surprises.

---

## 🔄 The Complete Flow (What Happens, Start to Finish)

User Opens the App
↓
User Uploads a Document (PDF / TXT / CSV / DOCX / XLSX / XLS)
↓
User Clicks "🚀 Process & Index"
↓
Any Previous Document's Data Is Deleted From the Vector Store
↓
Text Is Extracted From the New File (OCR is used automatically if a PDF is scanned/image-only)
↓
Text Is Split Into ~800-Character Chunks
↓
Chunks Are Converted Into Vectors (Number-Lists Representing Meaning) and Stored in ChromaDB
↓
The Temporary Uploaded File Is Deleted From Disk
↓
User Types a Question in the Chat Box
↓
If This Isn't the First Question, the App Rewrites It Using Chat History (so "what about that?" becomes a full question)
↓
The Hybrid Retriever Searches the CURRENT Document's Vectors (Meaning-Search + Keyword-Search Combined)
↓
Retrieved Chunks + Question Are Sent to the AI Model (via Groq)
↓
The Model Writes an Answer USING ONLY the Retrieved Chunks
↓
Answer Is Shown in the Chat, With an Expandable List of the Exact Chunks Used


---

## 🧪 Real-World Scenarios (Exactly What Happens)

### Scenario 1 — Upload One PDF, Ask a Question
You upload `research_paper.pdf` and click Process & Index. The app extracts its text, splits it into chunks, and stores those chunks as vectors. You ask *"What is the main objective of this paper?"* The app searches only `research_paper.pdf`'s stored chunks, finds the relevant ones, and the AI model writes an answer using only that retrieved text — displayed along with the source chunks it used.

### Scenario 2 — Ask Multiple Questions About the Same Document
✅ **Fully supported.** After indexing one document, you can ask as many questions as you like without re-uploading. Each question also benefits from chat history — so a follow-up like "and the second one?" is understood correctly, because the app rewrites it into a standalone question first.

### Scenario 3 — Upload a Second Document
❌ **The second document REPLACES the first, it does not add to it.**
Here's exactly what happens: clicking Process & Index on `document2.pdf` first deletes all of `document1.pdf`'s stored vectors (`vector_store.delete_collection()`), *then* indexes `document2.pdf` fresh. There is no "combined knowledge base" — the app only ever holds one document's content at a time.

### Scenario 4 — Ask About the First Document After Uploading a Second (⚠️ important)
**This is where it gets tricky, and I want to be exact about it, because two different things happen at once:**

- `document1.pdf`'s vector data is **gone** — it was deleted in Scenario 3.
- But your **chat history is NOT cleared** when you upload a new document (only the "Clear Chat" button clears it).

So if you ask a question about `document1.pdf` after uploading `document2.pdf`:
1. The app rewrites your question using the still-present chat history (which still mentions `document1.pdf`'s topics).
2. It searches `document2.pdf`'s vectors (the only ones that exist) for anything relevant.
3. Since `document1.pdf`'s content isn't there anymore, the model should say: *"I cannot find this information in the uploaded document."*

> ⚠️ **Known Limitation:** Once a new document is uploaded, the previous document's content is permanently removed from the searchable index. Questions about it can no longer be answered correctly, even though the chat history *mentions* it. **To ask about a previous document again, you must re-upload it** — which will, in turn, delete whatever is currently loaded.

### Scenario 5 — Browser Refresh / Closing and Reopening the App
Refreshing the page (or closing and reopening the app) starts a brand-new session. `vector_store` resets to empty in that new session — the app does **not** automatically reconnect to the `chroma_db/` folder from before. **You must re-upload your document to use the app again.** (Old vector data may still physically exist in the `chroma_db/` folder on disk, but the running app doesn't load it back in automatically.)

---

## 🧠 Memory: What's Remembered, and For How Long

| Type of Memory | Supported? | Explanation |
|---|---|---|
| **Remember current document** | ✅ | Yes, for as long as you don't upload a new one or refresh the page |
| **Ask multiple questions about the same document** | ✅ | Fully supported within one session |
| **Remember chat history (conversation memory)** | ✅ | Yes, within the same session — persists even across document uploads (see Scenario 4's caveat) |
| **Upload multiple documents at once / combine them** | ❌ | Not supported — one document is replaced by the next |
| **Search across multiple documents** | ❌ | Not supported |
| **Ask about an older, already-replaced document** | ❌ | Not supported — its data is deleted on new upload |
| **Remember documents after refreshing the page** | ❌ | Not supported — session resets, must re-upload |
| **Remember documents after closing and reopening the app** | ❌ | Not supported — same as above |
| **Multiple users with properly isolated data** | ❌ | Not designed for this — no login system; concurrent users would share the same server-side `chroma_db`/`temp_data` folders |

---

## ✅ What This Application CAN Do

- Accept **one document at a time**: PDF, TXT, CSV, DOCX, XLSX, or XLS
- Automatically use **OCR** for scanned/image-only PDFs
- Answer questions about that document using **hybrid search** (meaning-based + keyword-based)
- Handle **multiple follow-up questions** in one session, understanding conversational references ("that", "it", "the second one")
- Show you the **exact source chunks** used for every answer
- Honestly say **"I don't know"** when the answer isn't in the document
- Refuse to guess on **counting/totaling questions** (e.g., "how many rows are there") since it never sees a whole spreadsheet/document at once — only a handful of relevant chunks
- **Automatically clean up** temporary uploaded files after processing

## ❌ What This Application CANNOT Do

- Cannot hold **more than one document** in its searchable memory at a time — a new upload deletes the old one
- Cannot answer questions about a **previously uploaded document** once it's been replaced
- Cannot **combine or search across** multiple documents
- Cannot **remember any document after a page refresh** or app restart — always requires a fresh upload
- Cannot guarantee it will **never make a mistake** — it's designed to reduce hallucination by only using retrieved text, but this isn't a 100% guarantee
- Cannot reliably answer **"how many/total/sum/list everything"** style questions, since it only sees retrieved excerpts, not the full file
- Cannot **isolate multiple simultaneous users** from each other — not built as a multi-tenant system
- Cannot preserve **tables, images, or formatting** from DOCX files, or images/charts inside PDFs

---

## 💡 What Should I Expect When Using This App?

- **Upload:** any single file — PDF, TXT, CSV, DOCX, XLSX, or XLS.
- **Wait time:** processing usually takes a few seconds to under a minute, depending on file size — scanned PDFs (which need OCR) take noticeably longer than normal text PDFs.
- **Answers:** short (up to 3 sentences for normal questions), always tied to a visible source chunk you can double check.
- **Uploading a new file:** wipes out the previous document — treat each upload as "starting fresh," not "adding to what's there."
- **Unsupported questions** (like "how many total rows are there?" on a spreadsheet): the app will tell you plainly it can't answer that from the excerpt it has, rather than guessing.
- **Invalid or unreadable PDF:** you'll see a clear on-screen error, not a silent failure or a crash.
- **PDF with no extractable text at all** (even after OCR): you'll see an error saying the file may be corrupted, password-protected, or blank.
- **If the AI can't find the answer:** it will say so directly — "I cannot find this information in the uploaded document" — instead of making something up.

---

## ⚠️ Edge Cases

| Situation | What Happens |
|---|---|
| Asking a question with no document uploaded | The app shows a warning: "Please upload a file first." |
| Empty or blank PDF | Text extraction returns almost nothing; OCR is attempted as a fallback; if still empty, a clear error is shown |
| Corrupted PDF | Loading fails; the user sees a processing error message, not a crash |
| Password-protected PDF | Will very likely fail to extract text and fall through to the "could not extract readable text" error |
| Scanned/image-only PDF | Automatically detected (very little extractable text) and switched to OCR |
| PDF with tables | Table structure (rows/columns) is **not** preserved — it becomes plain flowing text |
| Very large PDF | Will take longer to process (more chunks to embed); no explicit file-size limit is enforced in the code, so extremely large files could be slow |
| Uploading the same file twice | Treated as a completely new upload — replaces whatever was previously indexed (even if it's literally the same file) |
| Unrelated question (not in the document) | The model is instructed to say it can't find the answer, rather than guessing |
| Groq API failure | Caught and shown to the user as an error message, not a silent crash |

---

## 📊 Capability Matrix

| User Action | Supported? | Actual Behavior |
|---|---|---|
| Upload one document | ✅ | Fully supported for PDF, TXT, CSV, DOCX, XLSX, XLS |
| Ask multiple questions about it | ✅ | Chat history is kept for the session |
| OCR for scanned PDFs | ✅ | Automatic fallback when text extraction is near-empty |
| Upload multiple documents at once | ❌ | Each new upload deletes the previous one |
| Search across multiple documents | ❌ | Not implemented |
| Return to a previously uploaded document | ❌ | Its data is gone once replaced |
| Remember chat history within a session | ✅ | Persists until "Clear Chat" is pressed or the page is refreshed |
| Persistent document storage across sessions | ❌ | Refreshing/reopening the app requires re-uploading |
| Cross-session memory | ❌ | Not implemented |
| Multiple users, properly isolated | ❌ | Not designed for concurrent multi-user use |

---

## ✨ Features Summary

- 📄 Multi-format uploads (PDF, TXT, CSV, DOCX, XLSX, XLS)
- 🖼️ Automatic OCR for scanned PDFs
- 🔍 Hybrid search (meaning + keyword)
- 💬 Conversational follow-up understanding within a session
- 📎 Transparent sourcing — every answer shows its source chunks
- 🙅 Refuses to guess when the answer isn't present
- 🧹 Auto-deletes temp files after processing
- ⚠️ Honest, built-in disclosure of its own limitations (see below)

---

## 🏗️ Architecture

> 📊 **Insert a diagram here** showing: `User → Streamlit UI → Document Loader → Text Splitter → ChromaDB (single active document)`, and separately: `Question → History-Aware Rewriter → Hybrid Retriever → Groq LLM → Answer + Sources`.

---

## 🧰 Tech Stack

| Category | Technology | Why it's used |
|---|---|---|
| Frontend | Streamlit | Chat-style web app, pure Python |
| Orchestration | LangChain (LCEL + `langchain-classic`) | Chains together question-rewriting → retrieval → answer generation |
| LLM | `openai/gpt-oss-120b` via Groq API | Writes answers fast; replaced `llama-3.3-70b-versatile`, which Groq is retiring Aug 16, 2026 |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | Turns text into meaning-vectors, run locally |
| Vector DB | ChromaDB | Stores and searches those vectors |
| Keyword search | `rank_bm25` | Catches exact terms meaning-search might miss |
| PDF reading | `pypdf` | Extracts text from normal PDFs |
| OCR | `pytesseract` + `pdf2image` (+ `tesseract-ocr`, `poppler-utils`) | Reads scanned PDFs as images |
| Other formats | `docx2txt`, `pandas`, `openpyxl` | Reads DOCX, CSV, Excel |
| Secrets | `python-dotenv` | Loads API keys from `.env`, never hardcoded |
| Testing | `pytest` | Automated checks for the retriever and loader |
| Deployment | Hugging Face Spaces | Hosts the public live app |

---

## 🗂️ Project Structure

```text
rag_engine/
│
├── app.py                     # ⭐ The live app — everything described above happens here
├── document_loader.py         # ⭐ Reads any supported file type, with OCR fallback for scanned PDFs
├── hybrid_retriever.py        # ⭐ Vector + BM25 search, merged and de-duplicated
│
├── requirements.txt            # Python packages
├── packages.txt                 # System packages needed for OCR on deployment
├── .env                         # Your Groq API key (never committed)
│
├── asset/                       # App icon (⚠️ check naming matches app.py's reference)
├── chroma_db/                   # Auto-created — current document's vectors live here
├── temp_data/                   # Auto-created — holds an upload briefly, then deletes it
│
├── tests/
│   ├── test_hybrid_retriever.py
│   └── test_doc_loader.py
│
└── experiments/                 # 🧪 Earlier prototypes, NOT part of the live app — kept as learning history
    ├── app_backend.py           # Alternate FastAPI backend (upload/ask endpoints)
    ├── chat.py                  # Simplest RAG chain, fully local model (Ollama + Llama 3.2)
    ├── chunking.py
    ├── hybrid_search.py
    ├── ingest.py
    ├── loader.py
    ├── query.py
    ├── rag_pipeline.py
    └── store.py
```

---

## ⚙️ Installation

1. Install Python 3.10+: `python --version`
2. Clone the repo: `git clone https://github.com/Subham093/Rag_Engine.git && cd Rag_Engine`
3. Create a virtual environment: `python -m venv venv`
4. Activate it — Windows: `venv\Scripts\Activate.ps1` · Mac/Linux: `source venv/bin/activate`
5. Install packages: `pip install -r requirements.txt`
6. Install OCR system tools — Windows: install Tesseract + Poppler and add to PATH · Mac: `brew install tesseract poppler` · Linux: `sudo apt install tesseract-ocr poppler-utils`
7. Get a free Groq API key at [console.groq.com](https://console.groq.com)
8. Create a `.env` file (see Configuration below)
9. Run it: `streamlit run app.py`

## 🔐 Configuration

```env
GROQ_API_KEY=your_groq_api_key_here
```

An environment variable is like a sticky note kept outside your code, so your secret key never ends up visible on GitHub. `.env` is already listed in `.gitignore`.

---

## 🔒 Security

- API key loaded via `.env`, never hardcoded
- `.env`, `venv/`, and `chroma_db/` excluded from Git via `.gitignore`
- Temp files deleted right after processing
- No authentication/login system — single-user tool by design, not a multi-tenant platform (see Future Improvements)

## ⚡ Performance

- Chunk size ~800 characters with 80-character overlap
- BM25 keyword index is rebuilt on every question — fine at single-document scale, would need caching for larger scale
- One-document-at-a-time design keeps searches fast and focused, at the cost of not supporting multi-document search

## 🧯 Error Handling

- Unsupported file type → clear `ValueError` naming the supported types
- Unreadable PDF, even after OCR → clear error about possible corruption/password-protection
- Temp file cleanup failures (e.g. Windows file locks) → caught, non-fatal
- General processing errors → shown as friendly messages, not raw crashes

## 🚀 Future Improvements

- [ ] Support multiple documents at once, with real cross-document search
- [ ] Auto-reconnect to a previous session's document after refresh, instead of requiring re-upload
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

## 📄 License

> Add your chosen license here (e.g. MIT) and a matching `LICENSE` file.

## 👤 Author

**Subham** — building DocuMind as a hands-on RAG portfolio project.

## 🙏 Acknowledgements

LangChain · Groq · ChromaDB · HuggingFace · Streamlit · `rank_bm25` · Tesseract OCR & Poppler
