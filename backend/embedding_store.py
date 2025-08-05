import os
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
from database import Database

class EmbeddingStore:
    def __init__(self):
        # Use a good general-purpose embedding model
        self.model_name = "all-MiniLM-L6-v2"  # 384 dimensions, fast and good quality
        self.model = None
        self.db = None
        
    async def initialize(self):
        """Initialize the embedding model and database connection"""
        try:
            # Load the sentence transformer model
            self.model = SentenceTransformer(self.model_name)
            
            # Initialize database connection
            self.db = Database()
            await self.db.initialize()
            
        except Exception as e:
            raise Exception(f"Failed to initialize embedding store: {str(e)}")
    
    async def store_chunks(self, pdf_id: str, chunks: List[Dict[str, any]]):
        """Generate embeddings for chunks and store them"""
        if not self.model:
            raise Exception("Embedding model not initialized")
        
        try:
            print(f"Starting to process {len(chunks)} chunks for PDF {pdf_id}")
            successful_chunks = 0
            failed_chunks = 0
            
            for i, chunk in enumerate(chunks):
                print(f"Processing chunk {i+1}/{len(chunks)}")
                
                try:
                    # Generate embedding
                    embedding = await self._generate_embedding(chunk["text"])
                    print(f"Generated embedding for chunk {i+1}")
                    
                    # Store in database
                    await self.db.store_chunk_embedding(
                        pdf_id=pdf_id,
                        chunk_text=chunk["text"],
                        chunk_index=chunk["index"],
                        embedding=embedding.tolist()
                    )
                    print(f"Stored chunk {i+1} in database")
                    successful_chunks += 1
                    
                except Exception as chunk_error:
                    print(f"ERROR processing chunk {i+1}: {chunk_error}")
                    failed_chunks += 1
                    
                    # If too many chunks fail, abort the entire operation
                    if failed_chunks > len(chunks) * 0.1:  # More than 10% failure rate
                        raise Exception(f"Too many chunk failures ({failed_chunks}/{len(chunks)}). Aborting embedding generation.")
                    
                    continue
            
            print(f"Completed processing chunks for PDF {pdf_id}: {successful_chunks} successful, {failed_chunks} failed")
            
            # Ensure we got at least some embeddings
            if successful_chunks == 0:
                raise Exception(f"No chunks were successfully processed for PDF {pdf_id}")
                
            if failed_chunks > 0:
                print(f"WARNING: {failed_chunks} chunks failed to process for PDF {pdf_id}")
                
        except Exception as e:
            print(f"Failed to store chunks: {str(e)}")
            raise Exception(f"Failed to store chunks: {str(e)}")
    
    async def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        try:
            # Clean and prepare text
            cleaned_text = self._clean_text(text)
            
            # Generate embedding
            embedding = self.model.encode(cleaned_text, convert_to_numpy=True)
            
            return embedding
            
        except Exception as e:
            raise Exception(f"Failed to generate embedding: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """Clean text before embedding generation"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Remove very long lines of repeated characters (often formatting artifacts)
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip lines that are mostly repeated characters
            if len(line) > 50:
                unique_chars = len(set(line.replace(' ', '')))
                if unique_chars < 5:  # Too few unique characters, likely formatting
                    continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    async def search_similar_chunks(
        self, 
        query: str, 
        limit: int = 5,
        min_similarity: float = 0.1  # Lower threshold for testing
    ) -> List[Dict[str, any]]:
        """Search for chunks similar to the query"""
        try:
            print(f"Searching for query: {query}")
            
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            print(f"Generated query embedding shape: {query_embedding.shape}")
            
            # Search in database - get all chunks for now since vector search isn't working
            chunks = await self.db.get_all_chunks_with_embeddings(limit=limit * 3)
            print(f"Retrieved {len(chunks)} chunks from database")
            
            if chunks:
                print(f"Sample chunk keys: {list(chunks[0].keys())}")
                print(f"First chunk has embedding: {'embedding' in chunks[0] and chunks[0]['embedding'] is not None}")
                if chunks[0].get('embedding'):
                    print(f"First chunk embedding type: {type(chunks[0]['embedding'])}")
                    print(f"First chunk embedding length: {len(chunks[0]['embedding']) if chunks[0]['embedding'] else 'None'}")
                    if chunks[0]['embedding']:
                        print(f"First few embedding values: {chunks[0]['embedding'][:5]}")
                else:
                    print("First chunk embedding is None or empty")
            else:
                print("No chunks retrieved from database")
            
            # Calculate similarities and filter
            results = []
            for chunk in chunks:
                if "embedding" in chunk and chunk["embedding"]:
                    try:
                        # Handle embedding format - it might be stored as a string
                        embedding_data = chunk["embedding"]
                        if isinstance(embedding_data, str):
                            # Try to parse as JSON
                            import json
                            try:
                                chunk_embedding = np.array(json.loads(embedding_data))
                            except:
                                print(f"Failed to parse embedding string for chunk {chunk.get('id', 'unknown')}")
                                continue
                        else:
                            chunk_embedding = np.array(embedding_data)
                        
                        # Calculate cosine similarity
                        similarity = self._cosine_similarity(query_embedding, chunk_embedding)
                        
                        print(f"Chunk similarity: {similarity:.3f}")
                        
                        if similarity >= min_similarity:
                            results.append({
                                **chunk,
                                "similarity": float(similarity)
                            })
                    except Exception as e:
                        print(f"Error calculating similarity for chunk: {e}")
                        continue
            
            # Sort by similarity and return top results
            results.sort(key=lambda x: x["similarity"], reverse=True)
            print(f"Found {len(results)} relevant chunks")
            
            return results[:limit]
            
        except Exception as e:
            print(f"Search error: {str(e)}")
            raise Exception(f"Failed to search similar chunks: {str(e)}")
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return dot_product / (norm_a * norm_b)
            
        except Exception:
            return 0.0
    
    async def clear_all(self):
        """Clear all embeddings"""
        # This will be handled by the database clear_all_data method
        # since embeddings are stored in the database
        pass
    
    def get_embedding_info(self) -> Dict[str, any]:
        """Get information about the embedding model"""
        return {
            "model_name": self.model_name,
            "dimensions": 384,
            "max_sequence_length": 256 if self.model else None,
            "initialized": self.model is not None
        }
    
    async def test_embedding(self, text: str) -> Dict[str, any]:
        """Test embedding generation for debugging"""
        try:
            embedding = await self._generate_embedding(text)
            
            return {
                "text": text[:100] + "..." if len(text) > 100 else text,
                "embedding_shape": embedding.shape,
                "embedding_norm": float(np.linalg.norm(embedding)),
                "sample_values": embedding[:5].tolist()
            }
            
        except Exception as e:
            return {"error": str(e)}