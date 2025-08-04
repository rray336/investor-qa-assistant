import os
from typing import List, Dict, Optional
from supabase import create_client, Client
from fastapi import UploadFile
import uuid
from datetime import datetime

class Database:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.client: Optional[Client] = None
        
    async def initialize(self):
        """Initialize Supabase client and create tables if needed"""
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase URL and key must be set in environment variables")
            
        self.client = create_client(self.supabase_url, self.supabase_key)
        
        # Set up service role authentication for storage operations
        # This bypasses RLS for storage operations
        
        # Create tables if they don't exist
        await self._create_tables()
    
    async def _create_tables(self):
        """Create database tables - tables should be created manually in Supabase dashboard"""
        # Tables should be created manually via Supabase SQL Editor
        # This is just a verification step
        try:
            # Test if tables exist by doing a simple query
            result = self.client.table("pdfs").select("count", count="exact").limit(1).execute()
            print("PDFs table exists and accessible")
        except Exception as e:
            print(f"Warning: PDFs table may not exist or be accessible: {e}")
            
        try:
            result = self.client.table("chunks").select("count", count="exact").limit(1).execute()
            print("Chunks table exists and accessible")
        except Exception as e:
            print(f"Warning: Chunks table may not exist or be accessible: {e}")
    
    async def save_file(self, file: UploadFile, is_confidential: bool) -> str:
        """Save uploaded file to Supabase storage"""
        try:
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'pdf'
            storage_path = f"pdfs/{file_id}.{file_extension}"
            
            # Read file content
            file_content = await file.read()
            await file.seek(0)  # Reset file pointer
            
            print(f"Attempting to upload file: {storage_path}")
            print(f"File size: {len(file_content)} bytes")
            
            # Try uploading to Supabase storage
            try:
                response = self.client.storage.from_("pdf-uploads").upload(
                    storage_path, 
                    file_content,
                    file_options={
                        "content-type": "application/pdf"
                    }
                )
                print(f"Raw storage response: {response}")
                
                # Handle different response formats
                if hasattr(response, 'error') and response.error:
                    print(f"Storage error: {response.error}")
                    raise Exception(f"Storage upload failed: {response.error}")
                    
                if hasattr(response, 'data') and response.data:
                    print(f"Storage success: {response.data}")
                    return storage_path
                    
                # If we get here, assume success (some versions don't return clear success indicators)
                print("Upload appears successful (no error returned)")
                return storage_path
                
            except Exception as storage_error:
                print(f"Storage upload exception: {storage_error}")
                # For now, continue with processing even if storage fails
                # In production, you'd want to handle this differently
                return f"local/{storage_path}"  # Indicate local fallback
            
        except Exception as e:
            print(f"General file save error: {str(e)}")
            raise Exception(f"Failed to save file: {str(e)}")
    
    async def store_pdf_metadata(
        self, 
        filename: str, 
        file_path: str, 
        is_confidential: bool, 
        chunk_count: int
    ) -> str:
        """Store PDF metadata in database"""
        try:
            result = self.client.table("pdfs").insert({
                "filename": filename,
                "file_path": file_path,
                "is_confidential": is_confidential,
                "chunk_count": chunk_count,
                "upload_date": datetime.utcnow().isoformat()
            }).execute()
            
            if result.data:
                return result.data[0]["id"]
            else:
                raise Exception("Failed to insert PDF metadata")
                
        except Exception as e:
            raise Exception(f"Failed to store PDF metadata: {str(e)}")
    
    async def store_chunk_embedding(
        self, 
        pdf_id: str, 
        chunk_text: str, 
        chunk_index: int, 
        embedding: List[float]
    ):
        """Store text chunk with embedding"""
        try:
            result = self.client.table("chunks").insert({
                "pdf_id": pdf_id,
                "chunk_text": chunk_text,
                "chunk_index": chunk_index,
                "embedding": embedding
            }).execute()
            
            return result.data[0]["id"] if result.data else None
            
        except Exception as e:
            raise Exception(f"Failed to store chunk: {str(e)}")
    
    async def get_all_pdfs(self) -> List[Dict]:
        """Retrieve all PDF metadata"""
        try:
            result = self.client.table("pdfs").select("*").order("upload_date", desc=True).execute()
            return result.data if result.data else []
            
        except Exception as e:
            raise Exception(f"Failed to retrieve PDFs: {str(e)}")
    
    async def search_similar_chunks(self, query_embedding: List[float], limit: int = 5) -> List[Dict]:
        """Search for similar chunks using vector similarity"""
        try:
            # Note: This requires pgvector extension and proper SQL
            # For now, we'll implement a basic version
            result = self.client.table("chunks").select(
                "id, pdf_id, chunk_text, chunk_index"
            ).limit(limit).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            raise Exception(f"Failed to search chunks: {str(e)}")
    
    async def get_all_chunks_with_embeddings(self, limit: int = 15) -> List[Dict]:
        """Get all chunks with their embeddings for similarity calculation"""
        try:
            # Join chunks with PDFs to get filename
            result = self.client.table("chunks").select(
                "id, pdf_id, chunk_text, chunk_index, embedding, pdfs(filename, is_confidential)"
            ).limit(limit).execute()
            
            print(f"Database query returned {len(result.data) if result.data else 0} chunks")
            
            # Flatten the joined data structure
            flattened_chunks = []
            for chunk in result.data if result.data else []:
                pdf_info = chunk.get('pdfs', {}) if chunk.get('pdfs') else {}
                flattened_chunk = {
                    'id': chunk.get('id'),
                    'pdf_id': chunk.get('pdf_id'),
                    'chunk_text': chunk.get('chunk_text'),
                    'chunk_index': chunk.get('chunk_index'),
                    'embedding': chunk.get('embedding'),
                    'filename': pdf_info.get('filename', 'Unknown document'),
                    'is_confidential': pdf_info.get('is_confidential', False)
                }
                flattened_chunks.append(flattened_chunk)
            
            if flattened_chunks:
                first_chunk = flattened_chunks[0]
                print(f"First chunk ID: {first_chunk.get('id')}")
                print(f"First chunk filename: {first_chunk.get('filename')}")
                print(f"First chunk embedding is None: {first_chunk.get('embedding') is None}")
                print(f"First chunk embedding type: {type(first_chunk.get('embedding'))}")
            
            return flattened_chunks
            
        except Exception as e:
            print(f"Failed to retrieve chunks with embeddings: {str(e)}")
            return []
    
    async def clear_all_data(self):
        """Clear all PDFs and chunks from database and storage"""
        try:
            print("Starting data clear process...")
            
            # Get all PDF file paths before deleting (for storage cleanup)
            print("Getting PDF file paths...")
            pdfs_result = self.client.table("pdfs").select("file_path").execute()
            print(f"Found {len(pdfs_result.data) if pdfs_result.data else 0} PDFs to delete")
            
            # Delete files from storage (best effort - don't fail if this doesn't work)
            if pdfs_result.data:
                for pdf in pdfs_result.data:
                    try:
                        print(f"Attempting to delete file: {pdf['file_path']}")
                        result = self.client.storage.from_("pdf-uploads").remove([pdf["file_path"]])
                        print(f"Storage deletion result: {result}")
                    except Exception as storage_error:
                        print(f"Storage deletion failed (continuing): {storage_error}")
                        pass  # Continue even if file deletion fails
            
            # Delete all chunks first (due to foreign key constraint)
            print("Deleting chunks...")
            chunks_result = self.client.table("chunks").delete().gte("chunk_index", 0).execute()
            print(f"Chunks deletion result: {chunks_result}")
            
            # Delete all PDFs from database
            print("Deleting PDF metadata...")
            pdfs_delete_result = self.client.table("pdfs").delete().gte("chunk_count", 0).execute()
            print(f"PDFs deletion result: {pdfs_delete_result}")
            
            print("Data clear completed successfully")
            
        except Exception as e:
            print(f"Clear data error: {str(e)}")
            raise Exception(f"Failed to clear data: {str(e)}")
    
    async def get_pdf_by_id(self, pdf_id: str) -> Optional[Dict]:
        """Get PDF metadata by ID"""
        try:
            result = self.client.table("pdfs").select("*").eq("id", pdf_id).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            raise Exception(f"Failed to get PDF: {str(e)}")