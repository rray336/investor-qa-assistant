import os
import asyncio
from typing import List, Dict, Optional
import google.generativeai as genai

class GeminiInterface:
    def __init__(self, model: str = "gemini-2.5-flash"):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None
        self.model = model
        
    async def initialize(self):
        """Initialize Gemini client"""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be set in environment variables")
        
        # Configure Gemini API
        genai.configure(api_key=self.api_key)
        
        # Initialize the model with safety settings for financial content
        generation_config = {
            "temperature": 0.1,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 1000,
        }
        
        # Safety settings for financial content
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        self.client = genai.GenerativeModel(
            model_name=self.model,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
    
    async def generate_answer(
        self, 
        question: str, 
        context_chunks: List[Dict[str, any]],
        max_tokens: int = 1000
    ) -> Dict[str, any]:
        """Generate answer using Gemini with context chunks"""
        if not self.client:
            await self.initialize()
        
        try:
            # Build the prompt
            prompt = self._build_prompt(question, context_chunks)
            
            # Update generation config for this request
            generation_config = {
                "temperature": 0.1,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": max_tokens,
            }
            
            # Call Gemini API - run in executor to make it truly async
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.client.generate_content(
                    prompt,
                    generation_config=generation_config
                )
            )
            
            # Parse response
            answer_text = response.text
            parsed_response = self._parse_response(answer_text)
            
            return {
                "answer": parsed_response["answer"],
                "confidence": parsed_response["confidence"],
                "reasoning": parsed_response.get("reasoning", ""),
                "sources_used": len(context_chunks)
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate answer: {str(e)}")
    
    def _build_prompt(self, question: str, context_chunks: List[Dict[str, any]]) -> str:
        """Build the prompt for Gemini with context and question"""
        
        # Build context section
        context_text = ""
        if context_chunks:
            context_text = "CONTEXT FROM DOCUMENTS:\n\n"
            for i, chunk in enumerate(context_chunks, 1):
                filename = chunk.get("filename", "Unknown document")
                chunk_text = chunk.get("chunk_text", chunk.get("text", ""))
                similarity = chunk.get("similarity", 0)
                
                context_text += f"Document {i} ({filename}, relevance: {similarity:.2f}):\n"
                context_text += f"{chunk_text}\n\n"
        else:
            context_text = "CONTEXT: No relevant documents found.\n\n"
        
        # Build the main prompt
        prompt = f"""You are a professional corporate investor relations assistant. Your role is to provide accurate, concise, and professional responses to investor questions based solely on the provided context.

{context_text}

QUESTION: {question}

Please provide your response in the following format:

ANSWER:
[Provide a clear, professional answer. Base your answer ONLY on the provided context. If the context doesn't contain relevant information, clearly state this.]

CONFIDENCE: [Provide a confidence score from 0-100 based on how well the context supports your answer]

REASONING: [Briefly explain your confidence score - what information was available/missing that influenced your confidence level]

Guidelines:
- Use only the information provided in the context
- Be professional and concise
- If information is missing or unclear, acknowledge this
- Provide specific references to document sources when possible
- Maintain a corporate/investor relations tone"""

        return prompt
    
    def _parse_response(self, response_text: str) -> Dict[str, any]:
        """Parse Gemini's response to extract answer, confidence, and reasoning"""
        try:
            # Initialize with defaults
            parsed = {
                "answer": "",
                "confidence": 50,
                "reasoning": ""
            }
            
            # Split response by sections
            sections = response_text.split("\n")
            current_section = None
            
            for line in sections:
                line = line.strip()
                
                if line.startswith("ANSWER:"):
                    current_section = "answer"
                    # Get content after "ANSWER:"
                    content = line.replace("ANSWER:", "").strip()
                    if content:
                        parsed["answer"] = content
                elif line.startswith("CONFIDENCE:"):
                    current_section = "confidence"
                    # Extract confidence score
                    confidence_text = line.replace("CONFIDENCE:", "").strip()
                    parsed["confidence"] = self._extract_confidence_score(confidence_text)
                elif line.startswith("REASONING:"):
                    current_section = "reasoning"
                    content = line.replace("REASONING:", "").strip()
                    if content:
                        parsed["reasoning"] = content
                elif line and current_section:
                    # Continue building the current section
                    if current_section == "answer":
                        if parsed["answer"]:
                            parsed["answer"] += "\n" + line
                        else:
                            parsed["answer"] = line
                    elif current_section == "reasoning":
                        if parsed["reasoning"]:
                            parsed["reasoning"] += " " + line
                        else:
                            parsed["reasoning"] = line
            
            # Clean up the answer
            parsed["answer"] = self._clean_answer_text(parsed["answer"])
            
            # Ensure we have some answer
            if not parsed["answer"]:
                parsed["answer"] = response_text  # Fallback to full response
            
            return parsed
            
        except Exception as e:
            # Fallback parsing
            return {
                "answer": response_text,
                "confidence": 50,
                "reasoning": f"Error parsing response: {str(e)}"
            }
    
    def _extract_confidence_score(self, confidence_text: str) -> int:
        """Extract numeric confidence score from text"""
        try:
            # Look for numbers in the text
            import re
            numbers = re.findall(r'\d+', confidence_text)
            
            if numbers:
                score = int(numbers[0])
                # Ensure score is between 0 and 100
                return max(0, min(100, score))
            
            # Fallback based on keywords
            confidence_text_lower = confidence_text.lower()
            if any(word in confidence_text_lower for word in ["high", "very confident", "certain"]):
                return 85
            elif any(word in confidence_text_lower for word in ["medium", "moderate", "somewhat"]):
                return 65
            elif any(word in confidence_text_lower for word in ["low", "uncertain", "unclear"]):
                return 35
            
            return 50  # Default
            
        except Exception:
            return 50
    
    def _clean_answer_text(self, answer: str) -> str:
        """Clean and format the answer text"""
        if not answer:
            return ""
        
        # Remove extra whitespace
        answer = "\n".join(line.strip() for line in answer.split("\n") if line.strip())
        
        # Do not enforce bullet points, just return cleaned text
        return answer
    
    async def test_connection(self) -> Dict[str, any]:
        """Test the Gemini API connection"""
        try:
            if not self.client:
                await self.initialize()
            
            # Simple test message
            test_prompt = "Please respond with 'Connection successful' to test the API."
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.generate_content(
                    test_prompt,
                    generation_config={"max_output_tokens": 50}
                )
            )
            
            return {
                "status": "success",
                "model": self.model,
                "response": response.text
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
