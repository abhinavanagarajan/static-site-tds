from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
import os

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry JSON relative to this file
BASE_DIR = os.path.dirname(__file__)
json_path = os.path.join(BASE_DIR, "q-vercel-latency.json")

with open(json_path) as f:
    telemetry = json.load(f)  # list of dicts with keys: region, latency_ms, uptime_pct

@app.post("/")
async def latency_metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold_ms = body.get("threshold_ms", 180)

    result = {}

    for region in regions:
        # Filter records for this region
        region_data = [r for r in telemetry if r["region"] == region]

        if not region_data:
            result[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0
            }
            continue

        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime_pct"] for r in region_data]
        breaches = sum(1 for l in latencies if l > threshold_ms)

        result[region] = {
            "avg_latency": round(float(np.mean(latencies)), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(float(np.mean(uptimes)), 2),
            "breaches": int(breaches)
        }

    return result
