import os
import shutil
import pandas as pd

# Define dataset directory
DATASET_DIR = "Dataset"  # Update with actual dataset path
TEST_DIR = os.path.join(DATASET_DIR, "test")  # Test images directory
CSV_FILE = os.path.join(TEST_DIR, "_classes.csv")  # CSV file

# Read CSV file
df = pd.read_csv(CSV_FILE)

# Class labels from CSV
CLASS_NAMES = ["ballooning", "fibrosis", "inflammation", "steatosis"]

# Process each image
for _, row in df.iterrows():
    image_name = row.iloc[0].strip()  # First column is image filename
    class_values = row.iloc[1:].astype(int).tolist()  # Class labels (binary)

    # Find the class where the value is 1
    for i, value in enumerate(class_values):
        if value == 1:
            class_name = CLASS_NAMES[i]
            class_folder = os.path.join(TEST_DIR, class_name)

            # Create class folder if it doesn't exist
            os.makedirs(class_folder, exist_ok=True)

            # Define source and destination paths
            src_path = os.path.join(TEST_DIR, image_name)
            dest_path = os.path.join(class_folder, image_name)

            # Copy image if it exists
            if os.path.exists(src_path):
                shutil.copy2(src_path, dest_path)  # Copy instead of move
                print(f"Copied: {image_name} → {class_folder}")
            else:
                print(f"⚠️ Warning: {image_name} not found!")

print("✅ Test data copied successfully!")
