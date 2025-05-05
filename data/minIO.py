import os
import json
from minio import Minio
from minio.error import S3Error
import io
from PIL import Image
import matplotlib.pyplot as plt

# Function to load credentials from JSON file
def load_credentials(json_path="credentials.json"):
    try:
        with open(json_path, 'r') as file:
            credentials = json.load(file)
            return credentials
    except FileNotFoundError:
        print(f"Error: Credentials file '{json_path}' not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{json_path}'.")
        exit(1)

# Load credentials
credentials = load_credentials()

# Use the working endpoint we discovered
minio_endpoint = "minio.tinkerthings.global:443"
access_key = credentials.get("accessKey", "")
secret_key = credentials.get("secretKey", "")
bucket_name = "tinkerthings-global-compost-tracker"
secure = True  # Using HTTPS on port 443

print(f"Connecting to MinIO at {minio_endpoint}")
print(f"Bucket: {bucket_name}")

# Create a MinIO client
client = Minio(
    endpoint=minio_endpoint,
    access_key=access_key,
    secret_key=secret_key,
    secure=secure
)

try:
    # Verify bucket exists
    if client.bucket_exists(bucket_name):
        print(f"Successfully connected to bucket '{bucket_name}'")
        
        # List objects in the bucket (fixed parameter issue)
        objects = list(client.list_objects(bucket_name, recursive=True))
        
        if not objects:
            print(f"No objects found in bucket '{bucket_name}'")
            exit(0)
        
        # Filter for image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        images = []
        
        print(f"\nImages in bucket {bucket_name}:")
        print("-" * 50)
        
        # List all images
        for i, obj in enumerate(objects):
            object_name = obj.object_name
            _, file_extension = os.path.splitext(object_name)
            
            if not image_extensions or file_extension.lower() in image_extensions:
                images.append(obj)
                print(f"{i+1}. {object_name} ({obj.size} bytes)")
        
        print("-" * 50)
        print(f"Total potential images found: {len(images)}")
        
        if images:
            # Function to download and display an image
            def download_and_display_image(object_name, save_path=None):
                try:
                    # Get the object data
                    response = client.get_object(bucket_name, object_name)
                    
                    # Read the data
                    data = response.read()
                    
                    # Load image using PIL
                    image_data = io.BytesIO(data)
                    image = Image.open(image_data)
                    
                    # Display image info
                    print(f"\nImage: {object_name}")
                    print(f"Format: {image.format}")
                    print(f"Size: {image.size}")
                    print(f"Mode: {image.mode}")
                    
                    # Display the image
                    plt.figure(figsize=(10, 8))
                    plt.imshow(image)
                    plt.title(object_name)
                    plt.axis('off')
                    plt.show()
                    
                    # Save to disk if save_path is provided
                    if save_path:
                        image.save(save_path)
                        print(f"Image saved to {save_path}")
                    
                    response.close()
                    response.release_conn()
                    return image
                
                except S3Error as err:
                    print(f"Error downloading {object_name}: {err}")
                    return None
                except Exception as err:
                    print(f"Error processing image {object_name}: {err}")
                    return None
            
            # Allow user to select an image to display
            while True:
                try:
                    print("\nEnter the number of the image you want to display (0 to exit):")
                    choice = int(input())
                    
                    if choice == 0:
                        break
                    elif 1 <= choice <= len(images):
                        selected_image = images[choice-1].object_name
                        download_and_display_image(selected_image)
                    else:
                        print(f"Please enter a number between 1 and {len(images)}")
                except ValueError:
                    print("Please enter a valid number")
                except KeyboardInterrupt:
                    print("\nExiting...")
                    break
        
    else:
        print(f"Bucket '{bucket_name}' does not exist")

except S3Error as err:
    print(f"MinIO Error: {err}")
except Exception as err:
    print(f"Error: {err}")