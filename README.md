# AI-Powered Offset Well Knowledge & Decision Support Platform

> **Hackathon Problem Statement:** *“AI-Powered Offset Well Knowledge and Decision Support Platform for Drilling Operations”*  
> **Status:** Backend & AI Core (v1.0.0) — Ready for local demo.  
> **Data Notice:** All datasets in this repository are **SYNTHETIC** and designed specifically for demonstration and evaluation purposes. Scenarios realistically emulate Indian offshore drilling basins (Mumbai Offshore, Bassein, Tapti, Ratna, Heera, Daman, Mukta) without exposing proprietary or confidential field data.

---

## 1. Project Overview & Core Concept

When drilling in complex formations, drilling engineers must make high-stakes, time-critical decisions (e.g. managing dynamic mud losses, impending kicks, tight hole, or severe stick-slip vibrations). While machine learning is often used for black-box classification, drilling engineers need **explainable evidence and precedent**:

```
Current Well Situation (Depth, Mud Weight, Pressure, ROP, WOB, Torque, Inclination, Azimuth)
                       │
                       ▼
        Find Similar Historical Offset Wells (Standardized KNN)
                       │
                       ▼
      Retrieve Historical Drilling Experiences & Incidents
                       │
                       ▼
     Show What Happened (Drilling narrative & symptoms)
                       │
                       ▼
     Show What Action Was Taken (Mitigation, pills, pump rates)
                       │
                       ▼
     Show The Result (Outcome, stabilization, restoration)
                       │
                       ▼
 Provide Actionable Engineering Evidence for Informed Decision Support
```

**Key Distinction:** The platform does NOT just issue a generic warning. It retrieves **exact historical precedent**, compares operational parameters transparently, and displays what engineers previously did and whether that action succeeded.

---

## 2. Technology Stack

- **Language:** Python 3.11+
- **Web Framework:** FastAPI (RESTful API, asynchronous ASGI, auto-generated interactive OpenAPI/Swagger documentation)
- **Database:** SQLite (Embedded, zero-setup relational storage with foreign key constraints)
- **Data Processing:** pandas & NumPy
- **Machine Learning & AI:** scikit-learn (`StandardScaler`, `NearestNeighbors` / KNN), joblib
- **Testing:** pytest & httpx (`TestClient`)

---

## 3. Repository Architecture

```text
AIML_Welldrilling/
├── dataset/
│   ├── README_DATASET.md          # Synthetic data notice (500 wells, 1,779 events)
│   ├── wells.csv                  # 500 historical offset wells across 7 Indian offshore fields
│   └── drilling_events.csv        # 1,779 historical events (lost circulation, kicks, tight hole, etc.)
├── backend/
│   ├── main.py                    # FastAPI application, routing, CORS, and lifecycle events
│   ├── database.py                # SQLite schema management, seeding, and query methods
│   ├── models.py                  # Pydantic data schemas for requests and responses
│   ├── similarity.py              # Explainable AI similarity engine & event retrieval
│   ├── requirements.txt           # Python dependencies
│   └── drilling_knowledge.db      # SQLite database (500 wells & 1,779 events)
├── frontend/
│   ├── index.html                 # Single-page web application structure
│   ├── style.css                  # Professional engineering light dashboard styles
│   └── app.js                     # State management, API integration, and rendering
├── scripts/
│   ├── generate_synthetic_data.py # Reproducible synthetic data generation script (500 wells)
│   └── test_live_api.py           # Live client verification script
├── tests/
│   └── test_backend.py            # Automated test suite (all endpoints & AI engine)
└── README.md                      # Project documentation
```

---

## 4. How the AI Similarity & Experience Retrieval Works

### 1. Feature Representation
The AI engine evaluates 8 standardized operational and geometric drilling parameters:
- `total_depth` ($m$): Planned / measured depth
- `mud_weight` ($ppg$): Drilling fluid density
- `pressure` ($psi$): Estimated formation / pore pressure
- `rop` ($m/hr$): Rate of penetration
- `wob` ($klbs$): Weight on bit
- `torque` ($kft\cdot lb$): Rotary drillstring torque
- `inclination` ($^\circ$): Well trajectory inclination
- `azimuth` ($^\circ$): Well compass direction

### 2. Standardization
Drilling parameters vary widely in scale (e.g. pressure ~ 5,000 psi vs. mud weight ~ 11 ppg). We use `StandardScaler` to transform each feature into standard $z$-scores ($z = \frac{x - \mu}{\sigma}$), ensuring equal weighting and preventing large-magnitude parameters from dominating the distance metric.

### 3. Euclidean Distance & Similarity Metric
Using `NearestNeighbors(metric='euclidean')`, distance $d \ge 0$ is computed between the standardized current well vector and candidate offset wells. To provide an intuitive, explainable ranking for engineers without arbitrary heuristics, distance is converted into similarity percentage using:

$$\text{Similarity (\%)} = \frac{100.0}{1.0 + 0.35 \times d}$$

- At $d = 0.0$ (identical parameters): **100.0%**
- At $d = 0.2$ (extremely close offset): **93.4%**
- At $d = 1.0$ (moderate variation): **74.0%**
- Monotonic, strictly bounded between 0% and 100%.

### 4. Explainability & Matching Factors
For each matched well, the engine provides:
- A per-parameter breakdown comparing **Current Value vs. Matched Value** and delta.
- Qualitative match quality rating (`Strong Match`, `Close Match`, `Moderate Difference`).
- Top key matching factors highlighting which parameters most closely align.

### 5. Historical Event Retrieval
After identifying the top-$k$ nearest offset wells, the system queries the relational SQLite database for all historical events associated with those wells. Events are annotated with:
- Well identifier and well similarity percentage
- Event depth and proximity to current drilling depth
- Event classification (e.g., *Lost Circulation*, *Gas Kick*, *Tight Hole*, *Differential Sticking*)
- Operational description (what happened)
- Immediate action taken (e.g., LCM pill recipe, BOP shut-in procedure, freeing soak)
- Recorded result (e.g., returns restored, well killed, pipe freed)
- Synthesized engineering evidence summary and actionable mitigation insights

---

## 5. Quickstart & Setup Instructions

### Prerequisites
- Python 3.10+ (Python 3.11 recommended)
- Git (optional)

### Step 1: Create and Activate Virtual Environment
```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 3: Run the Backend
```bash
# Windows / Linux / macOS
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
Once started, the interactive API documentation (Swagger UI) is available at:
👉 **http://127.0.0.1:8000/docs**

### Step 4: Run the Frontend UI
```bash
# Windows / Linux / macOS (serve on port 3000)
python -m http.server 3000 --directory frontend
```
Open your browser and navigate to:
👉 **http://127.0.0.1:3000**

---

## 6. Running Tests

Run the comprehensive pytest suite:
```bash
pytest -v tests/test_backend.py
```
This tests:
- `GET /api/health`
- `GET /api/wells` (with and without field filters)
- `GET /api/wells/{well_id}` (success and 404 handling)
- `GET /api/wells/{well_id}/events`
- `POST /api/similar-wells` (verifying 8-feature parameter breakdown and similarity scores)
- `POST /api/experience-search` (verifying full knowledge retrieval and precedent extraction)

---

## 7. Sample API Requests & Responses

### 1. Health Check
**Request:**
```bash
GET /api/health
```
**Response:**
```json
{
  "status": "healthy",
  "wells_count": 28,
  "events_count": 32,
  "is_synthetic": true,
  "data_notice": "Synthetic dataset simulating Indian offshore drilling operations (Mumbai Offshore, Bassein, Tapti, Ratna, Heera, Daman, Mukta)."
}
```

---

### 2. Find Similar Offset Wells
**Request:**
```bash
POST /api/similar-wells
Content-Type: application/json

{
  "total_depth": 3460.0,
  "mud_weight": 11.3,
  "pressure": 4270.0,
  "rop": 12.0,
  "wob": 16.5,
  "torque": 13.8,
  "inclination": 15.0,
  "azimuth": 212.0,
  "top_k": 2
}
```

**Response (excerpt):**
```json
{
  "query_parameters": {
    "total_depth": 3460.0,
    "mud_weight": 11.3,
    "pressure": 4270.0,
    "rop": 12.0,
    "wob": 16.5,
    "torque": 13.8,
    "inclination": 15.0,
    "azimuth": 212.0
  },
  "total_candidates": 28,
  "top_k": 2,
  "similar_wells": [
    {
      "well_id": "MO-B-101",
      "field": "Mumbai Offshore",
      "formation": "Bassein Limestone",
      "similarity": 95.7,
      "distance": 0.128,
      "total_depth": 3450.0,
      "mud_weight": 11.2,
      "pressure": 4250.0,
      "rop": 12.5,
      "wob": 16.0,
      "torque": 13.5,
      "inclination": 14.5,
      "azimuth": 210.0,
      "key_matching_factors": [
        "Weight on Bit (WOB): matched 16.0 vs current 16.5 klbs (-0.5 klbs)",
        "Drilling Torque: matched 13.5 vs current 13.8 kft-lb (-0.3 kft-lb)",
        "Formation Pressure: matched 4250.0 vs current 4270.0 psi (-20.0 psi)"
      ],
      "event_count": 2
    }
  ],
  "explanation": "Compared current parameters against historical offset wells using 8 standardized drilling features..."
}
```

---

### 3. Retrieve Historical Drilling Experiences & Evidence
**Request:**
```bash
POST /api/experience-search
Content-Type: application/json

{
  "total_depth": 3000.0,
  "mud_weight": 12.9,
  "pressure": 5500.0,
  "rop": 21.5,
  "wob": 21.8,
  "torque": 15.7,
  "inclination": 36.0,
  "azimuth": 142.0,
  "top_k": 2,
  "current_depth": 2750.0
}
```

**Response (excerpt):**
```json
{
  "query_parameters": {
    "total_depth": 3000.0,
    "mud_weight": 12.9,
    "pressure": 5500.0,
    "rop": 21.5,
    "wob": 21.8,
    "torque": 15.7,
    "inclination": 36.0,
    "azimuth": 142.0
  },
  "similar_wells": [
    {
      "well_id": "TP-D-301",
      "field": "Tapti",
      "formation": "Daman Sandstone",
      "similarity": 95.8,
      "distance": 0.125
    }
  ],
  "historical_experiences": [
    {
      "event_id": "EVT-1011",
      "well_id": "TP-D-301",
      "well_field": "Tapti",
      "well_formation": "Daman Sandstone",
      "well_similarity": 95.8,
      "depth": 2720.0,
      "depth_proximity": "Critical Proximity (within 30m of target depth)",
      "event_type": "Gas Kick",
      "description": "Drilling break from 12 m/hr to 32 m/hr upon entering Daman Sandstone. Pit gain of 18 bbl detected with flow check positive while pumps off.",
      "action_taken": "Space out drillpipe, shut-in well using annular BOP. Recorded SIDPP = 420 psi, SICP = 580 psi. Executed Wait & Weight well control method, raising mud weight from 12.8 ppg to 13.5 ppg kill mud.",
      "result": "Gas influx safely circulated out through choke manifold and degasser. Well confirmed dead; resumed drilling with 13.5 ppg mud."
    }
  ],
  "evidence_summary": "Identified 2 top matching offset wells with up to 95.8% similarity. Historical records show relevant drilling events in similar formations (Gas Kick). Precedents indicate key actions taken and resolved outcomes."
}
```

---

## 8. Summary of Accomplishments

1. **Zero Legacy Code / Pure Scratch Build**: Clean directory, dedicated `.venv`, lightweight FastAPI architecture.
2. **Transparent Mathematical Model**: Fully explainable KNN + StandardScaler similarity based on 8 realistic drilling features.
3. **Structured Evidence Retrieval**: Links offset wells to actionable historical events detailing *What Happened*, *Action Taken*, and *Result*.
4. **Tested & Validated**: Full test suite confirming data integrity, distance bounds, and event linkage.
## Contribution Notes

Documentation and testing improvements are welcome.