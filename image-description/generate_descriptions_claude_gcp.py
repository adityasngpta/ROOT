import os
import shutil
import base64
from anthropic import AnthropicVertex
from PIL import Image
import io

# Anthropic API Key and Project ID
PROJECT_ID = "leaf-429702"
LOCATION = "europe-west4"

# Initialize Anthropic client
client = AnthropicVertex(region=LOCATION, project_id=PROJECT_ID)

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to get the file extension
def get_file_extension(filename):
    return os.path.splitext(filename)[1].lower()

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Folder containing the images (relative to the script directory)
folder_path = os.path.join(script_dir, "images")

# Output folder for the responses (relative to the script directory)
output_folder_path = os.path.join(script_dir, "descriptions")
os.makedirs(output_folder_path, exist_ok=True)

# Function to get the response from Claude
def get_response(image_base64):
        message = client.messages.create(
            model="claude-3-haiku@20240307",
            max_tokens=512,
            temperature=0,
            system="You are an advanced AI assistant specializing in agricultural pest management, tasked with analyzing images provided by farmers to identify pest infestations and offer actionable advice. Your primary goal is to examine the image to detect the presence of pests and determine which of the following classes is present: Bean Leaf Beetle, Cloverworm, Dectes Stem Borer, Grape Colaspis, Grasshopper, Japanese Beetle, Northern Corn Rootworm, Southern Corn Rootworm, Stink Bug, or Western Corn Rootworm. In addition to identifying the pest, you should describe the health and condition of the background crop or plant and explain how the pest is impacting the crop. This includes detailing visible damage, changes in plant health, or potential yield loss. Based on the identified pest, provide specific recommendations for managing or controlling the infestation. This should include suggested treatments or pesticides, preventive measures to avoid future infestations, and other strategies. Your response should be clear, detailed, and actionable, aimed at helping farmers make informed decisions to effectively manage pest issues. Answer in paragraph form (no bullets or numbered responses).",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe this pest image."
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }
            ]
        )
        return message.content

# Function to format the response
def format_response(response):
    if isinstance(response, str):
        return response
    elif isinstance(response, list):
        formatted = []
        for item in response:
            if hasattr(item, 'text'):
                formatted.append(item.text)
            elif isinstance(item, dict) and 'text' in item:
                formatted.append(item['text'])
            else:
                formatted.append(str(item))
        return "\n".join(formatted)
    elif hasattr(response, 'text'):
        return response.text
    elif isinstance(response, dict) and 'text' in response:
        return response['text']
    else:
        return json.dumps(response, indent=2)

# Allowed image file extensions
allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}

# Iterate through each category folder
for category in os.listdir(folder_path):
    category_path = os.path.join(folder_path, category)
    
    if os.path.isdir(category_path):
        # Create the corresponding category folder in the descriptions folder
        description_category_path = os.path.join(output_folder_path, category)
        os.makedirs(description_category_path, exist_ok=True)

        # List all image files in the current category folder
        image_files = sorted([f for f in os.listdir(category_path) if os.path.isfile(os.path.join(category_path, f)) and get_file_extension(f) in allowed_extensions])
        total_images = len(image_files)

        # Process each image in the category
        for idx, image_name in enumerate(image_files):
            image_path = os.path.join(category_path, image_name)

            print(f"Processing image {idx+1}/{total_images} in category {category}: {image_name}")

            try:
                # Encode the image
                base64_image = encode_image(image_path)
                print(f"Encoded image: {image_name}")

                # Get 1 response for each image
                response = get_response(base64_image)
                print(f"Received response for image: {image_name}")

                # Format the response
                formatted_response = format_response(response)

                # Save the response in a text file with _Claude suffix
                output_file_path = os.path.join(description_category_path, f"{os.path.splitext(image_name)[0]}_Claude_3_Haiku.txt")
                with open(output_file_path, "w", encoding='utf-8') as output_file:
                    output_file.write(formatted_response)
                print(f"Saved response to file: {output_file_path}")

            except Exception as e:
                print(f"Error processing image {image_name}: {e}")

print("Completed processing all images.")