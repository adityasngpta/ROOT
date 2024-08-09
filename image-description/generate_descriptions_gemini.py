import os
import google.generativeai as genai

# Configure the API key
genai.configure(api_key="API-KEY")

# Function to get the file extension
def get_file_extension(filename):
    return os.path.splitext(filename)[1].lower()

# Function to upload the image to Gemini
def upload_to_gemini(image_path, mime_type=None):
    file = genai.upload_file(image_path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

# Function to get the response from Gemini
def get_response(file):
    try:
        chat_session = model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": [
                            file,
                        ],
                    }
                ]
            )
        response = chat_session.send_message("Describe this pest image.")
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Folder containing the images (relative to the script directory)
folder_path = os.path.join(script_dir, "images")

# Output folder for the responses (relative to the script directory)
output_folder_path = os.path.join(script_dir, "descriptions")
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
        "You are an advanced AI assistant specializing in agricultural pest management, tasked with analyzing images provided by farmers to identify pest infestations and offer actionable advice. Your primary goal is to examine the image to detect the presence of pests and determine which of the following classes is present: Bean Leaf Beetle, Cloverworm, Dectes Stem Borer, Grape Colaspis, Grasshopper, Japanese Beetle, Northern Corn Rootworm, Southern Corn Rootworm, Stink Bug, or Western Corn Rootworm. In addition to identifying the pest, you should describe the health and condition of the background crop or plant and explain how the pest is impacting the crop. This includes detailing visible damage, changes in plant health, or potential yield loss. Based on the identified pest, provide specific recommendations for managing or controlling the infestation. This should include suggested treatments or pesticides, preventive measures to avoid future infestations, and other strategies. Your response should be clear, detailed, and actionable, aimed at helping farmers make informed decisions to effectively manage pest issues. Answer in paragraph form (no bullets or numbered responses)."
    )
)

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
                # Upload the image to Gemini
                uploaded_file = upload_to_gemini(image_path, mime_type="image/jpeg")
                print(f"Uploaded image: {image_name}")

                # Get 1 response for each image
                response = get_response(uploaded_file.uri)
                print(f"Received response for image: {image_name}")

                # Save the response in a text file with _Gemini suffix
                output_file_path = os.path.join(description_category_path, f"{os.path.splitext(image_name)[0]}_Gemini_1.5_Pro.txt")
                with open(output_file_path, "w", encoding='utf-8') as output_file:
                    output_file.write(response)
                print(f"Saved response to file: {output_file_path}")

            except Exception as e:
                print(f"Error processing image {image_name}: {e}")

print("Completed processing all images.")


