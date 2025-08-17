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
from openai_interface import OpenAIInterface
from gemini_interface import GeminiInterface
from query_engine import QueryEngine
from database import Database

load_dotenv()

# Initialize components
db = Database()
pdf_processor = PDFProcessor()  # Will be recreated with custom settings per request
embedding_store = EmbeddingStore()
claude_interface = ClaudeInterface()
openai_gpt4_interface = OpenAIInterface(model="gpt-4")
openai_gpt35_interface = OpenAIInterface(model="gpt-3.5-turbo")
gemini_interface = GeminiInterface(model="gemini-2.5-flash")
query_engine = QueryEngine(embedding_store, claude_interface)  # Will be updated with custom settings per request

# AI interface selection helper
def get_ai_interface(model_type: str):
    """Get the appropriate AI interface based on model type"""
    if model_type == "openai-gpt4":
        return openai_gpt4_interface
    elif model_type == "openai-gpt35":
        return openai_gpt35_interface
    elif model_type == "gemini-pro":
        return gemini_interface
    else:  # Default to Claude
        return claude_interface

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
    "https://investor-qa-assistant-ncylyecsf-ray336s-projects.vercel.app",  # Production Vercel URL
    "https://investor-qa-assistant.vercel.app",  # Shorter production URL if it exists
    "https://*.vercel.app",  # Temporary: allow all Vercel apps for testing
]

# Add production frontend URL if specified
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

# Allow Vercel preview deployments
vercel_url = os.getenv("VERCEL_URL")
if vercel_url:
    allowed_origins.append(f"https://{vercel_url}")

# Debug CORS configuration
print(f"CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Investor Q&A Assistant API"}

@app.post("/upload-pdfs")
async def upload_pdfs(
    files: List[UploadFile] = File(...),
    confidential: List[bool] = Form(...),
    chunk_size: Optional[int] = Form(4000),
    chunk_overlap: Optional[int] = Form(400)
):
    """Upload multiple PDFs with confidentiality flags and chunking settings"""
    print(f"Upload request received: {len(files)} files, {len(confidential)} flags")
    print(f"Chunking settings: size={chunk_size}, overlap={chunk_overlap}")
    
    if len(files) != len(confidential):
        raise HTTPException(400, "Number of files and confidential flags must match")
    
    # Create PDF processor with custom settings
    custom_pdf_processor = PDFProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    results = []
    for i, (file, is_confidential) in enumerate(zip(files, confidential)):
        print(f"Processing file {i+1}: {file.filename}, confidential: {is_confidential}")
        try:
            # Save file to Supabase storage
            print(f"Saving file to storage...")
            file_path = await db.save_file(file, is_confidential)
            print(f"File saved to: {file_path}")
            
            # Process PDF with custom settings
            print(f"Processing PDF...")
            chunks = await custom_pdf_processor.process_pdf(file, file_path)
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
            # Temporarily skip embeddings to test upload flow
            skip_embeddings_env = os.getenv("SKIP_EMBEDDINGS", "false").lower()
            skip_embeddings = skip_embeddings_env in ["true", "1", "yes", "on"]
            print(f"SKIP_EMBEDDINGS environment variable: {os.getenv('SKIP_EMBEDDINGS')}")
            print(f"Skip embeddings resolved to: {skip_embeddings}")
            
            if not is_confidential and not skip_embeddings:
                print(f"Generating embeddings...")
                await embedding_store.store_chunks(pdf_id, chunks)
                print(f"Embeddings stored")
            else:
                if skip_embeddings:
                    print(f"Skipping embeddings (disabled for testing)")
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
async def ask_question(request: dict):
    """Process a question and return answer with confidence score"""
    try:
        user_question = request.get("question", "")
        if not user_question:
            raise HTTPException(400, "Question is required")
        
        # Get chunking settings from request (with defaults)
        chunking_settings = request.get("chunking_settings", {})
        chunk_size = chunking_settings.get("chunkSize", 4000)
        chunk_overlap = chunking_settings.get("chunkOverlap", 400) 
        max_chunks = chunking_settings.get("maxChunks", 20)
        ai_model = chunking_settings.get("aiModel", "claude")
        
        print(f"Using chunking settings: size={chunk_size}, overlap={chunk_overlap}, max={max_chunks}")
        print(f"Using AI model: {ai_model}")
        
        # Get the appropriate AI interface
        ai_interface = get_ai_interface(ai_model)
        
        # Create a temporary query engine with the selected AI interface
        temp_query_engine = QueryEngine(embedding_store, ai_interface)
        temp_query_engine.max_context_chunks = max_chunks
        
        # Get answer from query engine
        response = await temp_query_engine.answer_question(user_question)
        
        return {
            "question": user_question,
            "answer": response["answer"],
            "confidence": response["confidence"],
            "sources": response["sources"],
            "model_used": ai_model,
            "chunking_settings": {
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "max_chunks": max_chunks
            }
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

@app.get("/debug/chunks")
async def debug_chunks():
    """Debug endpoint to check what chunks are stored"""
    try:
        chunks = await db.get_all_chunks_with_embeddings(limit=50)
        
        chunk_summary = {}
        for chunk in chunks:
            filename = chunk.get('filename', 'Unknown')
            if filename not in chunk_summary:
                chunk_summary[filename] = {
                    'count': 0,
                    'has_embeddings': 0,
                    'sample_chunk_ids': []
                }
            
            chunk_summary[filename]['count'] += 1
            if chunk.get('embedding') is not None:
                chunk_summary[filename]['has_embeddings'] += 1
            
            if len(chunk_summary[filename]['sample_chunk_ids']) < 3:
                chunk_summary[filename]['sample_chunk_ids'].append(chunk.get('id'))
        
        return {
            "total_chunks": len(chunks),
            "by_file": chunk_summary,
            "raw_sample": chunks[:3] if chunks else []
        }
        
    except Exception as e:
        raise HTTPException(500, f"Error retrieving chunks: {str(e)}")

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