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
        response = chat_session.send_message("Provide a detailed response.")
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Folder containing the questions (relative to the script directory)
folder_path = os.path.join(script_dir, "questions")

# Output folder for the responses (relative to the script directory)
output_folder_path = os.path.join(script_dir, "answers")
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
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=(
        "You are an advanced AI assistant specializing in agriculture, tasked with answering questions asked by farmers to help deal with pest infestations and offer actionable advice. Your response should directly and concisely answer the question and help farmers make informed decisions to effectively manage agricultural issues for efficient and sustainable farming. Answer in paragraph form (no bullets or numbered responses).",
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
                output_file_path = os.path.join(response_category_path, f"{os.path.splitext(question_name)[0]}_Gemini_1.5_Flash.txt")
                with open(output_file_path, "w", encoding='utf-8') as output_file:
                    output_file.write(response)
                print(f"Saved response to file: {output_file_path}")

            except Exception as e:
                print(f"Error processing question {question_name}: {e}")

print("Completed processing all questions.")