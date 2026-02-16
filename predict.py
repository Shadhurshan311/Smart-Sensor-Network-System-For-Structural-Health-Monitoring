import os
from PIL import Image
import numpy as np
from tensorflow.keras.models import load_model

best_model = load_model('best_model.h5')

image_size = (224, 224)

def predict_all_images(folder_path):
    total_images = 0
    positive_count = 0

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            total_images += 1
            img_path = os.path.join(folder_path, filename)
            img = Image.open(img_path).convert('L')
            img = img.resize(image_size)
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=-1)  # Add channel dim
            img_array = np.expand_dims(img_array, axis=0)   # Add batch dim

            prediction = best_model.predict(img_array)
            label = 'Positive' if prediction[0][0] > 0.5 else 'Negative'
            if label == 'Positive':
                positive_count += 1

            print(f"{filename}: {label}")

    if total_images > 0:
        percentage_positive = (positive_count / total_images) * 100
        print(f"\nTotal images: {total_images}")
        print(f"Positive images: {positive_count}")
        print(f"Percentage of Positive outputs: {percentage_positive:.2f}%")
    else:
        print("No images found in the folder.")

# Run predictions
#predict_all_images('/content/drive/Shared drives/FYP/Weekly update/SAMPLES_Photos/MaterialLabbeams_July15')
predict_all_images(r'C:\Users\gkash\Downloads\Pera\FYP\crack real sample fac\crack')

