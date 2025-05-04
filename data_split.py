import os
import shutil
import pandas as pd
import numpy as np

n_clients = 4

dataset_path = "Dataset"
splits = ["train", "test", "valid"]  
clients = [f"client_{i+1}" for i in range(n_clients)] 

for client in clients:
    for split in splits:
        os.makedirs(os.path.join(client, split), exist_ok=True)

def distribute_images(split):
    csv_path = os.path.join(dataset_path, split, "_classes.csv")

    if not os.path.exists(csv_path):
        print(f"CSV file missing for {split} dataset!")
        return

    
    df = pd.read_csv(csv_path)
    class_names = df.columns[1:] 
    image_class_mapping = {class_name: [] for class_name in class_names}

    for _, row in df.iterrows():
        image_name = row.iloc[0]
        labels = row.iloc[1:].values

        for i, label in enumerate(labels):
            if label == 1: 
                image_class_mapping[class_names[i]].append(image_name)

 
    for class_name, images in image_class_mapping.items():
        np.random.shuffle(images) 
        split_images = np.array_split(images, n_clients)

        for i, client in enumerate(clients):
            class_dir = os.path.join(client, split, class_name)
            os.makedirs(class_dir, exist_ok=True)

            for img in split_images[i]:
                img_src = os.path.join(dataset_path, split, img)
                img_dest = os.path.join(class_dir, img)

                if os.path.exists(img_src):
                    shutil.copy(img_src, img_dest)  
                else:
                    print(f"Warning: {img_src} not found!")
for split in splits:
    distribute_images(split)

print("Dataset successfully distributed among clients!")
