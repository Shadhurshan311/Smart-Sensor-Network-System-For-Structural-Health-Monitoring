import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os
import numpy as np
import matplotlib.colors as mcolors

# === Step 1: Open file dialog ===
Tk().withdraw()
file_path = askopenfilename(
    title="Select Excel file",
    filetypes=[("Excel files", "*.xlsx *.xls")]
)

if not file_path:
    print("No file selected. Exiting.")
    exit()

# === Step 2: Read Excel file ===
try:
    df = pd.read_excel(file_path)
except Exception as e:
    print("Error reading file:", e)
    exit()

# === Step 3: Check required columns ===
required_columns = {"x", "cap1", "cap2", "cap3"}
if not required_columns.issubset(df.columns):
    print(f"Excel must contain {required_columns}")
    exit()

# === Step 4: Extract data ===
x = df["x"].values
cap1 = df["cap1"].values
cap2 = df["cap2"].values
cap3 = df["cap3"].values

# Clip capacitances to 0-200 range
cap1 = np.clip(cap1, 0, 200)
cap2 = np.clip(cap2, 0, 200)
cap3 = np.clip(cap3, 0, 200)

# === Step 5: Combine capacitance values in a single array ===
# Stack cap1, cap2, cap3 horizontally
cap_combined = np.vstack([cap1, cap2, cap3]).T  # Stack capacitances as columns

# === Step 6: Create a 2D array for plotting as heatmap ===
# We now have each x value having three capacitances in a row, one for each "cap1", "cap2", "cap3"
# This makes it a 2D array with 3 rows for each x, each corresponding to a capacitance value.
y_len = 3  # We have three rows now (one for each capacitance)
x_len = len(x)  # Number of x values

# === Step 7: Plot continuous green heatmap ===
fig, ax = plt.subplots(figsize=(12, 7))  # Increase height for more rows

# Custom green colormap
cmap = mcolors.LinearSegmentedColormap.from_list("green_scale", [(0, 0.1, 0), (0, 1, 0)])

im = ax.imshow(
    cap_combined.T,  # Transpose so that x-axis corresponds to the horizontal axis
    origin='lower',
    cmap=cmap,
    aspect='auto',
    extent=[x.min(), x.max(), 0, y_len],  # Adjust the extent to reflect the capacitance values
    vmin=0,
    vmax=200,
    interpolation='bilinear'
)

# Colorbar
cbar = fig.colorbar(im, ax=ax, orientation='horizontal')
cbar.set_label("Capacitance (0 → 200)")

# Labels and title
ax.set_xlabel("X Position along Beam")
ax.set_yticks([0, 1, 2])
ax.set_yticklabels(["Cap1", "Cap2", "Cap3"])  # Label each row to show which capacitance it corresponds to
ax.set_title("Concrete Crack Pattern (Green Intensity with 3 Capacitances)")

# Save PNG
save_path = os.path.join(os.path.dirname(file_path), "crack_pattern_green_strip_v3.png")
plt.savefig(save_path, dpi=300, bbox_inches='tight')
print(f"✅ Plot saved as: {save_path}")

plt.show()


