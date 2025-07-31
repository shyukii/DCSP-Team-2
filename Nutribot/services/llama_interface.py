import logging
import aiohttp
import json
import asyncio
from config import Config

logger = logging.getLogger(__name__)

class LlamaInterface:
    """
    Interface for interacting with OpenAI's GPT models via their API.
    """
    def __init__(self, model_name: str = None):
        """
        Initialise the LLM.

        Args:
            model_name: Name of the OpenAI model to use. Defaults to OPENAI_MODEL from config.
        """
        self.model_name = model_name or Config.OPENAI_MODEL
        
        self.api_url = Config.OPENAI_API_URL
        self.headers = {
            "Authorization": f"Bearer {Config.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Using OpenAI model: {self.model_name}")
        self.history = []

    def clear_memory(self):
        """Clear the conversation history."""
        self.history = []

    async def generate_response(self, prompt: str, max_length: int = 500) -> str:
        """
        Generate a response from OpenAI's GPT model.

        Args:
            prompt: The input text prompt
            max_length: Maximum length of the generated response (max_tokens)

        Returns:
            Generated response text
        """
        try:
            # Create system message for NutriBot
            system_message = {
                "role": "system",
                "content": "You are NutriBot, a helpful assistant specializing in gardening, composting, and environmental topics. Provide practical, informative, and friendly advice about plants, composting, sustainability, and related topics."
            }
            
            # Build messages array with conversation history
            messages = [system_message]
            
            # Add conversation history
            messages.extend(self.history)
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Prepare the payload for OpenAI API
            payload = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": max_length,
                "temperature": Config.AI_TEMPERATURE,
                "top_p": Config.AI_TOP_P,
                "frequency_penalty": 0,
                "presence_penalty": 0
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=Config.HTTP_TIMEOUT)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if 'choices' in result and len(result['choices']) > 0:
                            generated_text = result['choices'][0]['message']['content'].strip()
                            
                            # Add to conversation history
                            self.history.append({
                                "role": "user",
                                "content": prompt
                            })
                            self.history.append({
                                "role": "assistant",
                                "content": generated_text
                            })
                            
                            # Limit conversation history to prevent token overflow
                            if len(self.history) > 10:  # Keep last 5 exchanges
                                self.history = self.history[-10:]
                            
                            return generated_text
                        else:
                            logger.error(f"Unexpected API response format: {result}")
                            return "Sorry, I received an unexpected response format. Please try again."
                    
                    elif response.status == 401:
                        logger.error("OpenAI API authentication failed")
                        return "Sorry, there's an authentication issue. Please check the API key configuration."
                    
                    elif response.status == 429:
                        logger.error("OpenAI API rate limit exceeded")
                        return "Sorry, I'm currently receiving too many requests. Please try again in a moment."
                    
                    elif response.status == 503:
                        logger.error("OpenAI API service unavailable")
                        return "Sorry, the AI service is temporarily unavailable. Please try again later."
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenAI API Error {response.status}: {error_text}")
                        return "Sorry, I encountered an error while processing your request. Please try again."
            
        except asyncio.TimeoutError:
            logger.error("Request to OpenAI API timed out")
            return "Sorry, the request took too long. Please try again."
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return "Sorry, I received an invalid response. Please try again."
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Sorry, I encountered an error while processing your request. Please try again."

    async def analyze_image_with_vision(self, base64_image: str, prompt: str, max_length: int = 500) -> str:
        """
        Analyze an image using OpenAI's Vision API (GPT-4V)
        
        Args:
            base64_image: Base64 encoded image data
            prompt: Analysis prompt for the AI
            max_length: Maximum length of response
            
        Returns:
            Analysis response text
        """
        try:
            # Create system message for vision analysis
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ]
            
            # Prepare payload for OpenAI Vision API
            payload = {
                "model": "gpt-4o",  # Use GPT-4 with vision capabilities
                "messages": messages,
                "max_tokens": max_length,
                "temperature": Config.AI_TEMPERATURE,
                "top_p": Config.AI_TOP_P
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=Config.HTTP_TIMEOUT + 10)  # Extra time for vision
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if 'choices' in result and len(result['choices']) > 0:
                            return result['choices'][0]['message']['content'].strip()
                        else:
                            logger.error(f"Unexpected vision API response format: {result}")
                            return "Sorry, I received an unexpected response format during image analysis."
                    
                    elif response.status == 401:
                        logger.error("OpenAI Vision API authentication failed")
                        return "Sorry, there's an authentication issue with the vision analysis."
                    
                    elif response.status == 429:
                        logger.error("OpenAI Vision API rate limit exceeded")
                        return "Sorry, the vision analysis service is temporarily busy. Please try again in a moment."
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenAI Vision API Error {response.status}: {error_text}")
                        return "Sorry, I encountered an error during image analysis. Please try again."
                        
        except asyncio.TimeoutError:
            logger.error("Vision API request timed out")
            return "Sorry, the image analysis took too long. Please try again."
        except Exception as e:
            logger.error(f"Error in vision analysis: {e}")
            return "Sorry, I encountered an error while analyzing the image. Please try again."