"""Rebuild the lecture chart from the bundled USGS snapshot, not the live feed."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

root = Path(__file__).resolve().parents[1] / "weeks/week-06"
data = pd.read_csv(root / "earthquakes-snapshot.csv")
data = data[data["type"] == "earthquake"].copy()
plot_data = data.dropna(subset=["mag", "depth"])
ax = plot_data.plot.scatter(x="mag", y="depth", alpha=0.25, figsize=(7, 4.5), color="#315876")
ax.set_ylabel("Depth (km)")
ax.set_title("USGS earthquake snapshot (2025)")
plt.tight_layout()
plt.savefig(root / "snapshot-scatter.png", dpi=150)
plt.close()
