from typing import List, Dict, Optional
from embedding_store import EmbeddingStore
from claude_interface import ClaudeInterface

class QueryEngine:
    def __init__(self, embedding_store: EmbeddingStore, ai_interface):
        self.embedding_store = embedding_store
        self.ai_interface = ai_interface  # Can be any AI interface (Claude, OpenAI, etc.)
        self.max_context_chunks = 10 # Increase from 5 to 10
        self.min_similarity_threshold = 0.1 # Lower from 0.3 to 0.1
        
    async def answer_question(self, question: str) -> Dict[str, any]:
        """Process a question and return an answer with supporting information"""
        try:
            # Step 1: Retrieve relevant chunks
            relevant_chunks = await self._retrieve_relevant_chunks(question)
            
            # Step 2: Generate answer using selected AI interface
            response = await self.ai_interface.generate_answer(
                question=question,
                context_chunks=relevant_chunks
            )
            
            # Step 3: Build final response with metadata
            return {
                "answer": response["answer"],
                "confidence": response["confidence"],
                "reasoning": response.get("reasoning", ""),
                "sources": self._build_source_info(relevant_chunks),
                "chunks_found": len(relevant_chunks),
                "question": question
            }
            
        except Exception as e:
            return {
                "answer": f"I apologize, but I encountered an error processing your question: {str(e)}",
                "confidence": 0,
                "reasoning": "Error occurred during processing",
                "sources": [],
                "chunks_found": 0,
                "question": question
            }
    
    async def _retrieve_relevant_chunks(self, question: str) -> List[Dict[str, any]]:
        """Retrieve chunks most relevant to the question"""
        try:
            # Search for similar chunks
            chunks = await self.embedding_store.search_similar_chunks(
                query=question,
                limit=self.max_context_chunks,
                min_similarity=self.min_similarity_threshold
            )
            
            # Enhance chunks with additional metadata if needed
            enhanced_chunks = []
            for chunk in chunks:
                enhanced_chunk = {
                    **chunk,
                    "relevance_score": chunk.get("similarity", 0.0)
                }
                enhanced_chunks.append(enhanced_chunk)
            
            return enhanced_chunks
            
        except Exception as e:
            print(f"Error retrieving chunks: {str(e)}")
            return []
    
    def _build_source_info(self, chunks: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """Build source information for the response"""
        sources = []
        
        for chunk in chunks:
            source = {
                "filename": chunk.get("filename", "Unknown document"),
                "chunk_index": chunk.get("chunk_index", 0),
                "relevance_score": round(chunk.get("similarity", 0.0) * 100, 1),  # Convert to percentage
                "preview": self._get_chunk_preview(chunk.get("chunk_text", ""))
            }
            sources.append(source)
        
        return sources
    
    def _get_chunk_preview(self, text: str, max_length: int = 150) -> str:
        """Get a preview of chunk text for source display"""
        if not text:
            return ""
        
        if len(text) <= max_length:
            return text
        
        # Try to break at a sentence boundary
        truncated = text[:max_length]
        last_sentence = max(
            truncated.rfind('. '),
            truncated.rfind('! '),
            truncated.rfind('? ')
        )
        
        if last_sentence > max_length * 0.7:  # If we found a good break point
            return truncated[:last_sentence + 1] + "..."
        else:
            # Fall back to word boundary
            last_space = truncated.rfind(' ')
            if last_space > max_length * 0.8:
                return truncated[:last_space] + "..."
            else:
                return truncated + "..."
    
    async def get_query_suggestions(self, partial_question: str) -> List[str]:
        """Get query suggestions based on available content (future enhancement)"""
        # This could be enhanced to suggest questions based on document content
        suggestions = [
            "What were the key financial highlights this quarter?",
            "How did revenue compare to the previous quarter?",
            "What are the main risks mentioned in the filings?",
            "What guidance was provided for next quarter?",
            "What were the major operational changes discussed?"
        ]
        
        return suggestions[:3]  # Return top 3 suggestions
    
    async def analyze_question_complexity(self, question: str) -> Dict[str, any]:
        """Analyze question to determine processing approach"""
        question_lower = question.lower()
        
        # Simple keyword-based analysis
        financial_keywords = ["revenue", "profit", "earnings", "margin", "growth", "sales"]
        risk_keywords = ["risk", "challenge", "threat", "concern", "issue"]
        comparison_keywords = ["compare", "versus", "vs", "difference", "change"]
        
        analysis = {
            "type": "general",
            "keywords": [],
            "complexity": "medium",
            "requires_calculation": False,
            "requires_comparison": any(word in question_lower for word in comparison_keywords)
        }
        
        # Categorize question type
        if any(word in question_lower for word in financial_keywords):
            analysis["type"] = "financial"
            analysis["keywords"].extend([w for w in financial_keywords if w in question_lower])
        elif any(word in question_lower for word in risk_keywords):
            analysis["type"] = "risk"
            analysis["keywords"].extend([w for w in risk_keywords if w in question_lower])
        
        # Determine complexity
        if len(question.split()) < 10:
            analysis["complexity"] = "simple"
        elif len(question.split()) > 25:
            analysis["complexity"] = "complex"
        
        # Check for calculation needs
        calculation_indicators = ["calculate", "sum", "total", "percentage", "%", "ratio"]
        analysis["requires_calculation"] = any(word in question_lower for word in calculation_indicators)
        
        return analysis
    
    def get_stats(self) -> Dict[str, any]:
        """Get query engine statistics"""
        return {
            "max_context_chunks": self.max_context_chunks,
            "min_similarity_threshold": self.min_similarity_threshold,
            "embedding_model": self.embedding_store.model_name if hasattr(self.embedding_store, 'model_name') else "unknown",
            "claude_model": self.claude_interface.model if hasattr(self.claude_interface, 'model') else "unknown"
        }