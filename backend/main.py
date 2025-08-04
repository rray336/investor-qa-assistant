from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from pdf_processor import PDFProcessor
from embedding_store import EmbeddingStore
from claude_interface import ClaudeInterface
from query_engine import QueryEngine
from database import Database

load_dotenv()

# Initialize components
db = Database()
pdf_processor = PDFProcessor()
embedding_store = EmbeddingStore()
claude_interface = ClaudeInterface()
query_engine = QueryEngine(embedding_store, claude_interface)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and services on startup"""
    try:
        print("Initializing database...")
        await db.initialize()
        print("Initializing embedding store...")
        await embedding_store.initialize()
        print("Initialization complete!")
    except Exception as e:
        print(f"Initialization error: {e}")
        # Continue anyway for debugging
    yield

app = FastAPI(title="Investor Q&A Assistant", version="1.0.0", lifespan=lifespan)

# CORS middleware for React frontend
# Get allowed origins from environment variable for production
allowed_origins = [
    "http://localhost:3000",  # Local development
    "http://localhost:3001",  # Alternative local port
]

# Add production frontend URL if specified
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

# Allow Vercel preview deployments
vercel_url = os.getenv("VERCEL_URL")
if vercel_url:
    allowed_origins.extend([
        f"https://{vercel_url}",
        f"https://*.vercel.app"
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Investor Q&A Assistant API"}

@app.post("/upload-pdfs")
async def upload_pdfs(
    files: List[UploadFile] = File(...),
    confidential: List[bool] = Form(...)
):
    """Upload multiple PDFs with confidentiality flags"""
    print(f"Upload request received: {len(files)} files, {len(confidential)} flags")
    
    if len(files) != len(confidential):
        raise HTTPException(400, "Number of files and confidential flags must match")
    
    results = []
    for i, (file, is_confidential) in enumerate(zip(files, confidential)):
        print(f"Processing file {i+1}: {file.filename}, confidential: {is_confidential}")
        try:
            # Save file to Supabase storage
            print(f"Saving file to storage...")
            file_path = await db.save_file(file, is_confidential)
            print(f"File saved to: {file_path}")
            
            # Process PDF
            print(f"Processing PDF...")
            chunks = await pdf_processor.process_pdf(file, file_path)
            print(f"PDF processed into {len(chunks)} chunks")
            
            # Store metadata
            print(f"Storing metadata...")
            pdf_id = await db.store_pdf_metadata(
                filename=file.filename,
                file_path=file_path,
                is_confidential=is_confidential,
                chunk_count=len(chunks)
            )
            print(f"Metadata stored with ID: {pdf_id}")
            
            # Generate and store embeddings (only for non-confidential)
            if not is_confidential:
                print(f"Generating embeddings...")
                await embedding_store.store_chunks(pdf_id, chunks)
                print(f"Embeddings stored")
            else:
                print(f"Skipping embeddings (confidential file)")
            
            results.append({
                "filename": file.filename,
                "pdf_id": pdf_id,
                "chunks": len(chunks),
                "confidential": is_confidential,
                "status": "success"
            })
            print(f"File {file.filename} processed successfully")
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error processing file {file.filename}: {error_msg}")
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": error_msg
            })
    
    print(f"Upload completed: {results}")
    return {"results": results}

@app.post("/ask-question")
async def ask_question(question: dict):
    """Process a question and return answer with confidence score"""
    try:
        user_question = question.get("question", "")
        if not user_question:
            raise HTTPException(400, "Question is required")
        
        # Get answer from query engine
        response = await query_engine.answer_question(user_question)
        
        return {
            "question": user_question,
            "answer": response["answer"],
            "confidence": response["confidence"],
            "sources": response["sources"]
        }
        
    except Exception as e:
        raise HTTPException(500, f"Error processing question: {str(e)}")

@app.get("/pdfs")
async def list_pdfs():
    """Get list of uploaded PDFs with metadata"""
    try:
        pdfs = await db.get_all_pdfs()
        return {"pdfs": pdfs}
    except Exception as e:
        raise HTTPException(500, f"Error retrieving PDFs: {str(e)}")

@app.delete("/clear-all")
async def clear_all_data():
    """Clear all PDFs, embeddings, and metadata"""
    try:
        # Clear embeddings
        await embedding_store.clear_all()
        
        # Clear database
        await db.clear_all_data()
        
        return {"message": "All data cleared successfully"}
        
    except Exception as e:
        raise HTTPException(500, f"Error clearing data: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable (Railway sets PORT automatically)
    port = int(os.getenv("PORT", 8001))
    
    # Development vs Production settings
    is_production = os.getenv("RAILWAY_ENVIRONMENT") == "production" or os.getenv("ENV") == "production"
    
    if is_production:
        # Production configuration
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port,
            log_level="info"
        )
    else:
        # Development configuration with reload
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port,
            reload=True,
            log_level="debug"
        )