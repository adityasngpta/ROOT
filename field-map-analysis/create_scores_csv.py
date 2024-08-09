import os
import pandas as pd

# Define paths
script_dir = os.path.dirname(os.path.abspath(__file__))
images_folder = os.path.join(script_dir, "fields")
scores_folder = os.path.join(script_dir, "scores")

def extract_total_score(text):
    # Split the text into lines
    lines = text.split('\n')
    
    # Loop through each line to find the "Total Score" line
    for line in lines:
        if "Total Score:" in line:
            # Extract the score by splitting the line
            parts = line.split(':')
            if len(parts) > 1:
                # Extract the score part and clean it up
                score_part = parts[1].strip()
                if '/' in score_part:
                    score = score_part.split('/')[0][1:]
                    try:
                        return int(score)
                    except ValueError:
                        return None
    # If the "Total Score" line is not found, return None
    return None

# Initialize list for storing rows of data
data = []

# Define columns (make sure this matches the number of models you're handling)
columns = ["Map", "Claude 3.5 Sonnet", "Claude 3 Haiku", "Claude 3 Opus", "GPT-4 Turbo", "GPT-4o Mini", "GPT-4o", "Gemini 1.5 Flash", "Gemini 1.5 Pro"]

# Walk through subdirectories and files in the images folder
for root, dirs, files in os.walk(images_folder):
    for image_file in files:
        if image_file.endswith('.txt') and not image_file.startswith('.'):
            # Get the full path of the image file
            image_path = os.path.join(root, image_file)
            
            # Extract the base name without the file extension
            base_name = os.path.splitext(image_file)[0]
            
            # Prepare the row data with relative path
            relative_path = os.path.relpath(image_path, script_dir)
            row = [relative_path]
            
            # Determine the current subfolder to match with scores
            subfolder = os.path.basename(root)
            
            print(f"Processing image: {relative_path}")
            
            # Read corresponding score files
            for model in columns[1:]:  # Skip the first column (Image)
                score_filename = f"{base_name}_{model.replace(' ', '_')}-Score.txt"
                score_file = os.path.join(scores_folder, subfolder, score_filename)
                
                if os.path.isfile(score_file):
                    print(f"Reading score file: {score_file}")
                    with open(score_file, 'r', encoding='utf-8') as file:
                        score = extract_total_score(file.read().strip())
                        print(score)
                        row.append(score)
                else:
                    print(f"Score file not found: {score_file}")
                    row.append(None)
            
            # Check if row has correct number of columns
            if len(row) != len(columns):
                print(f"Warning: Skipping row for {relative_path}. Row length ({len(row)}) does not match columns length ({len(columns)}).")
                continue
            
            data.append(row)

# Create DataFrame
df = pd.DataFrame(data, columns=columns)

# Calculate the average score for each column
average_scores = df.iloc[:, 1:].mean()

# Append average scores to DataFrame
average_scores_row = pd.DataFrame([['Average'] + average_scores.tolist()], columns=columns)
df = pd.concat([df, average_scores_row], ignore_index=True)

# Save DataFrame to CSV
output_path = os.path.join(script_dir, "Description_Scores.csv")
df.to_csv(output_path, index=False)

print(f"CSV file created successfully at {output_path}")
print("Average scores for each column:")
print(average_scores)
