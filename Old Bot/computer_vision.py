from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
from typing import List, Dict, Union
import os


class ClarifaiImageSegmentation:
    """
    A class for performing image subject segmentation using Clarifai's API.
    """
    
    def __init__(self, pat: str, user_id: str = 'clarifai', app_id: str = 'main'):
        """
        Initialise the ClarifaiImageSegmentation class.
        
        Args:
            pat (str): Personal Access Token for Clarifai API
            user_id (str): User ID (defaults to 'clarifai')
            app_id (str): App ID (defaults to 'main')
        """
        self.pat = pat
        self.user_id = user_id
        self.app_id = app_id
        self.model_id = 'image-subject-segmentation'
        self.model_version_id = '55b2051b75f14577b6fdd5a4fa3fd5a7'
        
        # Set up the gRPC channel and stub
        self.channel = ClarifaiChannel.get_grpc_channel()
        self.stub = service_pb2_grpc.V2Stub(self.channel)
        self.metadata = (('authorization', 'Key ' + self.pat),)
        self.user_data_object = resources_pb2.UserAppIDSet(
            user_id=self.user_id, 
            app_id=self.app_id
        )
    
    def analyse_image(self, image_path: str) -> List[Dict[str, Union[str, float]]]:
        """
        Analyse an image file and return segmentation results.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            List[Dict[str, Union[str, float]]]: List of dictionaries containing 
                                               concept names and their coverage values
                                               
        Raises:
            FileNotFoundError: If the image file doesn't exist
            Exception: If the API call fails
        """
        # Check if file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Read the image file
        try:
            with open(image_path, "rb") as f:
                file_bytes = f.read()
        except Exception as e:
            raise Exception(f"Error reading image file: {str(e)}")
        
        # Make the API call
        try:
            post_model_outputs_response = self.stub.PostModelOutputs(
                service_pb2.PostModelOutputsRequest(
                    user_app_id=self.user_data_object,
                    model_id=self.model_id,
                    version_id=self.model_version_id,
                    inputs=[
                        resources_pb2.Input(
                            data=resources_pb2.Data(
                                image=resources_pb2.Image(
                                    base64=file_bytes
                                )
                            )
                        )
                    ]
                ),
                metadata=self.metadata
            )
        except Exception as e:
            raise Exception(f"API call failed: {str(e)}")
        
        # Check response status
        if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
            raise Exception(
                f"Post model outputs failed, status: {post_model_outputs_response.status.description}"
            )
        
        # Extract and format results
        results = []
        regions = post_model_outputs_response.outputs[0].data.regions
        
        for region in regions:
            for concept in region.data.concepts:
                results.append({
                    'name': concept.name,
                    'value': round(concept.value, 4)
                })
        
        return results
    
    def analyse_and_print(self, image_path: str) -> None:
        """
        Analyse an image and print the results in the original format.
        
        Args:
            image_path (str): Path to the image file
        """
        try:
            results = self.analyse_image(image_path)
            for result in results:
                print(f"{result['name']}: {result['value']}")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def get_top_concepts(self, image_path: str, top_n: int = 5) -> List[Dict[str, Union[str, float]]]:
        """
        Get the top N concepts from image segmentation.
        
        Args:
            image_path (str): Path to the image file
            top_n (int): Number of top concepts to return (default: 5)
            
        Returns:
            List[Dict[str, Union[str, float]]]: Top N concepts sorted by value
        """
        results = self.analyse_image(image_path)
        return sorted(results, key=lambda x: x['value'], reverse=True)[:top_n]


# Example usage
if __name__ == "__main__":
    # Initialise the segmentation class
    PAT = '88daa3cc427546dfaf4f37e1c1ddb3d3'
    segmenter = ClarifaiImageSegmentation(pat=PAT)
    
    # Analyse an image
    try:
        image_file = 'testimage.png'
        
        # Method 1: Get results as a list of dictionaries
        results = segmenter.analyse_image(image_file)
        print("Results as list:")
        for result in results:
            print(f"  {result['name']}: {result['value']}")
        
        print("\n" + "="*50 + "\n")
        
        # Method 2: Print results directly (original format)
        print("Direct printing:")
        segmenter.analyse_and_print(image_file)
        
        print("\n" + "="*50 + "\n")
        
        # Method 3: Get top 3 concepts
        top_concepts = segmenter.get_top_concepts(image_file, top_n=3)
        print("Top 3 concepts:")
        for concept in top_concepts:
            print(f"  {concept['name']}: {concept['value']}")
            
    except Exception as e:
        print(f"Error: {str(e)}")