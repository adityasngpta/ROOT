import os
import numpy as np
import random

def generate_cluster(size, position, intensity_range=(1, 10), cluster_size_range=(2, 3)):
    cluster_size = random.randint(*cluster_size_range)
    cluster = np.zeros(size)
    
    if position == "center":
        start_row = size[0] // 2 - 1
        start_col = size[1] // 2 - 1
    elif position == "northwest":
        start_row = 0
        start_col = 0
    elif position == "northeast":
        start_row = 0
        start_col = size[1] - cluster_size
    elif position == "southwest":
        start_row = size[0] - cluster_size
        start_col = 0
    elif position == "southeast":
        start_row = size[0] - cluster_size
        start_col = size[1] - cluster_size
    elif position == "west":
        start_row = size[0] // 2 - 1
        start_col = 0
    else:
        start_row = random.randint(0, size[0] - cluster_size)
        start_col = random.randint(0, size[1] - cluster_size)
    
    for i in range(cluster_size):
        for j in range(cluster_size):
            if start_row + i < size[0] and start_col + j < size[1]:
                cluster[start_row + i, start_col + j] = random.randint(*intensity_range)
    
    return cluster

def generate_fields(n_fields=100, sizes=[(5, 5), (6, 6), (5, 7), (7, 5)]):
    positions = ["center", "northwest", "northeast", "southwest", "southeast", "west", "random"]
    fields = []
    for _ in range(n_fields):
        size = random.choice(sizes)
        position = random.choice(positions)
        field = generate_cluster(size, position)
        fields.append((field, position))
    return fields

def analyze_field(field, position):
    max_pests = np.max(field)
    cluster_size = np.sum(field > 0)
    total_pests = np.sum(field)
    
    if max_pests == 0:
        analysis = "There are no pests in this field. No treatment is needed."
    elif max_pests >= 7:
        severity = "high"
        treatment = "Immediate and intensive pesticide treatment is recommended."
    elif max_pests >= 4:
        severity = "moderate"
        treatment = "Moderate pesticide treatment is recommended."
    else:
        severity = "low"
        treatment = "Light pesticide treatment or natural predators can be used."
    
    analysis = (
        f"The pest cluster is located in the {position} region of the field. "
        f"The severity of the infestation is {severity}. {treatment} "
        f"Maximum pest count: {max_pests}. Cluster size: {cluster_size}. "
        f"Total number of pests: {total_pests}. "
        f"Field size: {field.shape[0]} rows by {field.shape[1]} columns."
    )
    return analysis

# Create directories for field arrays and analyses
os.makedirs('fields', exist_ok=True)
os.makedirs('analyses', exist_ok=True)

# Generate 100 field arrays
fields = generate_fields(100)

# Analyze each field and save results
for idx, (field, position) in enumerate(fields):
    analysis = analyze_field(field, position)
    
    # Save field array to a file
    field_path = f'fields/{idx + 1}.txt'
    np.savetxt(field_path, field, fmt='%d')
    
    # Save analysis to a file
    analysis_path = f'analyses/{idx + 1}.txt'
    with open(analysis_path, 'w') as f:
        f.write(analysis)

print('Fields and analyses have been saved successfully with total number of pests included.')
