import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score
import joblib

# ---------- STEP 1: Load New Data ----------
file_path = 'C:\\Users\\94772\\Desktop\\FYP\\Samples\\new_dataTEST.csv'
data = pd.read_csv(file_path)

# Clean and fix column names
data.columns = data.columns.str.strip()

# Make sure required columns exist
expected_cols = ['Capacitance', 'Humidity', 'Temperature', 'Thickness', 'CrackType']
for col in expected_cols:
    if col not in data.columns:
        raise ValueError(f"Column '{col}' is missing in the new test dataset!")

# Separate features and label
X_test = data[['Capacitance', 'Humidity', 'Temperature', 'Thickness']].values
y_test_raw = data['CrackType'].values

# ---------- STEP 2: Load Preprocessing Tools ----------
label_encoder = joblib.load('label_encoder.pkl')
scaler = joblib.load('scaler.pkl')

# Encode labels (Crack / NonCrack)
y_test = label_encoder.transform(y_test_raw)

# Normalize features using same scaler from training
X_test_scaled = scaler.transform(X_test)
X_test_tensor = torch.tensor(X_test_scaled, dtype=torch.float32)

# ---------- STEP 3: Define MLP Model Architecture ----------
class MLP(nn.Module):
    def __init__(self, input_dim=4, hidden_dim=32, output_dim=2):
        super(MLP, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, x):
        return self.model(x)

# Match the best hidden_dim from training (e.g., 32)
model = MLP(input_dim=4, hidden_dim=32, output_dim=2)

# ---------- STEP 4: Load Trained Model ----------
model.load_state_dict(torch.load('C:\\Users\\94772\\Desktop\\FYP\\PythonApp\\models\\MLP_Model.pth'))
model.eval()

# ---------- STEP 5: Predict and Evaluate ----------
with torch.no_grad():
    outputs = model(X_test_tensor)
    _, predicted = torch.max(outputs, 1)

# Calculate Accuracy
accuracy = accuracy_score(y_test, predicted.numpy())
print(f"\n✅ Accuracy on new test data: {accuracy * 100:.2f}%")

# Show few predictions
decoded_preds = label_encoder.inverse_transform(predicted.numpy())
print("\n🔎 Sample Predictions:")
for i in range(min(10, len(decoded_preds))):
    print(f"True: {y_test_raw[i]}, Predicted: {decoded_preds[i]}")
