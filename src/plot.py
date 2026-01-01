from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd


def save_forecast_plot(df: pd.DataFrame, out_path: str) -> None:
    """
    Plot tomorrow's predicted intensity and highlight recommended windows.
    """
    d = df.copy()

    # Convert for plotting (matplotlib handles tz-aware, but keep it simple)
    x = d["from"].dt.tz_convert("Europe/London")
    y = d["predicted_intensity"]

    plt.figure(figsize=(12, 4))
    plt.plot(x, y)

    # Highlight recommended intervals
    rec = d[d["recommended"]]
    if not rec.empty:
        x_rec = rec["from"].dt.tz_convert("Europe/London")
        y_rec = rec["predicted_intensity"]
        plt.scatter(x_rec, y_rec)

    plt.title("Next-day baseline forecast (UK grid carbon intensity)")
    plt.xlabel("Time (UK)")
    plt.ylabel("Predicted intensity (gCO2/kWh)")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
