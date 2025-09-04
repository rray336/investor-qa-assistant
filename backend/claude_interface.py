import os
from typing import List, Dict, Optional
import anthropic
from anthropic import Anthropic

class ClaudeInterface:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        self.model = "claude-3-5-sonnet-latest"  # Use latest Claude 3.5 Sonnet
        
    async def initialize(self):
        """Initialize Claude client"""
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set in environment variables")
        
        self.client = Anthropic(api_key=self.api_key)
    
    async def generate_answer(
        self, 
        question: str, 
        context_chunks: List[Dict[str, any]],
        max_tokens: int = 1000
    ) -> Dict[str, any]:
        """Generate answer using Claude with context chunks"""
        if not self.client:
            await self.initialize()
        
        try:
            # Build the prompt
            prompt = self._build_prompt(question, context_chunks)
            
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.1,  # Low temperature for consistent, factual responses
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse response
            answer_text = response.content[0].text
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
        """Build the prompt for Claude with context and question"""
        
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
        prompt = f"""{context_text}

QUESTION: {question}

Please provide your response in the following format:

ANSWER:
[Your answer here]

CONFIDENCE: [Provide a confidence score from 0-100]

REASONING: [Briefly explain your confidence score]

Guidelines:
- Use only the information provided in the context
- Do only light clean up of the language for clarity"""

        return prompt
    
    def _parse_response(self, response_text: str) -> Dict[str, any]:
        """Parse Claude's response to extract answer, confidence, and reasoning"""
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
        """Test the Claude API connection"""
        try:
            if not self.client:
                await self.initialize()
            
            # Simple test message
            response = self.client.messages.create(
                model=self.model,
                max_tokens=50,
                messages=[
                    {
                        "role": "user",
                        "content": "Please respond with 'Connection successful' to test the API."
                    }
                ]
            )
            
            return {
                "status": "success",
                "model": self.model,
                "response": response.content[0].text
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
