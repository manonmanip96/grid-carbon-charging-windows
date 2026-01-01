from __future__ import annotations

import argparse
import math
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pandas as pd

from .fetch_data import fetch_intensity
from .model import baseline_forecast_next_day
from .plot import save_forecast_plot


def iso_utc(ts: pd.Timestamp) -> str:
    # Carbon Intensity API accepts ISO timestamps; "Z" is fine
    return ts.strftime("%Y-%m-%dT%H:%MZ")


def compute_tomorrow_window_utc() -> tuple[pd.Timestamp, pd.Timestamp]:
    """
    Compute tomorrow's start/end in UTC, using UK local date (Europe/London).
    """
    uk = ZoneInfo("Europe/London")
    now_uk = datetime.now(tz=uk)
    tomorrow_uk = (now_uk + timedelta(days=1)).date()

    start_uk = datetime(tomorrow_uk.year, tomorrow_uk.month, tomorrow_uk.day, 0, 0, tzinfo=uk)
    end_uk = start_uk + timedelta(days=1)

    start_utc = pd.Timestamp(start_uk.astimezone(timezone.utc))
    end_utc = pd.Timestamp(end_uk.astimezone(timezone.utc))
    return start_utc, end_utc


def compute_history_window_utc(days: int) -> tuple[pd.Timestamp, pd.Timestamp]:
    end = pd.Timestamp(datetime.now(tz=timezone.utc)).floor("30min")
    start = end - pd.Timedelta(days=days)
    return start, end


def recommend_slots(
    forecast_df: pd.DataFrame,
    energy_kwh: float,
    power_kw: float,
) -> pd.DataFrame:
    """
    Pick the lowest predicted intensity half-hour slots until we meet required energy.
    """
    if energy_kwh <= 0 or power_kw <= 0:
        raise ValueError("energy_kwh and power_kw must be > 0.")

    energy_per_slot = power_kw * 0.5  # kWh in 30 minutes
    slots_needed = math.ceil(energy_kwh / energy_per_slot)

    df = forecast_df.copy()
    df = df.sort_values("predicted_intensity", ascending=True).reset_index(drop=True)
    df["recommended"] = False
    df.loc[: slots_needed - 1, "recommended"] = True

    # Sort back chronologically for readability
    df = df.sort_values("from").reset_index(drop=True)
    return df


def main():
    parser = argparse.ArgumentParser(description="Recommend low-carbon EV charging windows (UK grid).")
    parser.add_argument("--energy_kwh", type=float, default=20.0, help="Energy required (kWh).")
    parser.add_argument("--power_kw", type=float, default=7.0, help="Charging power (kW).")
    parser.add_argument("--history_days", type=int, default=14, help="How many days of history to use.")
    parser.add_argument("--out_csv", type=str, default="outputs/example_recommendations.csv", help="Output CSV path.")
    parser.add_argument("--out_plot", type=str, default="outputs/forecast_plot.png", help="Output plot path.")
    args = parser.parse_args()

    # Compute windows
    hist_start, hist_end = compute_history_window_utc(args.history_days)
    tmr_start, tmr_end = compute_tomorrow_window_utc()

    # Fetch history
    hist = fetch_intensity(iso_utc(hist_start), iso_utc(hist_end))

    # Baseline forecast for tomorrow
    forecast = baseline_forecast_next_day(
        history=hist,
        target_day_start_utc=tmr_start,
        target_day_end_utc=tmr_end,
        value_col="intensity_forecast",
    )

    # Recommend slots
    rec = recommend_slots(forecast, energy_kwh=args.energy_kwh, power_kw=args.power_kw)

    # Save CSV
    out = rec.copy()
    out["from"] = out["from"].dt.strftime("%Y-%m-%d %H:%M:%S%z")
    out["to"] = out["to"].dt.strftime("%Y-%m-%d %H:%M:%S%z")
    out.to_csv(args.out_csv, index=False)

    # Plot
    save_forecast_plot(rec, args.out_plot)

    # Print a quick summary
    chosen = rec[rec["recommended"]].copy()
    print(f"Recommended {len(chosen)} half-hour slots for {args.energy_kwh} kWh at {args.power_kw} kW.")
    print(chosen[["from", "to", "predicted_intensity"]].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
