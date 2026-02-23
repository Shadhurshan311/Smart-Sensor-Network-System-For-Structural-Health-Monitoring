import pandas as pd
import numpy as np
import random
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler, label_binarize
from sklearn.metrics import accuracy_score, classification_report, ConfusionMatrixDisplay, roc_curve, auc
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt

# ---------- Set random seeds ----------
np.random.seed(42)
random.seed(42)

# ---------- Load and preprocess data ----------
data = pd.read_csv("C:\\Users\\94772\\Desktop\\FYP\\Samples\\sampleOneFile.csv")
data.columns = ['Capacitance', 'Humidity', 'Temperature', 'Thickness', 'Cracktype']
data.columns = data.columns.str.strip()
data = data.drop_duplicates()

label_encoder = LabelEncoder()
data['Cracktype'] = label_encoder.fit_transform(data['Cracktype'])

# ---------- Sensor data augmentation ----------
def augment_data(df, noise_level=0.01, n_copies=2):
    augmented = []
    for _ in range(n_copies):
        noisy = df.copy()
        for col in ['Capacitance', 'Humidity', 'Temperature', 'Thickness']:
            noise = np.random.normal(0, noise_level, size=len(df))
            noisy[col] = noisy[col] + noise
        augmented.append(noisy)
    return pd.concat([df] + augmented, ignore_index=True)

data_augmented = augment_data(data)

# ---------- Split features and labels ----------
X = data_augmented[['Capacitance', 'Humidity', 'Temperature', 'Thickness']].values
y = data_augmented['Cracktype'].values

# ---------- Normalize features ----------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ---------- Apply SMOTE ----------
smote = SMOTE(random_state=42)
X_balanced, y_balanced = smote.fit_resample(X_scaled, y)

# ---------- Final train-test split ----------
X_train, X_test, y_train, y_test = train_test_split(
    X_balanced, y_balanced, test_size=0.2, stratify=y_balanced, random_state=42
)

# ---------- Train final model ----------
final_model = XGBClassifier(
    learning_rate=0.1,
    max_depth=5,
    n_estimators=200,
    use_label_encoder=False,
    eval_metric='mlogloss',
    random_state=42
)

final_model.fit(X_train, y_train)
y_pred_final = final_model.predict(X_test)

# ---------- Evaluation ----------
accuracy = accuracy_score(y_test, y_pred_final)
print(f"\n🔸 Final XGBoost Accuracy: {accuracy * 100:.2f}%\n")
print("🔹 Classification Report:")
print(classification_report(y_test, y_pred_final, target_names=label_encoder.classes_))

# ---------- Confusion Matrix (Percentage) ----------
cm = confusion_matrix(y_test, y_pred_final)
cm_normalized = cm.astype('float') / cm.sum() * 100   # percentage over all samples

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm_normalized,
    display_labels=label_encoder.classes_
)

disp.plot(cmap='Greens', values_format=".2f")
plt.title("XGBoost Confusion Matrix (%)")
plt.show()

# ---------- ROC Curve ----------
n_classes = len(np.unique(y))
y_test_bin = label_binarize(y_test, classes=np.arange(n_classes))

if n_classes == 2:
    # Binary classification ROC
    y_score = final_model.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_score)
    roc_auc = auc(fpr, tpr)

    plt.figure()
    plt.plot(fpr, tpr, color='darkorange', lw=2,
             label=f"ROC curve (AUC = {roc_auc:.2f})")
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Guess')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve - XGBoost (Binary Classification)')
    plt.legend(loc="lower right")
    plt.grid(True)
    plt.show()
else:
    print("ROC curve plotting is currently set for binary classification only.")
