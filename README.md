# Investor Q&A Assistant (Claude-Powered)

## 📌 Overview

The Investor Q&A Assistant is a local, AI-powered web application designed to streamline investor communications. It enables users to upload earnings call transcripts, Q&A prep docs, 10-Qs, analyst reports, and other PDFs, then query the system to generate investor-style answers using Claude Code as the backend model.

---

## ⚙️ Features

- 📂 **Bulk PDF Upload** with option to mark each as confidential
- 🧠 **Persistent Knowledge Base** that accumulates over time
- 🔁 **Wipe-and-Reset Option** for starting fresh with new PDFs
- 🧾 **Rich React Interface** with PDF viewer, search, and filter/tag controls
- ❓ **Single-Turn Q&A Engine** — one question at a time
- 📊 **Answer Formatting**: concise bullet points with confidence scores
- 🔐 **Confidentiality-Aware Processing**
- 🔄 **On-Demand Embedding Refresh** when PDFs are re-uploaded
- 💼 **Professional, Corporate Tone** in all responses

---

## 🧱 Architecture

### 1. Frontend (React)

| Component         | Description                                            |
| ----------------- | ------------------------------------------------------ |
| 📁 `PDFUploader`  | Upload multiple PDFs at once, set confidentiality flag |
| 🔍 `QuestionBox`  | Submit single-turn questions                           |
| 📄 `PDFViewer`    | Inline viewer to browse uploaded PDFs                  |
| 🧩 `TagFilterBar` | Filter documents or questions by topic/tags            |
| 📋 `AnswerCard`   | Displays bullet-point answers with confidence score    |

### 2. Backend (FastAPI + Claude Code)

| Module                | Description                                      |
| --------------------- | ------------------------------------------------ |
| `pdf_processor.py`    | Parses and chunks PDFs                           |
| `embedding_store.py`  | Generates and stores embeddings (e.g., ChromaDB) |
| `query_engine.py`     | Retrieves top-k relevant chunks                  |
| `claude_interface.py` | Formats prompts and calls Claude Code            |
| `file_db.json`        | Lightweight metadata DB for PDF info and tags    |

---

## 🧠 Claude Integration

- Uses Claude Code (via local install or API if deployed later)
- Prompt format injects retrieved PDF chunks and current question
- Claude responds in markdown → parsed into bullet points + score

---

## 📁 File Upload Workflow

1. User uploads PDFs (via bulk drag-drop)
2. For each PDF:
   - Parse and chunk into ~500-1000 token segments
   - Embed chunks using Claude-compatible embedding model
   - Tag PDF with metadata (e.g., type = 10-Q, segment = Chicken)
   - Store in vector store (unless marked _confidential_)
3. Update local knowledge index

---

## ❓ Q&A Workflow

1. User enters a question
2. Backend retrieves top-k relevant embedded chunks
3. System builds a prompt for Claude:

You are a corporate investor relations assistant.
Answer professionally and concisely using only the context provided below.

[Contextual chunks here...]

Question: [User question]

4. Claude responds → parsed → formatted as:

- ✅ Bullet points
- 📉 Confidence score (based on relevance match or Claude estimate)

---

## 🖥️ Local Development Setup

### Requirements

- Node.js + npm
- Python 3.10+
- Claude Code environment (local or API key setup)
- ChromaDB (or another local vector DB)

### Suggested Folder Structure

investor-qa-app/
├── frontend/ (React)
│ ├── public/
│ └── src/
│ ├── components/
│ ├── pages/
│ └── App.jsx
├── backend/ (FastAPI)
│ ├── main.py
│ ├── pdf_processor.py
│ ├── embedding_store.py
│ ├── claude_interface.py
│ └── file_db.json
├── embeddings/
├── uploads/
└── README.md

---

## 🔐 Security Notes

- Confidential PDFs are tagged and skipped during embedding
- All computation is local by default
- Cloud deployment optional (e.g., with Vertex AI or AWS Bedrock)
- Claude does not retain prompts or train on user inputs (configurable)

---

## 🚧 Future Enhancements

- Multi-user access controls and audit logs
- Chat history and follow-up question support
- Auto-tagging by segment, document type, or quarter
- Integration with external calendar or earnings schedule

## 🔄 GitHub Integration

This project should be synced with a private GitHub repository to:

- Maintain version control and collaboration history
- Securely back up code, embeddings, and configuration
- Enable future CI/CD workflows for cloud deployment

Make sure to:

- Add `.env` and `uploads/` to `.gitignore`
- Regularly push commits with clear messages
- Optionally configure GitHub Actions for testing or cloud sync

---

## 📞 Contact

For feature requests or bug reports, please open an issue or contact the development team.
