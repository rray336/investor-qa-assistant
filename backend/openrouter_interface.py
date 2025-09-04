import os
import asyncio
import json
from typing import List, Dict, Optional
import aiohttp
import tiktoken

class OpenRouterInterface:
    def __init__(self, model: str = "deepseek/deepseek-chat-v3.1:free"):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        self.available_models = {
            "deepseek/deepseek-chat-v3.1:free": "deepseek/deepseek-chat-v3.1:free",
            "deepseek/deepseek-r1:free": "deepseek/deepseek-r1:free"
        }
        
        # Validate model
        if model not in self.available_models:
            self.model = "deepseek/deepseek-chat-v3.1:free"  # Default fallback
        
    async def initialize(self):
        """Initialize OpenRouter client (validation only)"""
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY must be set in environment variables")
    
    async def generate_answer(
        self, 
        question: str, 
        context_chunks: List[Dict[str, any]],
        max_tokens: int = 1000
    ) -> Dict[str, any]:
        """Generate answer using OpenRouter with context chunks"""
        if not self.api_key:
            await self.initialize()
        
        try:
            # Build the prompt
            prompt = self._build_prompt(question, context_chunks)
            
            # Prepare the request payload
            payload = {
                "model": self.available_models[self.model],
                "messages": [
                    {
                        "role": "system",
                        "content": ""
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": 0.1,  # Low temperature for consistent, factual responses
                "stream": False
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://investor-qa-assistant.vercel.app",  # Optional: for tracking
                "X-Title": "Investor Q&A Assistant"  # Optional: for tracking
            }
            
            # Make async HTTP request to OpenRouter
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"OpenRouter API error {response.status}: {error_text}")
                    
                    response_data = await response.json()
            
            # Extract the response content
            if 'choices' in response_data and len(response_data['choices']) > 0:
                content = response_data['choices'][0]['message']['content']
                
                # Parse the structured response
                parsed_response = self._parse_response(content)
                
                return {
                    "answer": parsed_response["answer"],
                    "confidence": parsed_response["confidence"],
                    "reasoning": parsed_response.get("reasoning", "Based on provided context"),
                    "model_used": self.model,
                    "tokens_used": response_data.get('usage', {}).get('total_tokens', 0)
                }
            else:
                raise Exception("No valid response from OpenRouter API")
                
        except Exception as e:
            print(f"OpenRouter API error: {str(e)}")
            # Return error response in expected format
            return {
                "answer": f"I apologize, but I encountered an error processing your question with OpenRouter: {str(e)}",
                "confidence": 0,
                "reasoning": "OpenRouter API error occurred",
                "model_used": self.model,
                "tokens_used": 0
            }
    
    def _build_prompt(self, question: str, context_chunks: List[Dict[str, any]]) -> str:
        """Build prompt with context chunks for OpenRouter"""
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
        """Parse OpenRouter response into structured format"""
        try:
            # Default values
            answer = response_text.strip()
            confidence = 70
            reasoning = "Standard response confidence"
            
            # Try to extract structured sections
            lines = response_text.strip().split('\n')
            current_section = None
            sections = {}
            current_content = []
            
            for line in lines:
                line = line.strip()
                if line.upper().startswith('ANSWER:'):
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = 'answer'
                    current_content = [line[7:].strip()] if len(line) > 7 else []
                elif line.upper().startswith('CONFIDENCE:'):
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = 'confidence'
                    current_content = [line[11:].strip()] if len(line) > 11 else []
                elif line.upper().startswith('REASONING:'):
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = 'reasoning'
                    current_content = [line[10:].strip()] if len(line) > 10 else []
                elif current_section and line:
                    current_content.append(line)
            
            # Add the last section
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content).strip()
            
            # Extract parsed values
            if 'answer' in sections and sections['answer']:
                answer = sections['answer']
            
            if 'confidence' in sections:
                try:
                    # Extract number from confidence text
                    conf_text = sections['confidence']
                    import re
                    numbers = re.findall(r'\d+', conf_text)
                    if numbers:
                        confidence = min(100, max(0, int(numbers[0])))
                except:
                    confidence = 70
            
            if 'reasoning' in sections and sections['reasoning']:
                reasoning = sections['reasoning']
            
            return {
                "answer": answer,
                "confidence": confidence,
                "reasoning": reasoning
            }
            
        except Exception as e:
            print(f"Error parsing OpenRouter response: {str(e)}")
            return {
                "answer": response_text.strip(),
                "confidence": 70,
                "reasoning": "Response parsing had issues, using fallback confidence"
            }
    
    def get_model_info(self) -> Dict[str, any]:
        """Get information about the current model"""
        return {
            "provider": "OpenRouter", 
            "model": self.model,
            "max_tokens": 4000,  # Conservative estimate for DeepSeek
            "supports_system_message": True
        }
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Simple estimation: ~4 characters per token for most models
        return len(text) // 4
    
    def get_max_context_tokens(self) -> int:
        """Get maximum context tokens for this model"""
        return 4000  # Conservative estimate for DeepSeek models