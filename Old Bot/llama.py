import asyncio
import logging
from typing import Optional
from huggingface_hub import InferenceClient

logger = logging.getLogger(__name__)


class LlamaInterface:
    """
    Simple interface for interacting with Llama models via Hugging Face Inference API.
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialise the LlamaInterface.
        
        Args:
            model_name: Name of the model to use. Defaults to Meta-Llama-3-8B-Instruct
        """

        self.model_name = model_name or "meta-llama/Meta-Llama-3-8B-Instruct" # modify this depending on model
        
        # Create the inference client
        self.client = InferenceClient(self.model_name)
        
    async def generate_response(self, prompt: str, max_length: int = 500) -> str:
        """
        Generate a response from the Llama model.
        
        Args:
            prompt: The input text prompt
            max_length: Maximum length of the generated response
            
        Returns:
            Generated response text
        """
        try:
            # Create message format for chat completion
            messages = [{"role": "user", "content": prompt}]
            
            # Get response from the model
            response = self.client.chat_completion(
                messages=messages,
                max_tokens=max_length,
                temperature=0.7
            )
            
            # Extract and return the response content
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Sorry, I encountered an error while processing your request. Please try again."