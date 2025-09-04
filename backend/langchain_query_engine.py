import base64
import io
import os
from typing import List, Dict, Optional
from pathlib import Path
from database import Database
from claude_interface import ClaudeInterface
from openai_interface import OpenAIInterface
from gemini_interface import GeminiInterface

# LangChain imports
from langchain.chat_models import init_chat_model

class LangchainQueryEngine:
    def __init__(self, database: Database):
        self.database = database
        # Initialize AI interfaces for response parsing
        self.claude_interface = ClaudeInterface()
        self.openai_interface = OpenAIInterface()
        self.gemini_interface = GeminiInterface()
        
        # Initialize LangChain models
        self.langchain_models = {}
    
    def _get_langchain_model(self, ai_model: str):
        """Get or create LangChain model instance"""
        if ai_model not in self.langchain_models:
            try:
                if ai_model == 'claude':
                    # Initialize Claude model via LangChain
                    self.langchain_models[ai_model] = init_chat_model(
                        "claude-3-5-sonnet-latest", 
                        model_provider="anthropic",
                        api_key=os.getenv("ANTHROPIC_API_KEY")
                    )
                elif ai_model.startswith('openai'):
                    # Map our model names to OpenAI model names
                    model_map = {
                        'openai-gpt4': 'gpt-4',
                        'openai-gpt35': 'gpt-3.5-turbo'
                    }
                    openai_model = model_map.get(ai_model, 'gpt-4')
                    self.langchain_models[ai_model] = init_chat_model(
                        openai_model,
                        model_provider="openai",
                        api_key=os.getenv("OPENAI_API_KEY")
                    )
                elif ai_model == 'gemini-pro':
                    # Initialize Gemini model via LangChain
                    self.langchain_models[ai_model] = init_chat_model(
                        "gemini-2.5-flash",
                        model_provider="google",
                        api_key=os.getenv("GEMINI_API_KEY")
                    )
                else:
                    # Fallback to Claude
                    self.langchain_models[ai_model] = init_chat_model(
                        "claude-3-5-sonnet-latest",
                        model_provider="anthropic", 
                        api_key=os.getenv("ANTHROPIC_API_KEY")
                    )
            except Exception as e:
                print(f"Failed to initialize LangChain model {ai_model}: {e}")
                # Fallback to Claude
                self.langchain_models[ai_model] = init_chat_model(
                    "claude-3-5-sonnet-latest",
                    model_provider="anthropic",
                    api_key=os.getenv("ANTHROPIC_API_KEY")
                )
        
        return self.langchain_models[ai_model]
        
    async def answer_question(self, question: str, ai_model: str = 'claude') -> Dict[str, any]:
        """Process a question using direct PDF analysis with LangChain approach"""
        try:
            print(f"Processing question with LangChain method using {ai_model}")
            
            # Step 1: Get all PDF files from database
            pdf_files = await self.database.get_pdf_files_for_query()
            
            if not pdf_files:
                return {
                    "answer": "No PDF files found in the database for analysis.",
                    "confidence": 0,
                    "reasoning": "No documents available",
                    "sources": [],
                    "chunks_found": 0,
                    "question": question,
                    "processing_method": "langchain",
                    "pdfs_processed": 0
                }
            
            print(f"Found {len(pdf_files)} PDFs to process")
            
            # Step 2: Process each PDF individually
            pdf_responses = []
            processed_count = 0
            
            for pdf_info in pdf_files:
                try:
                    # Download PDF from Supabase storage
                    pdf_content = await self._download_pdf_from_storage(pdf_info['file_path'])
                    
                    # Convert to base64
                    pdf_base64 = base64.b64encode(pdf_content).decode("utf-8")
                    
                    # Create message format exactly like Langchain_reader.md
                    message = {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": self._create_prompt(question),
                            },
                            {
                                "type": "file",
                                "source_type": "base64",
                                "data": pdf_base64,
                                "mime_type": "application/pdf",
                                "filename": pdf_info['filename'],
                            },
                        ],
                    }
                    
                    # Send to appropriate AI model
                    response = await self._send_to_ai_model(message, ai_model)
                    
                    pdf_responses.append({
                        "filename": pdf_info['filename'],
                        "response": response,
                        "pdf_id": pdf_info['id']
                    })
                    
                    processed_count += 1
                    print(f"Processed PDF {processed_count}/{len(pdf_files)}: {pdf_info['filename']}")
                    
                except Exception as pdf_error:
                    print(f"Error processing PDF {pdf_info['filename']}: {pdf_error}")
                    # Continue with other PDFs
                    continue
            
            if not pdf_responses:
                return {
                    "answer": "Failed to process any PDF files. Please check the files and try again.",
                    "confidence": 0,
                    "reasoning": "All PDF processing failed",
                    "sources": [],
                    "chunks_found": 0,
                    "question": question,
                    "processing_method": "langchain",
                    "pdfs_processed": 0
                }
            
            # Step 3: Consolidate responses
            consolidated_response = await self._consolidate_responses(question, pdf_responses, ai_model)
            
            return {
                "answer": consolidated_response["answer"],
                "confidence": consolidated_response["confidence"],
                "reasoning": consolidated_response.get("reasoning", f"Analyzed {processed_count} PDF(s) using direct PDF processing"),
                "sources": self._build_source_info(pdf_responses),
                "chunks_found": processed_count,  # Use PDF count instead of chunks
                "question": question,
                "processing_method": "langchain",
                "pdfs_processed": processed_count
            }
            
        except Exception as e:
            print(f"LangChain query processing error: {str(e)}")
            return {
                "answer": f"I apologize, but I encountered an error processing your question with LangChain: {str(e)}",
                "confidence": 0,
                "reasoning": "LangChain processing error occurred",
                "sources": [],
                "chunks_found": 0,
                "question": question,
                "processing_method": "langchain",
                "pdfs_processed": 0
            }
    
    def _create_prompt(self, question: str) -> str:
        """Create a prompt for direct PDF analysis using current format"""
        return f"""CONTEXT FROM DOCUMENT:

The PDF document is provided for analysis. Please review the entire document content to answer the question.

QUESTION: {question}

Please provide your response in the following format:

ANSWER:
[Your answer here]

CONFIDENCE: [Provide a confidence score from 0-100]

REASONING: [Briefly explain your confidence score]

Guidelines:
- Use only the information provided in the context
- Do only light clean up of the language for clarity"""
    
    async def _download_pdf_from_storage(self, file_path: str) -> bytes:
        """Download PDF file from Supabase storage"""
        try:
            # Use Supabase client to download file
            response = self.database.client.storage.from_("pdf-uploads").download(file_path)
            
            if hasattr(response, 'error') and response.error:
                raise Exception(f"Storage download failed: {response.error}")
            
            # Handle different response formats
            if hasattr(response, 'data') and response.data:
                return response.data
            elif isinstance(response, bytes):
                return response
            else:
                raise Exception("Unexpected response format from storage")
                
        except Exception as e:
            raise Exception(f"Failed to download PDF from storage: {str(e)}")
    
    async def _send_to_ai_model(self, message: Dict, ai_model: str) -> Dict[str, any]:
        """Send message with PDF to AI model using LangChain"""
        try:
            # Get LangChain model instance
            llm_model = self._get_langchain_model(ai_model)
            
            # Use LangChain invoke method - exactly like Langchain_reader.md
            response = llm_model.invoke([message])
            
            # Extract response text - handle different response formats
            if hasattr(response, 'content'):
                response_text = response.content
            elif hasattr(response, 'text'):
                response_text = response.text
            elif isinstance(response, str):
                response_text = response
            else:
                response_text = str(response)
            
            print(f"LangChain response: {response_text[:200]}...")  # Debug log
            
            # Parse the response using appropriate interface parsing method
            if ai_model == 'claude':
                parsed_response = self.claude_interface._parse_response(response_text)
            elif ai_model.startswith('openai'):
                parsed_response = self.openai_interface._parse_response(response_text)
            elif ai_model == 'gemini-pro':
                parsed_response = self.gemini_interface._parse_response(response_text)
            else:
                # Fallback to Claude parsing
                parsed_response = self.claude_interface._parse_response(response_text)
            
            return {
                "answer": parsed_response["answer"],
                "confidence": parsed_response["confidence"],
                "reasoning": parsed_response.get("reasoning", ""),
                "sources_used": 1  # Full PDF
            }
                
        except Exception as e:
            print(f"LangChain processing error: {str(e)}")
            raise Exception(f"LangChain model processing failed: {str(e)}")
    
    async def _consolidate_responses(self, question: str, pdf_responses: List[Dict], ai_model: str) -> Dict[str, any]:
        """Consolidate multiple PDF responses into a single answer"""
        try:
            # Create a consolidation prompt
            responses_text = "\n\n".join([
                f"=== {response['filename']} ===\n{response['response'].get('answer', str(response['response']))}"
                for response in pdf_responses
            ])
            
            consolidation_prompt = f"""
Based on the following responses from multiple PDF documents, please provide a comprehensive, consolidated answer to the question: "{question}"

Individual PDF Responses:
{responses_text}

Please synthesize the information and provide:
1. A comprehensive answer that combines insights from all documents
2. Note any conflicting information between documents
3. Highlight the most important points
4. Maintain a professional investor relations tone

Consolidated Answer:
"""
            
            # Use the selected AI model for consolidation
            if ai_model == 'claude':
                ai_interface = self.claude_interface
            elif ai_model.startswith('openai'):
                ai_interface = self.openai_interface
            elif ai_model == 'gemini-pro':
                ai_interface = self.gemini_interface
            else:
                ai_interface = self.claude_interface  # Default fallback
            
            # Generate consolidated response using existing AI interface
            response = await ai_interface.generate_answer(
                question=consolidation_prompt,
                context_chunks=[]  # No chunks needed for consolidation
            )
            
            return {
                "answer": response.get("answer", "Unable to consolidate responses"),
                "confidence": min(85, response.get("confidence", 70)),  # Slightly lower confidence for consolidated
                "reasoning": f"Consolidated analysis from {len(pdf_responses)} PDF documents"
            }
            
        except Exception as e:
            # Fallback: just combine responses without AI consolidation
            combined_answer = "\n\n".join([
                f"**From {response['filename']}:**\n{response['response'].get('answer', str(response['response']))}"
                for response in pdf_responses
            ])
            
            return {
                "answer": combined_answer,
                "confidence": 70,
                "reasoning": f"Combined responses from {len(pdf_responses)} PDF documents (consolidation failed)"
            }
    
    def _build_source_info(self, pdf_responses: List[Dict]) -> List[Dict[str, any]]:
        """Build source information for the response"""
        sources = []
        
        for response in pdf_responses:
            response_text = response['response'].get('answer', str(response['response'])) if isinstance(response['response'], dict) else str(response['response'])
            source = {
                "filename": response["filename"],
                "chunk_index": 0,  # Not applicable for full PDF processing
                "relevance_score": 100.0,  # Full PDF is 100% relevant
                "preview": f"Full PDF analysis: {response_text[:150]}..."
            }
            sources.append(source)
        
        return sources
    
    def get_stats(self) -> Dict[str, any]:
        """Get LangChain query engine statistics"""
        return {
            "processing_method": "langchain",
            "description": "Direct PDF analysis without chunking",
            "supported_models": ["claude", "openai-gpt4", "openai-gpt35", "gemini-pro"]
        }