import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from xgboost import XGBClassifier

# ---------- Load and preprocess training data (for fitting scaler & encoder) ----------
train_data = pd.read_csv("C:\\Users\\94772\\Desktop\\FYP\\Samples\\sampleOneFile.csv")
train_data.columns = ['Capacitance', 'Humidity', 'Temperature', 'Thickness', 'Cracktype']
train_data = train_data.drop_duplicates()

label_encoder = LabelEncoder()
train_data['Cracktype'] = label_encoder.fit_transform(train_data['Cracktype'])

X_train = train_data[['Capacitance', 'Humidity', 'Temperature', 'Thickness']].values
y_train = train_data['Cracktype'].values

# Normalize
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

# ---------- Train final model ----------
final_model = XGBClassifier(
    learning_rate=0.1,
    max_depth=5,
    n_estimators=200,
    use_label_encoder=False,
    eval_metric='mlogloss',
    random_state=42
)
final_model.fit(X_train_scaled, y_train)

import time
start_time=time.time()

# ---------- Load NEW dataset ----------
new_data = pd.read_csv("C:\\Users\\94772\\Desktop\\FYP\\Samples\\new_dataTEST.csv")
new_data.columns = ['Capacitance', 'Humidity', 'Temperature', 'Thickness']

# ---------- Preprocess new data ----------
X_new = scaler.transform(new_data.values)

# ---------- Predictions ----------
y_pred = final_model.predict(X_new)
y_proba = final_model.predict_proba(X_new)

# Decode labels back to original
predicted_labels = label_encoder.inverse_transform(y_pred)

# ---------- Show results ----------
for i, (label, probs) in enumerate(zip(predicted_labels, y_proba)):
    severity = np.max(probs) * 100   # highest probability %
    print(f"Sample {i+1}: Predicted → {label}  |  Confidence: {severity:.2f}%")

end_time=time.time()
print(f"\nTotal Runtime: {end_time - start_time:.2f}seconds")