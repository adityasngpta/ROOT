import os
import requests
import json

# OpenAI API Key
api_key = "API-KEY"

# Function to get the file extension
def get_file_extension(filename):
    return os.path.splitext(filename)[1].lower()

# Function to read the content of the text file
def read_text_file(file_path):
    with open(file_path, "r", encoding='utf-8') as file:
        return file.read()

# Function to get the score from the LLM using OpenAI GPT
def get_score(question_text, description_text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": """You are an advanced analysis scorer model tasked with evaluating and scoring the quality of answers provided by an AI assistant to farmer questions about pest infestations. Your role is to assess responses based on accuracy, comprehensiveness, clarity, actionability, and relevance. You will be given:

                1. The farmer's question.
                2. The AI assistant's answer to the question.

                Use the following rubric to score the response (grade very strictly, any deviation from the criteria should result in a point deduction, only the top 10 percent of descriptions should get 9/9 and top 20 percent should get 8/9 and top 30 percent should get 7/9 rest should get 6/9 or below):

                1. Accuracy (2 points)
                    - 2 points: The answer is completely accurate with no errors or misleading information. All factual statements have been verified for correctness.
                    - 1 point: The answer has minor inaccuracies or partially correct information that does not significantly mislead. Some factual statements may lack verification.
                    - 0 points: The answer is significantly inaccurate, contains major errors, or is misleading. Factual statements are incorrect or unverified.

                2. Comprehensiveness (2 points)
                    - 2 points: The answer addresses all aspects of the question thoroughly, including potential nuances and implications.
                    - 1 point: The answer covers most aspects of the question but misses some important details or nuances.
                    - 0 points: The answer is incomplete and fails to address the main aspects of the question or overlooks significant details.

                3. Clarity (2 points)
                    - 2 points: The answer is clear, well-structured, free of ambiguity, and easy to understand.
                    - 1 point: The answer is somewhat clear but may have issues with structure, wording, or slight ambiguity that affects understanding.
                    - 0 points: The answer is unclear, poorly structured, or contains ambiguous language that makes it difficult to understand.

                4. Actionability (2 points)
                    - 2 points: The answer provides specific, practical, and actionable advice that the farmer can easily implement.
                    - 1 point: The answer offers general advice that is somewhat actionable but lacks specificity or practical details.
                    - 0 points: The answer does not provide actionable advice or is too vague to be implemented effectively.

                5. Relevance (1 point)
                    - 1 point: The answer is highly relevant to the farmer's question, directly addressing the issue at hand.
                    - 0 points: The answer is irrelevant or only tangentially related to the farmer's question.

                Use this rubric to score each response strictly, deducting points for any deviation from the specified criteria. Be especially rigorous in fact-checking all statements for accuracy.

                Your response should be formatted as follows (please strictly follow the bracketing and line formatting):

                1. Accuracy (x/2) [Justification for score]
                2. Comprehensiveness (x/2) [Justification for score]
                3. Clarity (x/2) [Justification for score]
                4. Actionability (x/2) [Justification for score]
                5. Relevance (x/1) [Justification for score]
                6. Miscellaneous (-x) [Any points subtracted and why]

                Total Score: (x/9)

                Please make sure the format of your response strictly follows the above. There must be a line with the exact text "Total Score:" followed by the total score in parentheses."""
            },
            {
                "role": "user",
                "content": f"Farmer's question: {question_text}\nAI assistant's answer: {description_text}"
            }
        ],
        "max_tokens": 512,
        "temperature": 0
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Folder containing the descriptions (relative to the script directory)
description_folder_path = os.path.join(script_dir, "answers")

# Folder containing the questions (relative to the script directory)
question_folder_path = os.path.join(script_dir, "questions")

# Output folder for the scores (relative to the script directory)
score_folder_path = os.path.join(script_dir, "scores")
os.makedirs(score_folder_path, exist_ok=True)

# Allowed text file extension
allowed_extension = '.txt'

# Iterate through each category folder
for category in os.listdir(description_folder_path):

    description_category_path = os.path.join(description_folder_path, category)
    question_category_path = os.path.join(question_folder_path, category)
    
    if os.path.isdir(description_category_path) and os.path.isdir(question_category_path):
        # Create the corresponding category folder in the scores folder
        score_category_path = os.path.join(score_folder_path, category)
        os.makedirs(score_category_path, exist_ok=True)

        # List all text files in the current category folder
        description_files = sorted([f for f in os.listdir(description_category_path) if os.path.isfile(os.path.join(description_category_path, f)) and get_file_extension(f) == allowed_extension])
        total_files = len(description_files)

        # Process each description file in the category
        for idx, description_name in enumerate(description_files):
            description_path = os.path.join(description_category_path, description_name)

            # Extract the base filename and model name to match with questions
            base_name = os.path.splitext(description_name)[0].split('_')[0]
            model_name = '_'.join(os.path.splitext(description_name)[0].split('_')[1:])
            question_path = os.path.join(question_category_path, f"{base_name}.txt")

            print(f"Processing description {idx+1}/{total_files} in category {category}: {description_name}")

            try:
                # Read the description
                description_text = read_text_file(description_path)
                
                # Read the corresponding question
                question_text = read_text_file(question_path)

                # Get the score for the description
                response = get_score(question_text, description_text)
                print(f"Received score for description: {description_name}")

                # Save the score in a text file with the model name included
                score_file_path = os.path.join(score_category_path, f"{base_name}_{model_name}-Score.txt")
                with open(score_file_path, "w", encoding='utf-8') as score_file:
                    score_file.write(response)
                print(f"Saved score to file: {score_file_path}")

            except Exception as e:
                print(f"Error processing description {description_name}: {e}")

print("Completed scoring all descriptions.")
