import os
import openai
import re
import json

# OpenAI API Key
api_key = "API-KEY"

# Initialize OpenAI client
openai.api_key = api_key

def format_ground_truth(ground_truth_text):
    # Define regex patterns for each field
    patterns = {
        "region": r"The pest cluster is located in the ([\w\s]+) region",
        "severity": r"The severity of the infestation is (\w+)",
        "max_pests": r"Maximum pest count: (\d+)",
        "cluster_size": r"Cluster size: (\d+)",
        "num_pests": r"Total number of pests: (\d+)",
        "field_size": r"Field size: ([\d\s\w]+)"
    }
    
    values = {}
    
    for field, pattern in patterns.items():
        match = re.search(pattern, ground_truth_text)
        if match:
            values[field] = match.group(1).strip()
        else:
            values[field] = "Not found"
    
    return values

# Function to get the score from the LLM
def get_score(field_map_text, description_text, ground_truth_text):
    ground_truth_values = format_ground_truth(ground_truth_text)
    formatted_system_prompt = f"""You are an advanced analysis scorer model tasked with evaluating and scoring the quality of written analyses of plant pest infestation matrices based on accuracy, comprehensiveness, and actionability. Your role is to analyze reports that interpret pest distribution patterns in field matrices, assess the severity of infestations, and provide specific, data-driven recommendations for pest management and prevention.
                        To perform your evaluation, you will be given:

                        1. The analysis to score
                        2. The pest infestation matrix (field map) associated with the analysis
                        3. The ground truth data of the matrix including cluster position, severity, and key statistics

                        Use the following rubric to score the analysis (grade very strictly, any deviation from the criteria should result in a point deduction):

                        1. Pest Cluster Region (1 point)
                        - 1 point: Accurately identifies the pest cluster as located in the {ground_truth_values['region']} region.
                        - 0 points: Fails to identify the pest cluster location region correctly.

                        2. Infestation Severity (1 point)
                        - 1 point: Accurately identifies the severity of the infestation as {ground_truth_values['severity']}.
                        - 0 points: Fails to correctly determine the severity of the infestation.

                        3. Max Pest Count (1 point)
                        - 1 point: Accurately determines the most infested plant has {ground_truth_values['max_pests']} pests.
                        - 0 points: Fails to correctly determine the number of pests on the most infested plant.

                        4. Pest Cluster Size (1 point)
                        - 1 point: Accurately determines the size of the pest cluster as {ground_truth_values['cluster_size']} plants.
                        - 0 points: Fails to correctly determine the size of the pest cluster.

                        5. Total Pest Count (1 point)
                        - 1 point: Accurately determines there are {ground_truth_values['num_pests']} pests in the field.
                        - 0 points: Fails to correctly determine the total number of pests in the field.

                        6. Field Size (1 point)
                        - 1 point: Accurately determines the field size as {ground_truth_values['field_size']}.
                        - 0 points: Fails to correctly determine the field size.

                        7. Treatment Insights (3 points)
                        - 3 points: Provides highly specific, data-driven recommendations for pest management and prevention, considering all critical factors such as pest type, severity, and field conditions. The insights should be actionable and feasible within the context of the provided data.
                        - 2 points: Offers generally relevant recommendations for pest management and prevention, with minor omissions or lack of specificity. The insights should still be mostly actionable but may lack some detail.
                        - 1 point: Gives basic recommendations for pest management and prevention, which may lack depth, specificity, or direct applicability. The suggestions might be somewhat general and not entirely data-driven.
                        - 0 points: Fails to provide actionable or relevant recommendations for pest management and prevention, or the recommendations are not based on the provided data.
                        
                        For each criterion, provide a score and a brief justification for that score. Provide clear and concise justifications for each score, highlighting strengths and areas for improvement in the analysis. Your evaluation should be objective, consistent, and based solely on the information provided in the analysis and matrix, compared against the ground truth data. Additionally, include a Miscellaneous category to deduct points for any significant errors, omissions, or irrelevant information not covered in the above criteria.
                        Your response should be formatted as follows (please strictly follow the bracketing and line formatting):

                        1. Pest Cluster Region (x/1) [Justification for score]
                        2. Infestation Severity (x/1) [Justification for score]
                        3. Max Pest Count (x/1) [Justification for score]
                        4. Pest Cluster Size (x/1) [Justification for score]
                        5. Total Pest Count (x/1) [Justification for score]
                        6. Field Size (x/1) [Justification for score]
                        7. Treatment Insights (x/3) [Justification for score]
                        8. Miscellaneous (-x) [Any points subtracted and why]

                        Total Score: (x/9)
                        
                        Please make sure the format of your response strictly follows the above. There must be a line with the exact text "Total Score:" followed by the total score in parentheses."""
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": formatted_system_prompt},
            {"role": "user", "content": f"Description to score: {description_text}"},
            {"role": "user", "content": f"Original field map/matrix: {field_map_text}"}
        ],
        max_tokens=512,
        temperature=0
    )
    
    return response.choices[0].message['content']

# Function to format the response
def format_response(response):
    return response if isinstance(response, str) else json.dumps(response, indent=2)

# Function to get the file extension
def get_file_extension(filename):
    return os.path.splitext(filename)[1].lower()

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Folder containing the descriptions (relative to the script directory)
description_folder_path = os.path.join(script_dir, "analyses")

# Folder containing the field maps (relative to the script directory)
field_map_folder_path = os.path.join(script_dir, "fields")

# Folder containing the ground truth (relative to the script directory)
ground_truth_folder_path = os.path.join(script_dir, "ground truth")

# Output folder for the scores (relative to the script directory)
score_folder_path = os.path.join(script_dir, "scores")
os.makedirs(score_folder_path, exist_ok=True)

# Allowed text file extension
allowed_extension = '.txt'

# Iterate through each category folder
for category in os.listdir(description_folder_path):
    description_category_path = os.path.join(description_folder_path, category)
    
    if os.path.isdir(description_category_path):
        # Create the corresponding category folder in the scores folder
        score_category_path = os.path.join(score_folder_path, category)
        os.makedirs(score_category_path, exist_ok=True)

        # List all text files in the current category folder
        description_files = sorted([f for f in os.listdir(description_category_path) if os.path.isfile(os.path.join(description_category_path, f)) and get_file_extension(f) == allowed_extension])
        total_files = len(description_files)

        # Process each description file in the category
        for idx, description_name in enumerate(description_files):
            description_path = os.path.join(description_category_path, description_name)
            field_map_name = description_name.split('_')[0] + '.txt'  # Extract field map name from description filename
            field_map_path = os.path.join(field_map_folder_path, category, field_map_name)
            ground_truth_path = os.path.join(ground_truth_folder_path, category, field_map_name)

            print(f"Processing description {idx+1}/{total_files} in category {category}: {description_name}")
            print(f"Description file path: {description_path}")
            print(f"Field map file path: {field_map_path}")
            print(f"Ground truth file path: {ground_truth_path}")

            try:
                # Read the description
                with open(description_path, "r", encoding='utf-8') as file:
                    description_text = file.read()

                # Read the corresponding field map text
                if os.path.exists(field_map_path):
                    with open(field_map_path, "r", encoding='utf-8') as file:
                        field_map_text = file.read()
                else:
                    print(f"Field map file not found: {field_map_name}")
                    field_map_text = None
                
                # Read the ground truth data
                if os.path.exists(ground_truth_path):
                    with open(ground_truth_path, "r", encoding='utf-8') as file:
                        ground_truth_text = file.read()
                        ground_truth_values = format_ground_truth(ground_truth_text)
                        print(f"Ground truth values: {ground_truth_values}")
                else:
                    print(f"Ground truth file not found: {field_map_name}")
                    ground_truth_text = None
                
                # Call the GPT model
                if field_map_text and ground_truth_text:
                    score_result = get_score(field_map_text, description_text, ground_truth_text)
                    formatted_result = format_response(score_result)

                    # Write the score to a new file in the scores folder
                    score_file_name = f"{description_name.split('_')[0]}_GPT-4-Score.txt"
                    score_file_path = os.path.join(score_category_path, score_file_name)
                    with open(score_file_path, "w", encoding='utf-8') as file:
                        file.write(formatted_result)

                    print(f"Score file created: {score_file_name}")
                else:
                    print(f"Missing field map or ground truth data for {description_name}. Skipping.")
                    
            except Exception as e:
                print(f"Error processing {description_name}: {str(e)}")
