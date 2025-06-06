import os
from typing import List, Dict, Union
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
from config import Config

class ClarifaiImageSegmentation:
    """
    A class for performing image subject segmentation using Clarifai's API.
    """
    def __init__(self,
                 pat: str = Config.CLARIFAI_PAT,
                 user_id: str = Config.CLARIFAI_USER_ID,
                 app_id: str = Config.CLARIFAI_APP_ID):
        self.pat = pat
        self.user_id = user_id
        self.app_id = app_id
        self.model_id = Config.CLARIFAI_MODEL_ID
        self.model_version_id = Config.CLARIFAI_MODEL_VERSION
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
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        with open(image_path, "rb") as f:
            file_bytes = f.read()

        resp = self.stub.PostModelOutputs(
            service_pb2.PostModelOutputsRequest(
                user_app_id=self.user_data_object,
                model_id=self.model_id,
                version_id=self.model_version_id,
                inputs=[resources_pb2.Input(
                    data=resources_pb2.Data(
                        image=resources_pb2.Image(base64=file_bytes)
                    )
                )]
            ),
            metadata=self.metadata
        )

        if resp.status.code != status_code_pb2.SUCCESS:
            raise Exception(
                f"Segmentation failed: {resp.status.description}"
            )

        results = []
        regions = resp.outputs[0].data.regions
        for region in regions:
            for concept in region.data.concepts:
                results.append({
                    'name': concept.name,
                    'value': round(concept.value, 4)
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
