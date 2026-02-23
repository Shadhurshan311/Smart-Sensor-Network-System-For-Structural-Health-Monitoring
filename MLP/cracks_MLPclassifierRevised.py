import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import random
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, ConfusionMatrixDisplay

# ---------- Set random seeds ----------
torch.manual_seed(42)
np.random.seed(42)
random.seed(42)

# ---------- Load and clean data ----------
data = pd.read_csv("C:\\Users\\94772\\Desktop\\FYP\\Samples\\First500.csv")
data.columns = ['Capacitance', 'Humidity', 'Temperature', 'Thickness', 'CrackType']
data.columns = data.columns.str.strip()
data = data.drop_duplicates()

# ---------- Encode labels ----------
label_encoder = LabelEncoder()
data['CrackType'] = label_encoder.fit_transform(data['CrackType'])

# ---------- Feature & Label Setup ----------
X = data[['Capacitance', 'Humidity', 'Temperature', 'Thickness']].values
y = data['CrackType'].values

# ---------- Optional: Visualize feature separation ----------
df = pd.DataFrame(X, columns=['Capacitance', 'Humidity', 'Temperature', 'Thickness'])
df['CrackType'] = y
sns.pairplot(df, hue='CrackType', palette='Set2', diag_kind='kde')
plt.suptitle(" Feature Separation by Crack Type", y=1.02)
plt.show()

# ---------- Grid Search Parameters ----------
param_grid = {
    'lr': [0.1,0.01,0.001],
    'hidden_dim': [5,16,32]
}

kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

best_score = 0
best_params = {}

# ---------- Grid Search with 5-Fold CV ----------
for lr in param_grid['lr']:
    for hidden_dim in param_grid['hidden_dim']:
        fold_accuracies = []

        for fold, (train_idx, val_idx) in enumerate(kfold.split(X, y)):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]

            # Fit scaler only on training set
            scaler = StandardScaler()
            X_train = scaler.fit_transform(X_train)
            X_val = scaler.transform(X_val)

            # Convert to torch tensors
            X_train = torch.tensor(X_train, dtype=torch.float32)
            X_val = torch.tensor(X_val, dtype=torch.float32)
            y_train = torch.tensor(y_train, dtype=torch.long)
            y_val = torch.tensor(y_val, dtype=torch.long)

            # Define MLP model
            model = nn.Sequential(
                nn.Linear(4, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, len(np.unique(y)))
            )

            loss_fn = nn.CrossEntropyLoss()
            optimizer = torch.optim.Adam(model.parameters(), lr=lr)

            # Train
            for epoch in range(300):
                model.train()
                y_pred = model(X_train)
                loss = loss_fn(y_pred, y_train)

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            # Validate
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

# ---------- Final Training on Best Params ----------
print("\nBest Hyperparameters:", best_params)

# Final stratified split
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.1, random_state=4)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

X_train = torch.tensor(X_train, dtype=torch.float32)
X_test = torch.tensor(X_test, dtype=torch.float32)
y_train = torch.tensor(y_train, dtype=torch.long)
y_test = torch.tensor(y_test, dtype=torch.long)

# Final model
model = nn.Sequential(
    nn.Linear(4, best_params['hidden_dim']),
    nn.ReLU(),
    nn.Linear(best_params['hidden_dim'], best_params['hidden_dim']),
    nn.ReLU(),
    nn.Linear(best_params['hidden_dim'], len(np.unique(y)))
)
optimizer = torch.optim.Adam(model.parameters(), lr=best_params['lr'])
loss_fn = nn.CrossEntropyLoss()

# Train
for epoch in range(200):
    model.train()
    y_pred = model(X_train)
    loss = loss_fn(y_pred, y_train)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if epoch % 50 == 0:
        acc = (torch.argmax(y_pred, dim=1) == y_train).float().mean().item()
        print(f"Epoch {epoch}, Loss: {loss.item():.4f}, Accuracy: {acc*100:.2f}%")


# ---------- Evaluate ----------
model.eval()
with torch.no_grad():
    y_pred_test = model(X_test)
    predicted_classes = torch.argmax(y_pred_test, dim=1)

    acc = (predicted_classes == y_test).float().mean().item()
    print(f"\n Final Test Accuracy: {acc*100:.2f}%")

    print("\nClassification Report:")
    print(classification_report(y_test, predicted_classes, target_names=label_encoder.classes_))

    cm = confusion_matrix(y_test.numpy(), predicted_classes.numpy())
    ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=label_encoder.classes_).plot(cmap='Oranges')
    plt.title("Confusion Matrix (MLP Model)")
    plt.show()
