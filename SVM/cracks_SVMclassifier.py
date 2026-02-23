import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Load the dataset
data = pd.read_csv("C:\\Users\\94772\\Desktop\\FYP\\Samples\\sampleOneFile.csv")  

# Remove exact duplicate rows
data_cleaned = data.drop_duplicates()     # To reduce data redundancy

# Save the cleaned file if needed
data_cleaned.to_csv("cleaned_data.csv", index=False)

# Rename and strip column names
data.columns = ['Capacitance', 'Humidity', 'Temperature', 'Thickness', 'Cracktype']
data.columns = data.columns.str.strip()

# Encode labels (Crack/NonCrack → 0/1 or more)
label_encoder = LabelEncoder()
data['Cracktype'] = label_encoder.fit_transform(data['Cracktype'])  # Auto assigns 0/1

# Features and labels
X = data[['Capacitance', 'Humidity', 'Temperature', 'Thickness']].values
y = data['Cracktype'].values

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train/Test split
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report

svm_model = SVC(kernel='rbf', C=0.5, gamma='scale')  # RBF kernel
svm_model.fit(X_train, y_train)

y_pred_svm = svm_model.predict(X_test)
print("🔸 SVM Accuracy:", accuracy_score(y_test, y_pred_svm) * 100)
print("Classification Report (SVM):")
print(classification_report(y_test, y_pred_svm, target_names=label_encoder.classes_))

from sklearn.metrics import ConfusionMatrixDisplay
import matplotlib.pyplot as plt

ConfusionMatrixDisplay.from_estimator(
    svm_model,
    X_test,
    y_test,
    display_labels=label_encoder.classes_,  # Example: ['Crack', 'NonCrack']
    cmap='Greens',
    values_format='d'
)
plt.title("SVM Confusion Matrix")
plt.show()
