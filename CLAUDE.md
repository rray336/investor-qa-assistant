# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Investor Q&A Assistant powered by Claude, designed to help streamline investor communications. The application processes PDF documents (earnings calls, 10-Qs, analyst reports) and provides AI-powered question answering capabilities.

## Architecture

The project follows a full-stack architecture:

**Frontend (React)**
- `PDFUploader`: Bulk PDF upload with confidentiality flags
- `QuestionBox`: Single-turn question interface
- `PDFViewer`: Inline document viewing
- `TagFilterBar`: Document filtering and tagging
- `AnswerCard`: Formatted responses with confidence scores

**Backend (FastAPI + Claude)**
- `pdf_processor.py`: PDF parsing and chunking
- `embedding_store.py`: Vector embeddings (ChromaDB)
- `query_engine.py`: Retrieval system for relevant chunks
- `claude_interface.py`: Claude API integration
- `file_db.json`: Metadata storage for PDFs

## Development Setup

**Requirements:**
- Node.js + npm (frontend)
- Python 3.10+ (backend)
- Claude Code environment
- ChromaDB for vector storage

**Expected Directory Structure:**
```
investor-qa-app/
├── frontend/           # React application
├── backend/           # FastAPI server
├── embeddings/        # Vector storage
├── uploads/          # PDF file storage
└── README.md
```

**Note:** Currently only README.md exists - the actual implementation needs to be created following the architecture described in README.md.

## Key Workflows

**PDF Processing:**
1. Upload PDFs with confidentiality marking
2. Parse and chunk documents (~1000 tokens, 4000 characters)
3. Generate embeddings using Claude-compatible models
4. Store in vector database with metadata

**Q&A Process:**
1. Retrieve relevant chunks based on question similarity
2. Format prompt with context and question
3. Call Claude for professional, concise responses
4. Parse response into bullet points with confidence scores

## Security Considerations

- Confidential PDFs are tagged and excluded from embedding
- All processing is local by default
- Cloud deployment optional
- Claude configured to not retain prompts or train on inputs

## Future Development

The project is designed to support:
- Multi-user access controls
- Chat history and follow-up questions
- Auto-tagging by document type/segment
- Calendar integration for earnings schedules