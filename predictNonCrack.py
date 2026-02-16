import os
import random
from PIL import Image
import numpy as np
from tensorflow.keras.models import load_model

# Load trained model
best_model = load_model('best_model.h5')

# Image settings
image_size = (224, 224)

def predict_random_images(folder_path, num_images=200):
    all_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if len(all_files) == 0:
        print("No images found in the folder.")
        return

    # Randomly select 200 or fewer if not enough
    selected_files = random.sample(all_files, min(num_images, len(all_files)))

    positive_count = 0

    for filename in selected_files:
        img_path = os.path.join(folder_path, filename)
        img = Image.open(img_path).convert('L')  # Convert to grayscale
        img = img.resize(image_size)
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=-1)  # Add channel dimension
        img_array = np.expand_dims(img_array, axis=0)   # Add batch dimension

        prediction = best_model.predict(img_array, verbose=0)
        label = 'Positive' if prediction[0][0] > 0.5 else 'Negative'

        if label == 'Positive':
            positive_count += 1

        print(f"{filename}: {label}")

    total = len(selected_files)
    percentage = (positive_count / total) * 100
    print(f"\nTotal images predicted: {total}")
    print(f"Positive images: {positive_count}")
    print(f"Percentage Positive: {percentage:.2f}%")

# 📌 Call this function
predict_random_images(r'C:\Users\gkash\Downloads\Pera\FYP\archive1\Negative')

