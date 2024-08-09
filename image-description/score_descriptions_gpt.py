import os
import base64
import requests

# OpenAI API Key
api_key = "API-KEY"

# Function to encode the image as base64 (used for creating the image URL)
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to get the file extension
def get_file_extension(filename):
    return os.path.splitext(filename)[1].lower()

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Folder containing the descriptions (relative to the script directory)
description_folder_path = os.path.join(script_dir, "descriptions")

# Output folder for the scores (relative to the script directory)
score_folder_path = os.path.join(script_dir, "scores")
os.makedirs(score_folder_path, exist_ok=True)

# Headers for the API request
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Function to get the score from OpenAI
def get_score(description_text, ground_truth, image_url):
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": """You are an advanced description scorer model tasked with evaluating and scoring the quality of written descriptions of pest images based on clarity, completeness, and relevance. Your role is to analyze descriptions of crop images that identify pest infestations, describe the impact on plant health, and provide specific, actionable recommendations for pest management and prevention.

Use the following rubric to score the description (grade very strictly, any deviation from the criteria should result in a point deduction):

1. Pest Identification (3 points)
- 3 points: Accurately identifies the pest species and its position on the crop
- 2 points: Identifies the pest, but lacks specificity
- 1 point: Vaguely identifies the pest or makes minor errors
- 0 points: Fails to identify the pest or makes significant errors

2. Damage Description (3 points)
- 3 points: Thoroughly describes visible damage and potential future impact on crop health
- 2 points: Describes visible damage but lacks detail on potential future impact
- 1 point: Briefly mentions damage without specifics
- 0 points: Fails to describe damage or provides inaccurate information

3. Management Recommendations (3 points)
- 3 points: Provides specific, actionable, and appropriate pest management recommendations
- 2 points: Offers general management recommendations but lacks specificity and/or has minor inaccuracies
- 1 point: Suggests vague or incomplete/inaccurate management strategies
- 0 points: Fails to provide management recommendations or suggests inappropriate actions

Additionally, include a Miscellaneous category to deduct points for any significant errors, omissions, or irrelevant information not covered in the above criteria.

Your response should be formatted as follows (please strictly follow the bracketing and line formatting):

1. Pest Identification (x/3) [Justification for score]
2. Damage Description (x/3) [Justification for score]
3. Management Recommendations (x/3) [Justification for score]
Miscellaneous (-x) [Any points subtracted and why]

Total Score: (x/9)"""
            },
            {
                "role": "user",
                "content": f"The correct ground truth classification for the pest in this image is '{ground_truth}'. If the description got the classification wrong, update the score accordingly."
            },
            {
                "role": "user",
                "content": description_text
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": image_url
                }
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()

# Iterate through each category folder
for category in os.listdir(description_folder_path):
    description_category_path = os.path.join(description_folder_path, category)
    
    if os.path.isdir(description_category_path):
        # Create the corresponding category folder in the scores folder
        score_category_path = os.path.join(score_folder_path, category)
        os.makedirs(score_category_path, exist_ok=True)

        # List all text files in the current category folder
        description_files = sorted([f for f in os.listdir(description_category_path) if os.path.isfile(os.path.join(description_category_path, f)) and get_file_extension(f) == '.txt'])
        total_files = len(description_files)

        # Process each description file in the category
        for idx, description_name in enumerate(description_files):
            description_path = os.path.join(description_category_path, description_name)
            image_name = description_name.split('_')[0] + '.jpg'  # Extract image name from description filename
            image_path = os.path.join(script_dir, "images", category, image_name)

            print(f"Processing description {idx+1}/{total_files} in category {category}: {description_name}")

            try:
                # Read the description
                with open(description_path, "r", encoding='utf-8') as file:
                    description_text = file.read()

                # Encode the corresponding image and create a URL
                if os.path.exists(image_path):
                    base64_image = encode_image(image_path)
                    image_url = f"data:image/jpeg;base64,{base64_image}"
                else:
                    print(f"Image file not found: {image_name}")
                    image_url = None

                # Get the score for the description
                if image_url:
                    response = get_score(description_text, category, image_url)
                    print(f"Received score for description: {description_name}")

                    # Format the response
                    formatted_response = response['choices'][0]['message']['content']

                    # Save the score in a text file
                    score_file_path = os.path.join(score_category_path, f"{os.path.splitext(description_name)[0]}-Score.txt")
                    with open(score_file_path, "w", encoding='utf-8') as score_file:
                        score_file.write(formatted_response)
                    print(f"Saved score to file: {score_file_path}")
                else:
                    print(f"Skipping scoring for {description_name} due to missing image.")

            except Exception as e:
                print(f"Error processing description {description_name}: {e}")

print("Completed scoring all descriptions.")
