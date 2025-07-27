import os
from typing import List, Dict, Union
from clarifai.client.model import Model
from config import Config

class ClarifaiImageSegmentation:
    """
    A class for performing image subject segmentation using Clarifai's new Model API.
    Supports different models for compost and plant analysis.
    """
    def __init__(self, model_type: str = "compost", pat: str = None):
        self.model_type = model_type
        
        # Select appropriate model URL and PAT based on type
        if model_type == "plant":
            self.model_url = Config.CLARIFAI_PLANT_MODEL_URL
            self.pat = pat or Config.CLARIFAI_PLANT_PAT or Config.CLARIFAI_PAT
        elif model_type == "compost":
            self.model_url = Config.CLARIFAI_COMPOST_MODEL_URL
            self.pat = pat or Config.CLARIFAI_TANK_PAT or Config.CLARIFAI_PAT
        else:
            raise ValueError(f"Invalid model_type: {model_type}. Use 'compost' or 'plant'")
        
        if not self.pat:
            raise ValueError(f"No Clarifai PAT found for {model_type} model. Check environment variables.")
        
        self.model = Model(url=self.model_url, pat=self.pat)

    def analyse_image(self, image_path: str) -> List[Dict[str, Union[str, float]]]:
        """
        Analyse an image file and return segmentation results.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Use the local file path directly
        model_prediction = self.model.predict_by_filepath(image_path)
        
        results = []
        regions = model_prediction.outputs[0].data.regions
        for region in regions:
            for concept in region.data.concepts:
                # Accessing and rounding the concept's percentage of image covered
                name = concept.name
                value = round(concept.value, 4)
                results.append({
                    'name': name,
                    'value': value
                })
        return results

    def analyse_image_by_url(self, image_url: str) -> List[Dict[str, Union[str, float]]]:
        """
        Analyse an image by URL and return segmentation results.
        """
        model_prediction = self.model.predict_by_url(image_url)
        
        results = []
        regions = model_prediction.outputs[0].data.regions
        for region in regions:
            for concept in region.data.concepts:
                # Accessing and rounding the concept's percentage of image covered
                name = concept.name
                value = round(concept.value, 4)
                results.append({
                    'name': name,
                    'value': value
                })
        return results

    def analyse_and_print(self, image_path: str) -> None:
        """Analyse an image and print the raw results."""
        try:
            for r in self.analyse_image(image_path):
                print(f"{r['name']}: {r['value']}")
        except Exception as e:
            print(f"Error: {e}")

    def get_top_concepts(self, image_path: str, top_n: int = 5) -> List[Dict[str, Union[str, float]]]:
        """Return the top-N concepts by confidence."""
        results = self.analyse_image(image_path)
        return sorted(results, key=lambda x: x['value'], reverse=True)[:top_n]