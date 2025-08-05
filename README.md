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

## 🖥️ Deployment Guide

### 📋 Prerequisites

- Node.js 16+ and npm
- Python 3.9+ 
- Supabase account (for database)
- Anthropic API key (for Claude)
- Railway account (for backend deployment)
- Vercel account (for frontend deployment)

---

## 🔧 Backend Deployment

### 🏠 Local Development

**1. Environment Setup**
```bash
# Navigate to project root
cd investor-qa-ai

# Create .env file with required variables:
# SUPABASE_URL=your_supabase_project_url
# SUPABASE_ANON_KEY=your_supabase_anon_key  
# ANTHROPIC_API_KEY=your_anthropic_api_key
```

**2. Python Environment**
```bash
cd backend

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**3. Database Setup**
- Create Supabase project
- Create tables: `pdfs` and `chunks` (schema in database.py)
- Add your Supabase URL and key to .env

**4. Start Local Server**
```bash
python main.py
```
- Server runs on: `http://localhost:8001`
- Health check: `http://localhost:8001/health`

### 🚂 Railway Deployment (Production)

**1. Railway Setup**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to existing project or create new
railway link
```

**2. Environment Variables**
Set in Railway Dashboard > Variables:
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

**3. Deploy**
```bash
# Deploy from project root
railway up
```

**Configuration Files:**
- `Procfile`: `web: cd backend && python main.py`
- `railway.toml`: Contains build and deploy settings
- Auto-deploys on git push to main branch

---

## 🎨 Frontend Deployment

### 🏠 Local Development

**1. Environment Setup**
```bash
cd frontend

# Install dependencies  
npm install
```

**2. Local API Connection**
- Frontend connects to `http://localhost:8001` (via package.json proxy)
- Ensure backend is running locally first

**3. Start Development Server**
```bash
npm start
```
- App runs on: `http://localhost:3000`
- Hot-reload enabled

### ▲ Vercel Deployment (Production)

**1. Vercel Setup**
```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login
```

**2. Environment Variables**
Set in Vercel Dashboard > Settings > Environment Variables:
```
REACT_APP_API_URL=your_railway_backend_url
```

**3. Deploy**
```bash
# Deploy from project root
vercel

# Or auto-deploy via GitHub integration
```

**Configuration:**
- `vercel.json`: Defines build settings and SPA routing
- Builds from `frontend/` directory
- Auto-deploys on git push to main branch

---

## 🔄 Full Stack Deployment Workflow

**1. Backend First**
```bash
# Deploy backend to Railway
railway up
# Note the Railway URL (e.g., https://your-app.railway.app)
```

**2. Update Frontend Config**
```bash
# Set backend URL in Vercel environment variables
REACT_APP_API_URL=https://your-app.railway.app
```

**3. Deploy Frontend**
```bash
# Deploy frontend to Vercel
vercel --prod
```

**4. Test Full Stack**
- Visit Vercel frontend URL
- Test PDF upload and Q&A functionality
- Check Railway logs for backend issues

---

## 🏗️ Project Structure

```
investor-qa-ai/
├── backend/               # FastAPI server
│   ├── venv/             # Python virtual environment
│   ├── main.py           # FastAPI application
│   ├── requirements.txt  # Python dependencies
│   └── *.py             # Core modules
├── frontend/             # React application  
│   ├── src/             # React source code
│   ├── package.json     # Node dependencies
│   └── build/           # Production build output
├── .env                 # Environment variables (local)
├── Procfile            # Railway deployment config
├── railway.toml        # Railway settings
└── vercel.json         # Vercel deployment config
```

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
