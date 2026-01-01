from __future__ import annotations

import pandas as pd
import numpy as np

from .features import add_time_features


def baseline_forecast_next_day(
    history: pd.DataFrame,
    target_day_start_utc: pd.Timestamp,
    target_day_end_utc: pd.Timestamp,
    value_col: str = "intensity_forecast",
) -> pd.DataFrame:
    """
    Baseline forecast:
    Predict intensity for each half-hour slot tomorrow using the mean intensity for the same slot
    over the historical window.

    - history: dataframe containing timestamps and intensity values
    - target_day_start_utc / end: inclusive-exclusive window for tomorrow (UTC)
    - value_col: which column to use from history (forecast is usually always populated)

    Returns: DataFrame with ['from','to','predicted_intensity'] for tomorrow.
    """
    hist = history.copy()

    # Choose the best available signal: fallback to actual if forecast missing
    if value_col not in hist.columns:
        raise ValueError(f"Missing {value_col} in history.")
    hist["value"] = hist[value_col]
    if hist["value"].isna().all() and "intensity_actual" in hist.columns:
        hist["value"] = hist["intensity_actual"]

    hist = hist.dropna(subset=["value"])
    hist = add_time_features(hist)

    # Mean by half-hour slot
    slot_means = hist.groupby("slot")["value"].mean()

    # Build the tomorrow timeline (48 half-hour slots)
    times = pd.date_range(
        start=target_day_start_utc,
        end=target_day_end_utc,
        freq="30min",
        inclusive="left",
        tz="UTC",
    )

    df_tomorrow = pd.DataFrame({"from": times})
    df_tomorrow["to"] = df_tomorrow["from"] + pd.Timedelta(minutes=30)

    df_tomorrow = add_time_features(df_tomorrow)
    df_tomorrow["predicted_intensity"] = df_tomorrow["slot"].map(slot_means)

    # Fallback if some slots missing (e.g., sparse history)
    overall_mean = float(hist["value"].mean()) if len(hist) else np.nan
    df_tomorrow["predicted_intensity"] = df_tomorrow["predicted_intensity"].fillna(overall_mean)

    return df_tomorrow[["from", "to", "predicted_intensity"]]
