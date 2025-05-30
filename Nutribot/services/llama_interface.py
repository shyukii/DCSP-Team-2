import logging
import aiohttp
import json
from config import LLAMA_MODEL, HUGGINGFACE_API_TOKEN

logger = logging.getLogger(__name__)

class LlamaInterface:
    """
    Interface for interacting with Llama models via Hugging Face's direct Inference API.
    """
    def __init__(self, model_name: str = None):
        """
        Initialise the LlamaInterface.

        Args:
            model_name: Name of the model to use. Defaults to LLAMA_MODEL from config.
        """
        # Use a working model as fallback
        self.model_name = model_name or LLAMA_MODEL
        
        # List of known working models
        self.working_models = [
            "HuggingFaceH4/zephyr-7b-beta",
            "microsoft/Phi-3-mini-4k-instruct",
            "mistralai/Mixtral-8x7B-Instruct-v0.1"
        ]
        
        # If the configured model is not working, use a fallback
        if self.model_name in ["microsoft/DialoGPT-medium", "microsoft/DialoGPT-small", "gpt2"]:
            logger.warning(f"Model {self.model_name} is currently unavailable. Using fallback model.")
            self.model_name = "HuggingFaceH4/zephyr-7b-beta"
        
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        self.headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Using model: {self.model_name}")

    async def generate_response(self, prompt: str, max_length: int = 500) -> str:
        """
        Generate a response from the model using direct API calls.

        Args:
            prompt: The input text prompt
            max_length: Maximum length of the generated response

        Returns:
            Generated response text
        """
        try:
            # Create a system prompt that helps guide the model
            system_context = "You are NutriBot, a helpful assistant specializing in gardening, composting, and environmental topics."
            
            # Format the conversation properly for zephyr model
            formatted_prompt = f"<|system|>\n{system_context}</s>\n<|user|>\n{prompt}</s>\n<|assistant|>\n"
            
            # Prepare the payload for text generation
            payload = {
                "inputs": formatted_prompt,
                "parameters": {
                    "max_new_tokens": max_length,
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if isinstance(result, list) and len(result) > 0:
                            generated_text = result[0].get('generated_text', 'No response generated.')
                            # Clean up the response - remove any formatting artifacts
                            generated_text = generated_text.strip()
                            
                            # Remove any continuation of the conversation template
                            if "</s>" in generated_text:
                                generated_text = generated_text.split("</s>")[0].strip()
                            
                            # Remove any additional conversation markers
                            if "<|user|>" in generated_text:
                                generated_text = generated_text.split("<|user|>")[0].strip()
                                
                            return generated_text
                        else:
                            return str(result)
                    elif response.status == 503:
                        # Model is loading
                        error_data = await response.json()
                        estimated_time = error_data.get('estimated_time', 20)
                        return f"The model is currently loading. Please try again in {estimated_time} seconds."
                    else:
                        error_text = await response.text()
                        logger.error(f"API Error {response.status}: {error_text}")
                        
                        # Try with a fallback model
                        if self.model_name not in self.working_models:
                            logger.info("Attempting with fallback model...")
                            self.model_name = self.working_models[0]
                            self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
                            return await self.generate_response(prompt, max_length)
                        
                        return "Sorry, I encountered an error while processing your request. Please try again."
            
        except asyncio.TimeoutError:
            logger.error("Request timed out")
            return "Sorry, the request took too long. Please try again."
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Sorry, I encountered an error while processing your request. Please try again."
