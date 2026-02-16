import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TF INFO/WARN logs

import cv2
import numpy as np
from tensorflow.keras.models import load_model

# Load trained model
best_model = load_model('best_model.h5', compile=False)

# Input image size used in training
image_size = (224, 224)

def preprocess_frame(frame):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Resize to model input size
    img = cv2.resize(gray, image_size)
    # Normalize
    img_array = img / 255.0
    # Expand dims for model input
    img_array = np.expand_dims(img_array, axis=-1)  # (224,224,1)
    img_array = np.expand_dims(img_array, axis=0)   # (1,224,224,1)
    return img_array

# Open webcam (0 = default cam)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam")
    exit()

print("Press 'q' to quit")
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Preprocess
    img_array = preprocess_frame(frame)

    # Prediction
    prediction = best_model.predict(img_array, verbose=0)
    label = 'Crack' if prediction[0][0] > 0.5 else 'Non-Crack'

    # Overlay label on frame
    cv2.putText(frame, f"Prediction: {label}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255) if label=="Crack" else (0, 255, 0), 2)

    # Show frame
    cv2.imshow("Crack Detection", frame)

    # Quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
