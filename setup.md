# Investor Q&A Assistant - Setup Guide

## Prerequisites

- Python 3.10 or higher
- Node.js 16 or higher
- npm or yarn
- Supabase account
- Anthropic API key (Claude)

## Setup Steps

### 1. Clone and Setup Environment

```bash
# Navigate to project directory
cd investor-qa-ai

# Copy environment template
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` file with your credentials:

```env
# Get from your Supabase project settings
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here

# Get from Anthropic Console (https://console.anthropic.com/)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 3. Supabase Database Setup

1. Create a new Supabase project at https://supabase.com
2. Go to SQL Editor and run these commands:

```sql
-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create PDFs table
CREATE TABLE pdfs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    is_confidential BOOLEAN DEFAULT FALSE,
    chunk_count INTEGER DEFAULT 0,
    upload_date TIMESTAMP DEFAULT NOW(),
    file_size BIGINT
);

-- Create chunks table with vector embeddings
CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pdf_id UUID REFERENCES pdfs(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding VECTOR(384)  -- 384 dimensions for all-MiniLM-L6-v2
);

-- Create index on embeddings for fast similarity search
CREATE INDEX ON chunks USING ivfflat (embedding vector_cosine_ops);
```

3. Create a storage bucket:
   - Go to Storage → Create bucket
   - Name: `pdf-uploads`
   - Make it public if you want direct file access (optional)

### 4. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
python main.py
```

The backend will start on http://localhost:8001

### 5. Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will start on http://localhost:3000

## Testing the Setup

1. Open http://localhost:3000 in your browser
2. Upload a test PDF file
3. Ask a question about the uploaded document
4. Verify you get a response with confidence score

## Troubleshooting

### Common Issues

**Backend won't start:**

- Check Python version: `python --version`
- Verify environment variables in `.env`
- Check Supabase connection

**Frontend API errors:**

- Ensure backend is running on port 8000
- Check browser network tab for CORS issues
- Verify API URL in frontend environment

**PDF upload fails:**

- Check Supabase storage bucket exists
- Verify bucket permissions
- Check file size limits

**No embeddings generated:**

- Ensure sentence-transformers downloads models successfully
- Check available disk space
- Verify vector extension is enabled in Postgres

### Performance Notes

- First run will download the embedding model (~90MB)
- PDF processing time depends on document size
- Vector similarity search requires adequate PostgreSQL memory

## Development

### Adding New Features

1. Backend changes: Modify files in `/backend/`
2. Frontend changes: Modify files in `/frontend/src/`
3. Database changes: Update SQL in setup guide and migration scripts

### Testing

```bash
# Backend tests (if implemented)
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

## Production Deployment

For production deployment, consider:

1. Use environment-specific `.env` files
2. Configure proper CORS origins
3. Set up SSL/HTTPS
4. Use production-grade ASGI server (gunicorn + uvicorn)
5. Configure PostgreSQL for production workload
6. Set up monitoring and logging
7. Implement proper error handling and rate limiting
