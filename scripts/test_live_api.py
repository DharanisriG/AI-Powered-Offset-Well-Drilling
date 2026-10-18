"""
Live API Client Demonstration Script.
Executes sample requests against all endpoints and displays structured JSON responses.
"""

import sys
import json
import httpx

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000"

def pretty_print(title: str, data: dict):
    print("\n" + "=" * 80)
    print(f"[*] {title}")
    print("=" * 80)
    print(json.dumps(data, indent=2))

def run_live_tests():
    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    # 1. Health Endpoint
    res = client.get("/api/health")
    pretty_print("1. GET /api/health", res.json())

    # 2. List Wells (Filter by field)
    res = client.get("/api/wells?field=Bassein")
    pretty_print("2. GET /api/wells?field=Bassein", res.json())

    # 3. Get Single Well
    res = client.get("/api/wells/MO-B-101")
    pretty_print("3. GET /api/wells/MO-B-101", res.json())

    # 4. Get Well Historical Events
    res = client.get("/api/wells/MO-B-101/events")
    pretty_print("4. GET /api/wells/MO-B-101/events", res.json())

    # 5. Similar Wells Matching (Loss Zone Scenario)
    loss_payload = {
        "total_depth": 3480.0,
        "mud_weight": 11.3,
        "pressure": 4280.0,
        "rop": 12.2,
        "wob": 16.2,
        "torque": 13.7,
        "inclination": 14.8,
        "azimuth": 211.0,
        "top_k": 2
    }
    res = client.post("/api/similar-wells", json=loss_payload)
    pretty_print("5. POST /api/similar-wells (Loss Zone Scenario)", res.json())

    # 6. Experience Search & Evidence Retrieval (Overpressured Gas Sand Scenario)
    kick_payload = {
        "total_depth": 3020.0,
        "mud_weight": 12.9,
        "pressure": 5520.0,
        "rop": 22.0,
        "wob": 22.0,
        "torque": 15.8,
        "inclination": 37.0,
        "azimuth": 143.0,
        "top_k": 2,
        "current_depth": 2780.0
    }
    res = client.post("/api/experience-search", json=kick_payload)
    pretty_print("6. POST /api/experience-search (Overpressured Gas Sand Scenario)", res.json())

if __name__ == "__main__":
    run_live_tests()
