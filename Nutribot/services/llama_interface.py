import logging
from huggingface_hub import InferenceClient
from config import LLAMA_MODEL

logger = logging.getLogger(__name__)

class LlamaInterface:
    """
    Simple interface for interacting with Llama models via Hugging Face Inference API.
    """
    def __init__(self, model_name: str = None):
        """
        Initialise the LlamaInterface.

        Args:
            model_name: Name of the model to use. Defaults to LLAMA_MODEL from config.
        """
        self.model_name = model_name or LLAMA_MODEL
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
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completion(
                messages=messages,
                max_tokens=max_length,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Sorry, I encountered an error while processing your request. Please try again."
