from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from functools import lru_cache
import pandas as pd
from datetime import datetime

# ---------- Load Sensor Data ----------
DATA_FILE = "sensor_data.csv"  # Path to your CSV file

df = pd.read_csv(DATA_FILE)

# Parse timestamps and remove timezone info for consistent comparison
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True).dt.tz_convert(None)

# ---------- Initialize FastAPI App ----------
app = FastAPI(title="SmartFactory Sensor Analytics API")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Cached Statistics Function ----------
@lru_cache(maxsize=128)
def get_stats_cached(location: str = None, sensor: str = None,
                     start_date: str = None, end_date: str = None):
    """Compute stats from the dataframe with caching enabled."""
    filtered = df.copy()

    # Apply filters if provided
    if location:
        filtered = filtered[filtered["location"] == location]

    if sensor:
        filtered = filtered[filtered["sensor"] == sensor]

    if start_date:
        start = pd.to_datetime(start_date, utc=True).tz_convert(None)
        filtered = filtered[filtered["timestamp"] >= start]

    if end_date:
        end = pd.to_datetime(end_date, utc=True).tz_convert(None)
        filtered = filtered[filtered["timestamp"] <= end]

    # Handle empty results
    if filtered.empty:
        return {"count": 0, "avg": None, "min": None, "max": None}

    # Compute stats
    stats = {
        "count": int(filtered["value"].count()),
        "avg": float(filtered["value"].mean()),
        "min": float(filtered["value"].min()),
        "max": float(filtered["value"].max())
    }

    return stats


# ---------- API Endpoint ----------
@app.get("/stats")
def get_stats(request: Request, response: Response,
              location: str = None, sensor: str = None,
              start_date: str = None, end_date: str = None):
    """
    Endpoint to return statistical summaries for IoT sensor data.
    Query params: location, sensor, start_date, end_date
    """

    # Check cache status before & after
    cache_before = get_stats_cached.cache_info()
    stats = get_stats_cached(location, sensor, start_date, end_date)
    cache_after = get_stats_cached.cache_info()

    # Determine if result came from cache
    if cache_after.hits > cache_before.hits:
        response.headers["X-Cache"] = "HIT"
    else:
        response.headers["X-Cache"] = "MISS"

    return {"stats": stats}


# ---------- Run the API ----------
# Use: uvicorn main:app --reload
