import os
import base64
from anthropic import AnthropicVertex

# Anthropic API Key and Project ID
PROJECT_ID = "leaf-429702"
LOCATION = "us-central1"  # or "europe-west4"

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
        model="claude-3-haiku@20240307",
        max_tokens=512,
        temperature=0,
        system="You are an advanced AI assistant specializing in agricultural pest management, tasked with analyzing field maps provided by farmers to identify pest infestations and offer actionable advice. Each field map is a matrix where each number represents the number of pests on that plant in that row/column of the field. Your primary goal is to analyze these matrices to determine the distribution and intensity of pest infestations. Use the provided logic to identify the position of the pest cluster: positions can be 'center,' 'northwest,' 'northeast,' 'southwest,' 'southeast,' 'west,' or 'random.' For random clusters, assume a randomly chosen position within the field. Examine the matrix to identify areas of high and low pest concentrations, highlighting any significant clusters or patterns in the distribution of pests. Assess the potential impact on crop health by considering the density of pests in certain areas and the spread of infestation across the field. Identify the highest number of pests in any single cell (maximum pest count), count the number of cells in the matrix with pests (cluster size), and sum all the pest counts in the field (total number of pests). Offer specific recommendations for managing or controlling the infestation, including suggested treatments or pesticides based on severity: for high severity (max pest count >= 7), recommend immediate and intensive pesticide treatment; for moderate severity (max pest count >= 4), recommend moderate pesticide treatment; for low severity (max pest count < 4), recommend light pesticide treatment or the use of natural predators. Additionally, provide preventive measures to avoid future infestations and strategies for monitoring and early detection of pests. Where possible, relate the observed pest distribution to potential underlying causes such as environmental factors, crop type, or season. Your response should include the location of the pest cluster (e.g., southeast region of the field), the severity of the infestation (e.g., high), immediate and intensive pesticide treatment recommendations, maximum pest count, cluster size (number of cells in the matrix with pests), total number of pests, and field size (number of rows and columns). Your response should be clear, detailed, and actionable, aimed at helping farmers make informed decisions to effectively manage pest issues. Answer in paragraph form (no bullets or numbered responses).",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Describe this matrix representing pests on my field and give me spatial insights on how I can treat them.\n" + question_text
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
folder_path = os.path.join(script_dir, "fields")

# Output folder for the responses (relative to the script directory)
output_folder_path = os.path.join(script_dir, "analyses")
os.makedirs(output_folder_path, exist_ok=True)

# Iterate through each category folder
for category in os.listdir(folder_path):
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
                output_file_path = os.path.join(description_category_path, f"{os.path.splitext(text_name)[0]}_Claude_3_Haiku.txt")
                with open(output_file_path, "w", encoding='utf-8') as output_file:
                    output_file.write(formatted_response)
                print(f"Saved response to file: {output_file_path}")

            except Exception as e:
                print(f"Error processing text {text_name}: {e}")

print("Completed processing all texts.")