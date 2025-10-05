from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry CSV bundle (replace with your bundle path if needed)
# Example: assume a CSV file "telemetry.csv" with columns: region, latency_ms, uptime
df = pd.read_csv("telemetry.csv")  # The sample telemetry bundle

@app.post("/")
async def latency_metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold_ms = body.get("threshold_ms", 180)

    result = {}

    for region in regions:
        region_df = df[df["region"] == region]

        if region_df.empty:
            result[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0
            }
            continue

        avg_latency = region_df["latency_ms"].mean()
        p95_latency = np.percentile(region_df["latency_ms"], 95)
        avg_uptime = region_df["uptime"].mean()
        breaches = (region_df["latency_ms"] > threshold_ms).sum()

        result[region] = {
            "avg_latency": float(round(avg_latency, 2)),
            "p95_latency": float(round(p95_latency, 2)),
            "avg_uptime": float(round(avg_uptime, 2)),
            "breaches": int(breaches)
        }

    return result
