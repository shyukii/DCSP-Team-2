##################################################################################################
# In this section, we set the user authentication, user and app ID, model details, and the URL
# of the image we want as an input. Change these strings to run your own example.
#################################################################################################

# Your PAT (Personal Access Token) can be found in the Account's Security section
PAT = '88daa3cc427546dfaf4f37e1c1ddb3d3'
# Specify the correct user_id/app_id pairings
# Since you're making inferences outside your app's scope
USER_ID = 'clarifai'
APP_ID = 'main'
# Change these to whatever model and image URL you want to use
MODEL_ID = 'image-subject-segmentation'
MODEL_VERSION_ID = '55b2051b75f14577b6fdd5a4fa3fd5a7'
# IMAGE_URL = 'https://samples.clarifai.com/metro-north.jpg'
# To use a local file, assign the location variable
IMAGE_FILE_LOCATION = 'testimage.png'

############################################################################
# YOU DO NOT NEED TO CHANGE ANYTHING BELOW THIS LINE TO RUN THIS EXAMPLE
############################################################################

from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2

channel = ClarifaiChannel.get_grpc_channel()
stub = service_pb2_grpc.V2Stub(channel)

metadata = (('authorization', 'Key ' + PAT),)

# To use a local file, uncomment the following lines
with open(IMAGE_FILE_LOCATION, "rb") as f:
    file_bytes = f.read()

userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

post_model_outputs_response = stub.PostModelOutputs(
    service_pb2.PostModelOutputsRequest(
        user_app_id=userDataObject,  # The userDataObject is created in the overview and is required when using a PAT
        model_id=MODEL_ID,
        version_id=MODEL_VERSION_ID,  # This is optional. Defaults to the latest model version
        inputs=[
            resources_pb2.Input(
                data=resources_pb2.Data(
                    image=resources_pb2.Image(
                        # url=IMAGE_URL
                        base64=file_bytes
                    )
                )
            )
        ]
    ),
    metadata=metadata
)
if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
    print(post_model_outputs_response.status)
    raise Exception("Post model outputs failed, status: " + post_model_outputs_response.status.description)

regions = post_model_outputs_response.outputs[0].data.regions

for region in regions:
    for concept in region.data.concepts:
        # Accessing and rounding the concept's percentage of image covered
        name = concept.name
        value = round(concept.value, 4)
        print((f"{name}: {value}"))