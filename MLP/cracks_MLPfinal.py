import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import random
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report,
    precision_score,
    recall_score,
    f1_score,
    ConfusionMatrixDisplay
)

# ---------- Set random seeds ----------
torch.manual_seed(42)
np.random.seed(42)
random.seed(42)

# ---------- Load and clean data ----------
data = pd.read_csv("C:\\Users\\94772\\Desktop\\FYP\\Samples\\sampleOneFile.csv")
data.columns = ['Capacitance', 'Humidity', 'Temperature', 'Thickness', 'CrackType']
data.columns = data.columns.str.strip()
data = data.drop_duplicates()

# ---------- Encode labels ----------
label_encoder = LabelEncoder()
data['CrackType'] = label_encoder.fit_transform(data['CrackType'])

# ---------- Visualize Pairplot ----------
sns.pairplot(data, hue="CrackType", diag_kind="kde", palette="husl")
plt.suptitle("Pairplot of Features by Crack Type", y=1.02)
plt.show()

# ---------- Data Augmentation ----------
def add_noise(df, noise_level=0.01):
    noisy_df = df.copy()
    features = ['Capacitance', 'Humidity', 'Temperature', 'Thickness']
    for feature in features:
        std = noisy_df[feature].std()
        noisy_df[feature] += np.random.normal(0, noise_level * std, size=len(df))
    return noisy_df

augmented_data = add_noise(data, noise_level=0.02)
data = pd.concat([data, augmented_data], ignore_index=True)
data.to_csv("cleaned_data.csv", index=False)

# ---------- Feature & Label Setup ----------
X = data[['Capacitance', 'Humidity', 'Temperature', 'Thickness']].values
y = data['CrackType'].values

# ---------- Hyper Parameters ----------
param_grid = {
    'lr': [0.1, 0.01, 0.001],
    'hidden_dim': [5, 16, 32]
}

# ---------- Tunable parameters ----------
cv_epochs = 600
final_epochs = 1000
dropout_rate = 0.1

# ---------- Cross-validation setup ----------
kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
best_score = 0
best_params = {}

for lr in param_grid['lr']:
    for hidden_dim in param_grid['hidden_dim']:
        fold_accuracies = []

        for fold, (train_idx, val_idx) in enumerate(kfold.split(X, y)):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]

            scaler = StandardScaler()
            X_train = scaler.fit_transform(X_train)
            X_val = scaler.transform(X_val)

            X_train = torch.tensor(X_train, dtype=torch.float32)
            X_val = torch.tensor(X_val, dtype=torch.float32)
            y_train = torch.tensor(y_train, dtype=torch.long)
            y_val = torch.tensor(y_val, dtype=torch.long)

            model = nn.Sequential(
                nn.Linear(4, hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout_rate),
                nn.Linear(hidden_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout_rate),
                nn.Linear(hidden_dim, len(np.unique(y)))
            )

            loss_fn = nn.CrossEntropyLoss()
            optimizer = torch.optim.Adam(model.parameters(), lr=lr)

            for epoch in range(cv_epochs):
                model.train()
                y_pred = model(X_train)
                loss = loss_fn(y_pred, y_train)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            model.eval()
            with torch.no_grad():
                y_val_pred = model(X_val)
                val_classes = torch.argmax(y_val_pred, dim=1)
                acc = accuracy_score(y_val.numpy(), val_classes.numpy())
                fold_accuracies.append(acc)

        avg_acc = np.mean(fold_accuracies)
        print(f"LR={lr}, Hidden={hidden_dim} → CV Accuracy: {avg_acc*100:.2f}%")

        if avg_acc > best_score:
            best_score = avg_acc
            best_params = {'lr': lr, 'hidden_dim': hidden_dim}

# ---------- Final Training ----------
print("\nBest Hyperparameters:", best_params)
print("Tunable Parameters:")
print(f"- Epochs (CV): {cv_epochs}, Epochs (Final): {final_epochs}")
print(f"- Dropout Rate: {dropout_rate}\n")

X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.1, random_state=4)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

X_train = torch.tensor(X_train, dtype=torch.float32)
X_test = torch.tensor(X_test, dtype=torch.float32)
y_train = torch.tensor(y_train, dtype=torch.long)
y_test = torch.tensor(y_test, dtype=torch.long)

model = nn.Sequential(
    nn.Linear(4, best_params['hidden_dim']),
    nn.ReLU(),
    nn.Dropout(dropout_rate),
    nn.Linear(best_params['hidden_dim'], best_params['hidden_dim']),
    nn.ReLU(),
    nn.Dropout(dropout_rate),
    nn.Linear(best_params['hidden_dim'], len(np.unique(y)))
)

optimizer = torch.optim.Adam(model.parameters(), lr=best_params['lr'])
loss_fn = nn.CrossEntropyLoss()

# ---------- Training ----------
for epoch in range(final_epochs):
    model.train()
    y_pred = model(X_train)
    loss = loss_fn(y_pred, y_train)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

# ---------- Final Evaluation ----------
model.eval()
with torch.no_grad():
    y_train_pred = model(X_train)
    y_test_pred = model(X_test)
    train_classes = torch.argmax(y_train_pred, dim=1)
    test_classes = torch.argmax(y_test_pred, dim=1)

    train_acc = accuracy_score(y_train.numpy(), train_classes.numpy())
    test_acc = accuracy_score(y_test.numpy(), test_classes.numpy())
    precision = precision_score(y_test.numpy(), test_classes.numpy())
    recall = recall_score(y_test.numpy(), test_classes.numpy())
    f1 = f1_score(y_test.numpy(), test_classes.numpy())
    train_loss = loss_fn(y_train_pred, y_train).item()
    test_loss = loss_fn(y_test_pred, y_test).item()

    print(f"\n📊 Final Performance:")
    print(f"- Train Accuracy: {train_acc*100:.2f}%")
    print(f"- Final Test Accuracy: {test_acc*100:.2f}%")
    print(f"- Precision: {precision:.4f}")
    print(f"- Recall: {recall:.4f}")
    print(f"- F1 Score: {f1:.4f}")
    print(f"- Train Loss: {train_loss:.4f}")
    print(f"- Test Loss: {test_loss:.4f}")

#-------Confusion Matrix---------------
    cm = confusion_matrix(y_test.numpy(), test_classes.numpy())
    ConfusionMatrixDisplay=    cm_percent = cm / cm.sum() * 100
    cm_percent = np.round(cm_percent, 2)

    fig, ax = plt.subplots()
    im = ax.imshow(cm_percent, cmap='Oranges')
    ax.set_xticks(np.arange(len(label_encoder.classes_)))
    ax.set_yticks(np.arange(len(label_encoder.classes_)))
    ax.set_xticklabels(label_encoder.classes_)
    ax.set_yticklabels(label_encoder.classes_)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, f"{cm_percent[i, j]}%", ha="center", va="center", color="black")

    ax.set_title("Confusion Matrix in Percentages")
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.colorbar(im)
    plt.tight_layout()
    plt.show()
