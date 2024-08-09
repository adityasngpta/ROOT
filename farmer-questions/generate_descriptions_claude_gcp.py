import os
import base64
from anthropic import AnthropicVertex

# Anthropic API Key and Project ID
PROJECT_ID = "leaf-429702"
LOCATION = "us-east5"  # or "europe-west4"

# Initialize Anthropic client
client = AnthropicVertex(region=LOCATION, project_id=PROJECT_ID)

# Function to get the file extension
def get_file_extension(filename):
    return os.path.splitext(filename)[1].lower()

# Function to read the content of the text file
def read_text_file(file_path):
    with open(file_path, "r", encoding='utf-8') as file:
        return file.read()

# Function to get the response from Claude
def get_response(question_text):
    message = client.messages.create(
        model="claude-3-opus@20240229",
        max_tokens=512,
        temperature=0,
        system="You are an advanced AI assistant specializing in agriculture, tasked with answering questions asked by farmers to help deal with pest infestations and offer actionable advice. Your response should directly and concisely answer the question and help farmers make informed decisions to effectively manage agricultural issues for efficient and sustainable farming. Answer in paragraph form (no bullets or numbered responses).",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": question_text
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

# Allowed text file extension
allowed_extensions = {'.txt'}

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Folder containing the questions (relative to the script directory)
folder_path = os.path.join(script_dir, "questions")

# Output folder for the responses (relative to the script directory)
output_folder_path = os.path.join(script_dir, "answers")
os.makedirs(output_folder_path, exist_ok=True)

# Iterate through each category folder
for category in os.listdir(folder_path):
    if category == "Southern Corn Rootworm":
        category_path = os.path.join(folder_path, category)
        
        if os.path.isdir(category_path):
            # Create the corresponding category folder in the descriptions folder
            description_category_path = os.path.join(output_folder_path, category)
            os.makedirs(description_category_path, exist_ok=True)

            # List all text files in the current category folder
            text_files = sorted([f for f in os.listdir(category_path) if os.path.isfile(os.path.join(category_path, f)) and get_file_extension(f) in allowed_extensions])
            total_files = len(text_files)

            # Process each text file in the category
            for idx, text_name in enumerate(text_files):
                text_path = os.path.join(category_path, text_name)

                if idx+1 != 5 and category == 'Grasshopper':
                    continue

                print(f"Processing text {idx+1}/{total_files} in category {category}: {text_name}")

                try:
                    # Read the question from the text file
                    question_text = read_text_file(text_path)
                    print(f"Read question from file: {text_name}")

                    # Get the response for the question
                    response = get_response(question_text)
                    print(f"Received response for text: {text_name}")

                    # Format the response
                    formatted_response = format_response(response)

                    # Save the response in a text file with _Claude suffix
                    output_file_path = os.path.join(description_category_path, f"{os.path.splitext(text_name)[0]}_Claude_3_Opus.txt")
                    with open(output_file_path, "w", encoding='utf-8') as output_file:
                        output_file.write(formatted_response)
                    print(f"Saved response to file: {output_file_path}")

                except Exception as e:
                    print(f"Error processing text {text_name}: {e}")

print("Completed processing all texts.")