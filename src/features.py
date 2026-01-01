from __future__ import annotations

import pandas as pd


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds time-of-day and day-of-week features using the 'from' timestamp.
    Assumes df['from'] is timezone-aware (UTC).
    """
    out = df.copy()
    out["dow"] = out["from"].dt.dayofweek  # Monday=0
    out["hour"] = out["from"].dt.hour
    out["minute"] = out["from"].dt.minute
    # Half-hour slot index in day: 0..47
    out["slot"] = (out["hour"] * 60 + out["minute"]) // 30
    return out
