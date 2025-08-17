# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Investor Q&A Assistant powered by multiple AI models, designed to help streamline investor communications. The application processes PDF documents (earnings calls, 10-Qs, analyst reports) and provides AI-powered question answering capabilities using Claude, OpenAI, and Gemini models.

## Architecture

The project follows a full-stack architecture:

**Frontend (React)**
- `PDFUploader`: Bulk PDF upload with confidentiality flags
- `QuestionBox`: Single-turn question interface
- `PDFViewer`: Inline document viewing
- `TagFilterBar`: Document filtering and tagging
- `AnswerCard`: Formatted responses with confidence scores
- `SettingsPanel`: Configure AI model and chunking settings

**Backend (FastAPI)**
- `pdf_processor.py`: PDF parsing and chunking
- `embedding_store.py`: Vector embeddings (ChromaDB)
- `query_engine.py`: Retrieval system for relevant chunks
- `claude_interface.py`: Claude API integration
- `openai_interface.py`: OpenAI API integration
- `gemini_interface.py`: Gemini API integration
- `database.py`: Metadata storage for PDFs in Supabase

## Development Setup

**Requirements:**
- Node.js + npm (frontend)
- Python 3.10+ (backend)
- API keys for Claude, OpenAI, and/or Gemini
- Supabase account for database and storage

**Expected Directory Structure:**
```
investor-qa-app/
├── frontend/           # React application
├── backend/           # FastAPI server
├── .env               # Environment variables
└── README.md
```

**Note:** The project is fully implemented as described in the `README.md`.

## Key Workflows

**PDF Processing:**
1. Upload PDFs with confidentiality marking
2. Parse and chunk documents (~1000 tokens, 4000 characters)
3. Generate embeddings using a sentence-transformer model
4. Store in vector database with metadata

**Q&A Process:**
1. User selects an AI model.
2. Retrieve relevant chunks based on question similarity
3. Format prompt with context and question
4. Call the selected AI model for a professional, concise response
5. Parse response into bullet points with confidence scores

## Security Considerations

- Confidential PDFs are tagged and excluded from embedding
- All computation is local by default
- Cloud deployment optional
- AI models are configured not to retain prompts or train on inputs (by default, check provider policies)

## Future Development

The project is designed to support:
- Multi-user access controls
- Chat history and follow-up questions
- Auto-tagging by document type/segment
- Calendar integration for earnings schedules