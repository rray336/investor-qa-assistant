import PyPDF2
from typing import List, Dict
from fastapi import UploadFile
import io

class PDFProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    async def process_pdf(self, file: UploadFile, file_path: str) -> List[Dict[str, any]]:
        """Extract text from PDF and split into chunks"""
        try:
            # Read PDF content
            file_content = await file.read()
            await file.seek(0)  # Reset file pointer
            
            # Extract text using PyPDF2
            text = await self._extract_text_from_pdf(file_content)
            
            # Split into chunks
            chunks = self._split_text_into_chunks(text)
            
            # Create chunk objects with metadata
            processed_chunks = []
            for i, chunk_text in enumerate(chunks):
                processed_chunks.append({
                    "text": chunk_text,
                    "index": i,
                    "file_path": file_path,
                    "filename": file.filename
                })
            
            return processed_chunks
            
        except Exception as e:
            raise Exception(f"Failed to process PDF {file.filename}: {str(e)}")
    
    async def _extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF bytes"""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def _split_text_into_chunks(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Find end of chunk
            end = start + self.chunk_size
            
            # If we're not at the end of the text, try to break at a sentence or word boundary
            if end < len(text):
                # Look for sentence boundaries (. ! ?)
                sentence_end = self._find_sentence_boundary(text, start, end)
                if sentence_end > start:
                    end = sentence_end
                else:
                    # Fall back to word boundary
                    word_end = self._find_word_boundary(text, start, end)
                    if word_end > start:
                        end = word_end
            
            # Extract chunk
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move to next chunk with overlap
            start = max(start + 1, end - self.chunk_overlap)
            
            # Prevent infinite loop
            if start >= len(text):
                break
        
        return chunks
    
    def _find_sentence_boundary(self, text: str, start: int, end: int) -> int:
        """Find the last sentence boundary before the end position"""
        sentence_endings = ['. ', '! ', '? ', '.\n', '!\n', '?\n']
        
        best_pos = start
        search_start = max(start, end - 200)  # Look back up to 200 chars
        
        for ending in sentence_endings:
            pos = text.rfind(ending, search_start, end)
            if pos > best_pos:
                best_pos = pos + len(ending)
        
        return best_pos if best_pos > start else end
    
    def _find_word_boundary(self, text: str, start: int, end: int) -> int:
        """Find the last word boundary before the end position"""
        # Look for whitespace
        search_start = max(start, end - 100)  # Look back up to 100 chars
        pos = text.rfind(' ', search_start, end)
        
        return pos + 1 if pos > start else end
    
    def get_chunk_preview(self, chunk: Dict[str, any], max_length: int = 100) -> str:
        """Get a preview of a chunk for display purposes"""
        text = chunk.get("text", "")
        if len(text) <= max_length:
            return text
        
        return text[:max_length] + "..."
    
    def validate_pdf(self, file: UploadFile) -> bool:
        """Validate that the uploaded file is a PDF"""
        if not file.filename:
            return False
        
        # Check file extension
        if not file.filename.lower().endswith('.pdf'):
            return False
        
        # Check MIME type
        if file.content_type and not file.content_type.startswith('application/pdf'):
            return False
        
        return True