"""
Image Analysis Handler for Nutribot
Handles dual AI analysis: Clarifai + OpenAI Vision
"""

import os
import logging
import base64
from typing import Dict, List, Optional, Tuple
from services.clarifai_segmentation import ClarifaiImageSegmentation
from services.llama_interface import LlamaInterface

logger = logging.getLogger(__name__)


class ImageAnalysisHandler:
    """
    Handles dual image analysis combining Clarifai technical analysis 
    with OpenAI Vision independent assessment
    """
    
    def __init__(self):
        self.llama = LlamaInterface()
        
        # Log environment variable status
        from config import Config
        logger.info(f"CLARIFAI_TANK_PAT set: {bool(Config.CLARIFAI_TANK_PAT)}")
        logger.info(f"CLARIFAI_PLANT_PAT set: {bool(Config.CLARIFAI_PLANT_PAT)}")
        logger.info(f"CLARIFAI_PAT (legacy) set: {bool(Config.CLARIFAI_PAT)}")
        logger.info(f"OPENAI_API_KEY set: {bool(Config.OPENAI_API_KEY)}")
    
    async def analyze_image_with_ai_advice(
        self, 
        image_path: str, 
        scan_type: str
    ) -> Dict:
        """
        Perform dual analysis: Clarifai + OpenAI interpretation AND independent OpenAI Vision
        
        Args:
            image_path (str): Path to the image file
            scan_type (str): "compost" or "plant"
            
        Returns:
            Dict: Analysis results with structured advice
        """
        result = {
            "clarifai_success": False,
            "vision_success": False,
            "clarifai_results": None,
            "clarifai_interpretation": None,
            "vision_analysis": None,
            "combined_message": ""
        }
        
        # Step 1: Try Clarifai Analysis
        clarifai_results = await self._analyze_with_clarifai(image_path, scan_type)
        if clarifai_results:
            result["clarifai_success"] = True
            result["clarifai_results"] = clarifai_results
            
            # Step 2: Get OpenAI interpretation of Clarifai results
            interpretation = await self._interpret_clarifai_results(clarifai_results, scan_type)
            result["clarifai_interpretation"] = interpretation
        
        # Step 3: Independent OpenAI Vision Analysis (always attempted)
        vision_analysis = await self._analyze_with_openai_vision(image_path, scan_type)
        if vision_analysis:
            result["vision_success"] = True
            result["vision_analysis"] = vision_analysis
        
        # Step 4: Format combined response
        result["combined_message"] = self._format_combined_response(result, scan_type)
        
        return result
    
    async def _analyze_with_clarifai(
        self, 
        image_path: str, 
        scan_type: str
    ) -> Optional[List[Dict]]:
        """
        Analyze image with Clarifai model
        """
        try:
            logger.info(f"Starting Clarifai analysis for {scan_type} with image: {image_path}")
            clarifai = ClarifaiImageSegmentation(model_type=scan_type)
            logger.info(f"Clarifai instance created successfully for {scan_type}")
            top_concepts = clarifai.get_top_concepts(image_path, top_n=5)
            logger.info(f"Clarifai analysis successful: {len(top_concepts)} concepts found")
            return top_concepts
        except Exception as e:
            logger.error(f"Clarifai analysis failed for {scan_type}: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return None
    
    async def _interpret_clarifai_results(
        self, 
        clarifai_results: List[Dict], 
        scan_type: str
    ) -> Optional[str]:
        """
        Use OpenAI to interpret Clarifai technical results
        """
        try:
            # Format Clarifai results for AI interpretation
            results_text = "\n".join([
                f"- {result['name']}: {round(result['value']*100, 1)}% confidence"
                for result in clarifai_results
            ])
            
            if scan_type == "compost":
                prompt = f"""You are a composting expert. Based on these technical analysis results from an image classification model:

{results_text}

Provide expert interpretation focusing on:
1. What these detected elements indicate about compost quality
2. The decomposition stage and process health
3. Potential issues or concerns
4. Specific actionable recommendations for improvement

Keep the response concise and practical for home composters."""

            else:  # plant
                prompt = f"""You are a plant health specialist. Based on these technical analysis results from an image classification model:

{results_text}

Provide expert interpretation focusing on:
1. What these detected elements indicate about plant health
2. Identification of potential diseases, pests, or deficiencies
3. Overall plant condition assessment
4. Specific care recommendations and next steps

Keep the response concise and practical for home gardeners."""
            
            interpretation = await self.llama.generate_response(prompt, max_length=400)
            return interpretation
            
        except Exception as e:
            logger.error(f"Clarifai interpretation failed: {str(e)}")
            return None
    
    async def _analyze_with_openai_vision(
        self, 
        image_path: str, 
        scan_type: str
    ) -> Optional[str]:
        """
        Analyze image directly with OpenAI Vision API
        """
        try:
            logger.info(f"Starting OpenAI Vision analysis for {scan_type} with image: {image_path}")
            
            # Convert image to base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            logger.info(f"Image successfully converted to base64, size: {len(base64_image)} characters")
            
            if scan_type == "compost":
                prompt = """You are a composting expert analyzing this compost image. Provide a visual assessment covering:

1. **Visual Observations**: What you see in terms of color, texture, moisture, decomposition stage
2. **Quality Assessment**: Overall compost health and maturity
3. **Issues Identified**: Any problems like improper ratios, moisture issues, or contamination
4. **Recommendations**: Specific actions to improve the compost

Be practical and specific in your advice for home composters."""

            else:  # plant
                prompt = """You are a plant health specialist analyzing this plant image. Provide a visual assessment covering:

1. **Visual Observations**: Leaf color, texture, growth patterns, any visible symptoms
2. **Health Assessment**: Overall plant condition and vitality
3. **Issues Identified**: Signs of disease, pests, nutrient deficiencies, or stress
4. **Care Recommendations**: Specific actions for plant health improvement

Be practical and specific in your advice for home gardeners."""
            
            logger.info(f"Calling OpenAI Vision API for {scan_type}")
            vision_analysis = await self.llama.analyze_image_with_vision(base64_image, prompt)
            logger.info(f"OpenAI Vision analysis successful, response length: {len(vision_analysis) if vision_analysis else 0}")
            return vision_analysis
            
        except Exception as e:
            logger.error(f"OpenAI Vision analysis failed for {scan_type}: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return None
    
    def _format_combined_response(self, result: Dict, scan_type: str) -> str:
        """
        Format the final combined response message
        """
        scan_emoji = "🪣" if scan_type == "compost" else "🌱"
        scan_name = "Compost Tank" if scan_type == "compost" else "Plant"
        
        # Case 1: Both analyses successful
        if result["clarifai_success"] and result["vision_success"]:
            message = f"{scan_emoji} **{scan_name} Analysis Complete**\n\n"
            
            # Technical Analysis Section
            message += "📊 **Technical Analysis:**\n"
            if result["clarifai_interpretation"]:
                message += result["clarifai_interpretation"]
            else:
                # Fallback: show raw Clarifai results
                message += "Detected elements:\n"
                for item in result["clarifai_results"]:
                    message += f"• {item['name'].title()}: {round(item['value']*100, 1)}%\n"
            
            message += "\n\n👁️ **Visual Assessment:**\n"
            message += result["vision_analysis"]
            
        # Case 2: Only Vision successful
        elif result["vision_success"]:
            message = f"{scan_emoji} **{scan_name} Visual Analysis Complete**\n\n"
            message += "👁️ **Expert Assessment:**\n"
            message += result["vision_analysis"]
            
        # Case 3: Only Clarifai successful
        elif result["clarifai_success"]:
            message = f"{scan_emoji} **{scan_name} Technical Analysis Complete**\n\n"
            message += "📊 **Analysis Results:**\n"
            if result["clarifai_interpretation"]:
                message += result["clarifai_interpretation"]
            else:
                message += "Detected elements:\n"
                for item in result["clarifai_results"]:
                    message += f"• {item['name'].title()}: {round(item['value']*100, 1)}%\n"
            message += "\n\n⚠️ *Visual analysis temporarily unavailable*"
            
        # Case 4: Both failed
        else:
            message = f"⚠️ Unable to analyze the {scan_name.lower()} image at this time. Please try again with a clearer photo or check your connection."
        
        return message


# Global instance for easy import
image_analyzer = ImageAnalysisHandler()