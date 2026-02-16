import os
import numpy as np
from PIL import Image
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from tensorflow.keras.models import load_model

# Load your trained model
best_model = load_model('best_model.h5', compile=False)

# Input image size used in training
image_size = (224, 224)

def predict_single_image(image_path):
    # Load and preprocess the image
    img = Image.open(image_path).convert('L')  # Grayscale
    img = img.resize(image_size)               # Resize
    img_array = np.array(img) / 255.0          # Normalize
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dim and channel dim together
    img_array = np.expand_dims(img_array, axis=-1)  # Add channel dimension

    # Get prediction
    prediction = best_model.predict(img_array)

    # Output result
    label = 'Crack' if prediction[0][0] > 0.5 else 'Non-Crack'
    print(f"{os.path.basename(image_path)}: {label}")
    return label

# Example usage: (change the path to your test image)
predict_single_image(r"C:\Users\gkash\Downloads\Pera\FYP\archive\Negative\19950.jpg")