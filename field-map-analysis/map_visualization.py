import os
import numpy as np
from PIL import Image

def field_to_image(field, width=512):
    # Normalize the field values to the range [0, 255]
    max_intensity = 255
    normalized_field = (field / np.max(field)) * max_intensity
    # Convert to uint8 for image representation
    image = Image.fromarray(normalized_field.astype(np.uint8), 'L')
    
    # Calculate new height to maintain aspect ratio
    original_width, original_height = image.size
    new_height = int((width / original_width) * original_height)
    
    # Resize the image to the new width and calculated height
    image = image.resize((width, new_height), Image.NEAREST)
    return image

# Define the full path to the fields directory
fields_dir = '/Users/adityasengupta/Downloads/ROOT/field-map-analysis/maps'
images_dir = '/Users/adityasengupta/Downloads/ROOT/field-map-analysis/images'

# Create directory for images
os.makedirs(images_dir, exist_ok=True)

# List all field files
field_files = os.listdir(fields_dir)

# Convert each field to an image, resize, and save
for field_file in field_files:
    field_path = os.path.join(fields_dir, field_file)
    field = np.loadtxt(field_path, dtype=int)
    
    image = field_to_image(field)
    
    # Save the image
    image_path = os.path.join(images_dir, field_file.replace('.txt', '.jpg'))
    image.save(image_path)

print('Field maps have been encoded into images with a width of 256 pixels and proportional height, saved as jpg files.')
