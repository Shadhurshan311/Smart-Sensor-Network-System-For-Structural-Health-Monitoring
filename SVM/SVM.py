# Step 1: Import libraries
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# Step 2: Load uploaded CSV
df = pd.read_csv("C:\\Users\\94772\\Desktop\\FYP\\Samples\\sampleOneFile.csv")

# Step 3: Convert 'CrackType' to binary label
df['Label'] = df['CrackType'].map({'NonCrack': 0, 'Crack': 1})

# Step 4: Feature selection and splitting
X = df[['Capacitance(pF)', 'Humidity(%)', 'Temperature(C)', 'Thickness(mm)']]
y = df['Label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Step 5: Feature scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Step 6: GridSearchCV to find best parameters
param_grid = {
    'C': [105,106,107,108,109],
    'gamma': [21,23,25,27,29],
    'kernel': ['rbf']
}

grid = GridSearchCV(SVC(), param_grid, cv=5, scoring='accuracy', verbose=1, n_jobs=-1)
grid.fit(X_train_scaled, y_train)

# Step 7: Best model after GridSearch
best_model = grid.best_estimator_
print("\n🔍 Best Parameters Found by GridSearchCV:\n", grid.best_params_)

# Step 8: Evaluate model
y_pred = best_model.predict(X_test_scaled)

accuracy = accuracy_score(y_test, y_pred)
print(f"\n✅ Prediction Accuracy: {accuracy * 100:.2f}%")
print("\n📊 Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\n📋 Classification Report:\n", classification_report(y_test, y_pred))

# Step 9: Predict a new sample using best model
def predict_new_sample(capacitance, humidity, temperature, thickness):
    sample = [[capacitance, humidity, temperature, thickness]]
    sample_scaled = scaler.transform(sample)
    prediction = best_model.predict(sample_scaled)
    return "Crack" if prediction[0] == 1 else "NonCrack"

# Example prediction
result = predict_new_sample(920, 65, 28, 14)
print("\n🔍 Prediction for new sample:", result)