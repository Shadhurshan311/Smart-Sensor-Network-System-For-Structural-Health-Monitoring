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
if not {"x", "capacitance"}.issubset(df.columns):
    print("Excel must contain 'x' and 'capacitance'")
    exit()

# === Step 4: Extract data ===
x = df["x"].values
cap = df["capacitance"].values

# Clip capacitance to 0-200 range
cap = np.clip(cap, 0, 200)

# === Step 5: Create a 2D array for plotting as heatmap ===
# We'll just repeat the capacitance values along y-axis to make a horizontal strip
y_len = 100  # height of the strip
cap_grid = np.tile(cap, (y_len, 1))  # repeat along rows

# === Step 6: Plot continuous green heatmap ===
fig, ax = plt.subplots(figsize=(12, 5))  # narrow height for strip

# Custom green colormap
cmap = mcolors.LinearSegmentedColormap.from_list("green_scale", [(0, 0.1, 0), (0, 1, 0)])

im = ax.imshow(
    cap_grid,
    origin='lower',
    cmap=cmap,
    aspect='auto',
    extent=[x.min(), x.max(), 0, y_len],
    vmin=0,
    vmax=200,
    interpolation='bilinear' 
)

# Colorbar
cbar = fig.colorbar(im, ax=ax, orientation='horizontal')
cbar.set_label("Capacitance (0 → 200)")

# Labels and title
ax.set_xlabel("X Position along Beam")
ax.set_yticks([])  # hide y-axis
ax.set_title("Concrete Crack Pattern (Green Intensity)")

# Save PNG
save_path = os.path.join(os.path.dirname(file_path), "crack_pattern_green_strip.png")
plt.savefig(save_path, dpi=300, bbox_inches='tight')
print(f"✅ Plot saved as: {save_path}")

plt.show()