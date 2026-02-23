import pandas as pd
import numpy as np
import joblib
import serial
import time
from sklearn.preprocessing import LabelEncoder, StandardScaler
from xgboost import XGBClassifier

# ---------------- Load and preprocess training dataset ----------------
train_data = pd.read_csv("C:\\Users\\94772\\Desktop\\FYP\\Samples\\sampleOneFile.csv")
train_data.columns = ['Capacitance', 'Humidity', 'Temperature', 'Thickness', 'Cracktype']
train_data = train_data.drop_duplicates()

# Encode labels
label_encoder = LabelEncoder()
train_data['Cracktype'] = label_encoder.fit_transform(train_data['Cracktype'])

# Features and labels
X_train = train_data[['Capacitance', 'Humidity', 'Temperature', 'Thickness']].values
y_train = train_data['Cracktype'].values

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

# Train model (only once here; later we’ll save it)
final_model = XGBClassifier(
    learning_rate=0.1,
    max_depth=5,
    n_estimators=200,
    eval_metric='mlogloss',
    random_state=42
)
final_model.fit(X_train_scaled, y_train)

# ---------------- Save trained objects (do this once) ----------------
joblib.dump(final_model, "xgboost_model.pkl")
joblib.dump(scaler, "scaler.pkl")
joblib.dump(label_encoder, "label_encoder.pkl")

# ---------------- Load trained objects ----------------
final_model = joblib.load("xgboost_model.pkl")
scaler = joblib.load("scaler.pkl")
label_encoder = joblib.load("label_encoder.pkl")

# ---------------- Function for real-time prediction ----------------
def predict_realtime(capacitance, humidity, temperature, thickness):
    sample = np.array([[capacitance, humidity, temperature, thickness]])
    sample_scaled = scaler.transform(sample)

    y_pred = final_model.predict(sample_scaled)
    y_proba = final_model.predict_proba(sample_scaled)

    label = label_encoder.inverse_transform(y_pred)[0]
    severity = np.max(y_proba) * 100

    return f"Prediction: {label} | Confidence: {severity:.2f}%"

# ---------------- Setup Serial Connection ----------------
# Change 'COM3' to your Arduino/ESP port, and 9600 to your baud rate
ser = serial.Serial('COM6', 9600, timeout=1)
time.sleep(2)

print("🔵 Real-time crack detection started... (Press CTRL+C to stop)\n")

try:
    while True:
        line = ser.readline().decode().strip()
        if line:
            try:
                # Expecting: capacitance,humidity,temperature,thickness
                c, h, t, th = map(float, line.split(","))
                result = predict_realtime(c, h, t, th)
                print(result)

            except Exception as e:
                print(f"⚠️ Invalid sensor data: {line} | Error: {e}")

except KeyboardInterrupt:
    print("\n⏹️ Real-time prediction stopped by user.")
    ser.close()



