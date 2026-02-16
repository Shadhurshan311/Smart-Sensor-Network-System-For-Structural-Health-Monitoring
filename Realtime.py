import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from PIL import Image
import numpy as np
from tensorflow.keras.models import load_model

# Load your trained model

best_model = load_model('best_model.h5',compile=False)



# Input image size used in training
image_size = (224, 224)

def predict_single_image(image_path):
    # Load and preprocess the image
    img = Image.open(image_path).convert('L')   # Grayscale
    img = img.resize(image_size)               # Resize
    img_array = np.array(img) / 255.0          # Normalize
    img_array = np.expand_dims(img_array, axis=-1)  # Add channel dim
    img_array = np.expand_dims(img_array, axis=0)   # Add batch dim

    # Get prediction
    prediction = best_model.predict(img_array)

    # Output result
    label = 'Crack' if prediction[0][0] > 0.5 else 'Non-Crack'
    print(f"{os.path.basename(image_path)}: {label}")
    return label

# Example usage: (change the path to your test image)
predict_single_image(r"C:\Users\gkash\Downloads\Pera\FYP\archive\Positive\19673.jpg")
