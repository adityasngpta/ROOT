import os
import google.generativeai as genai

# Configure the API key
genai.configure(api_key="API-KEY")

# Function to get the file extension
def get_file_extension(filename):
    return os.path.splitext(filename)[1].lower()

# Function to get the response from Gemini
def get_response(question_text):
    try:
        chat_session = model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": [
                            question_text,
                        ],
                    }
                ]
            )
        response = chat_session.send_message("Describe this matrix representing pests on my field and give me spatial insights on how I can treat them.")
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Folder containing the questions (relative to the script directory)
folder_path = os.path.join(script_dir, "fields")

# Output folder for the responses (relative to the script directory)
output_folder_path = os.path.join(script_dir, "analyses")
os.makedirs(output_folder_path, exist_ok=True)

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 512,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction=(
        "You are an advanced AI assistant specializing in agricultural pest management, tasked with analyzing field maps provided by farmers to identify pest infestations and offer actionable advice. Each field map is a matrix where each number represents the number of pests on that plant in that row/column of the field. Your primary goal is to analyze these matrices to determine the distribution and intensity of pest infestations. Use the provided logic to identify the position of the pest cluster: positions can be 'center,' 'northwest,' 'northeast,' 'southwest,' 'southeast,' 'west,' or 'random.' For random clusters, assume a randomly chosen position within the field. Examine the matrix to identify areas of high and low pest concentrations, highlighting any significant clusters or patterns in the distribution of pests. Assess the potential impact on crop health by considering the density of pests in certain areas and the spread of infestation across the field. Identify the highest number of pests in any single cell (maximum pest count), count the number of cells in the matrix with pests (cluster size), and sum all the pest counts in the field (total number of pests). Offer specific recommendations for managing or controlling the infestation, including suggested treatments or pesticides based on severity: for high severity (max pest count >= 7), recommend immediate and intensive pesticide treatment; for moderate severity (max pest count >= 4), recommend moderate pesticide treatment; for low severity (max pest count < 4), recommend light pesticide treatment or the use of natural predators. Additionally, provide preventive measures to avoid future infestations and strategies for monitoring and early detection of pests. Where possible, relate the observed pest distribution to potential underlying causes such as environmental factors, crop type, or season. Your response should include the location of the pest cluster (e.g., southeast region of the field), the severity of the infestation (e.g., high), immediate and intensive pesticide treatment recommendations, maximum pest count, cluster size (number of cells in the matrix with pests), total number of pests, and field size (number of rows and columns). Your response should be clear, detailed, and actionable, aimed at helping farmers make informed decisions to effectively manage pest issues. Answer in paragraph form (no bullets or numbered responses).",
    )
)

# Allowed text file extension
allowed_extensions = {'.txt'}

# Iterate through each category folder (if needed)
for category in os.listdir(folder_path):
    category_path = os.path.join(folder_path, category)
    
    if os.path.isdir(category_path):
        # Create the corresponding category folder in the responses folder
        response_category_path = os.path.join(output_folder_path, category)
        os.makedirs(response_category_path, exist_ok=True)

        # List all text files in the current category folder
        question_files = sorted([f for f in os.listdir(category_path) if os.path.isfile(os.path.join(category_path, f)) and get_file_extension(f) in allowed_extensions])
        total_files = len(question_files)

        # Process each text file in the category
        for idx, question_name in enumerate(question_files):
            question_path = os.path.join(category_path, question_name)

            print(f"Processing question {idx+1}/{total_files} in category {category}: {question_name}")

            try:
                # Read the content of the question file
                with open(question_path, "r", encoding='utf-8') as question_file:
                    question_text = question_file.read()

                # Get the response for the question
                response = get_response(question_text)
                print(f"Received response for question: {question_name}")

                # Save the response in a text file with _Gemini suffix
                output_file_path = os.path.join(response_category_path, f"{os.path.splitext(question_name)[0]}_Gemini_1.5_Pro.txt")
                with open(output_file_path, "w", encoding='utf-8') as output_file:
                    output_file.write(response)
                print(f"Saved response to file: {output_file_path}")

            except Exception as e:
                print(f"Error processing question {question_name}: {e}")

print("Completed processing all questions.")