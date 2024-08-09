import os
import base64
import requests
import time

# OpenAI API Key
api_key = "API-KEY"

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

# Headers for the API request
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Function to get the response from OpenAI
def get_response(image_base64):
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are an advanced AI assistant specializing in agricultural pest management, tasked with analyzing images provided by farmers to identify pest infestations and offer actionable advice. Your primary goal is to examine the image to detect the presence of pests and determine which of the following classes is present: Bean Leaf Beetle, Cloverworm, Dectes Stem Borer, Grape Colaspis, Grasshopper, Japanese Beetle, Northern Corn Rootworm, Southern Corn Rootworm, Stink Bug, or Western Corn Rootworm. In addition to identifying the pest, you should describe the health and condition of the background crop or plant and explain how the pest is impacting the crop. This includes detailing visible damage, changes in plant health, or potential yield loss. Based on the identified pest, provide specific recommendations for managing or controlling the infestation. This should include suggested treatments or pesticides, preventive measures to avoid future infestations, and other strategies. Your response should be clear, detailed, and actionable, aimed at helping farmers make informed decisions to effectively manage pest issues. Answer in paragraph form (no bullets or numbered responses)."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Describe this pest image."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()

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

                # Retry logic for rate limit handling
                retry = True
                while retry:
                    response = get_response(base64_image)
                    print(f"Received response for image: {image_name}")

                    # Check if 'choices' is in the response
                    if 'choices' in response:
                        # Save the response in a text file with _Claude suffix
                        output_file_path = os.path.join(description_category_path, f"{os.path.splitext(image_name)[0]}_GPT-4o_Mini.txt")
                        with open(output_file_path, "w", encoding='utf-8') as output_file:
                            output_file.write(response['choices'][0]['message']['content'])
                        print(f"Saved response to file: {output_file_path}")
                        retry = False
                    else:
                        error = response.get('error', {})
                        if error.get('code') == 'rate_limit_exceeded':
                            wait_time = int(error.get('message').split('try again in ')[-1].split('s')[0])
                            print(f"Rate limit exceeded, retrying in {wait_time} seconds...")
                            time.sleep(wait_time + 1)
                        else:
                            retry = False
                            print(f"Error: 'choices' not in response for image {image_name}, response: {response}")

            except Exception as e:
                print(f"Error processing image {image_name}: {e}")

print("Completed processing all images.")