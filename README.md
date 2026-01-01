# Charging Window Recommender (UK Grid Carbon Intensity)

A lightweight Python tool that fetches UK grid carbon intensity data, produces a simple next-day forecast, and recommends low-carbon EV charging windows.

## Why
EV charging (and other flexible loads) is cheaper and greener when scheduled around low-carbon periods. This project explores a simple, explainable baseline approach.

## What it does
- Fetches half-hourly UK carbon intensity data
- Builds a baseline next-day forecast
- Recommends optimal charging windows for a given energy requirement
- Saves a CSV schedule and a forecast plot

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python src/recommend.py --energy_kwh 20 --power_kw 7
