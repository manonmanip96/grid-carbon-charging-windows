from __future__ import annotations

import requests
import pandas as pd


API_BASE = "https://api.carbonintensity.org.uk"


def fetch_intensity(from_iso: str, to_iso: str, timeout: int = 30) -> pd.DataFrame:
    """
    Fetch UK carbon intensity between two ISO timestamps.
    ISO format expected: YYYY-MM-DDTHH:MMZ (UTC) or with offset.
    Returns a DataFrame with columns: ['from', 'to', 'intensity_actual', 'intensity_forecast'].
    """
    url = f"{API_BASE}/intensity/{from_iso}/{to_iso}"
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    payload = r.json()

    rows = payload.get("data", [])
    if not rows:
        raise ValueError("No data returned from Carbon Intensity API.")

    out = []
    for row in rows:
        intensity = row.get("intensity", {})
        out.append(
            {
                "from": row.get("from"),
                "to": row.get("to"),
                "intensity_actual": intensity.get("actual"),
                "intensity_forecast": intensity.get("forecast"),
            }
        )

    df = pd.DataFrame(out)
    # Parse datetimes (API returns ISO strings)
    df["from"] = pd.to_datetime(df["from"], utc=True)
    df["to"] = pd.to_datetime(df["to"], utc=True)
    return df
