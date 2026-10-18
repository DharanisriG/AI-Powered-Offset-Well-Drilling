"""
FastAPI Backend Application for AI-Powered Offset Well Platform.
Provides RESTful APIs for well catalogs, explainable KNN similarity matching,
and historical drilling experience/event retrieval.
"""

from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from backend.database import (
    init_db,
    get_all_wells,
    get_well_by_id,
    get_events_by_well_id,
    get_db_stats,
    IS_SYNTHETIC_DATA,
)
from backend.models import (
    WellResponse,
    DrillingEventResponse,
    WellQuery,
    SimilarWellsResponse,
    ExperienceSearchResponse,
    HealthResponse,
)
from backend.similarity import similarity_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event handler for database initialization and model fitting."""
    print("[Startup] Initializing SQLite database and loading synthetic datasets...")
    init_db()
    print("[Startup] Fitting AI similarity engine with offset well parameters...")
    similarity_engine.fit()
    print("[Startup] AI Offset Well Platform backend ready.")
    yield
    print("[Shutdown] Shutting down AI Offset Well Platform backend.")

app = FastAPI(
    title="AI-Powered Offset Well Decision Support API",
    description=(
        "Decision support system for drilling engineers. Retrieves similar historical offset wells "
        "and previous drilling experiences/events using explainable Scikit-Learn KNN similarity. "
        "NOTE: Uses synthetic Indian offshore drilling data for hackathon demonstration."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for flexible integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["General"])
def root_info():
    """Root endpoint providing platform description and API links."""
    return {
        "platform": "AI-Powered Offset Well Knowledge and Decision Support Platform",
        "description": "Helps drilling engineers retrieve relevant historical offset well experiences based on current well parameters.",
        "docs_url": "/docs",
        "health_check": "/api/health",
        "is_synthetic_data": IS_SYNTHETIC_DATA,
        "disclaimer": "All datasets are synthetic and designed for hackathon demonstration purposes."
    }

@app.get("/api/health", response_model=HealthResponse, tags=["System"])
def get_health():
    """6. GET /api/health - Return backend status and synthetic dataset metrics."""
    stats = get_db_stats()
    return HealthResponse(
        status=stats["status"],
        wells_count=stats["wells_count"],
        events_count=stats["events_count"],
        is_synthetic=stats["is_synthetic"],
        data_notice=stats["data_notice"]
    )

@app.get("/api/wells", response_model=List[WellResponse], tags=["Wells"])
def list_wells(
    field: Optional[str] = Query(None, description="Optional filter by field name"),
    formation: Optional[str] = Query(None, description="Optional filter by geological formation")
):
    """1. GET /api/wells - Return available historical offset wells."""
    wells = get_all_wells()
    if field:
        wells = [w for w in wells if w["field"].lower() == field.lower()]
    if formation:
        wells = [w for w in wells if w["formation"].lower() == formation.lower()]
    return wells

@app.get("/api/wells/{well_id}", response_model=WellResponse, tags=["Wells"])
def get_well(well_id: str):
    """2. GET /api/wells/{well_id} - Return complete well information for a specific well."""
    well = get_well_by_id(well_id)
    if not well:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Well with ID '{well_id}' not found in database."
        )
    return well

@app.get("/api/wells/{well_id}/events", response_model=List[DrillingEventResponse], tags=["Events"])
def get_well_events(well_id: str):
    """4. GET /api/wells/{well_id}/events - Return historical drilling events for that well."""
    # Check well existence
    well = get_well_by_id(well_id)
    if not well:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Well with ID '{well_id}' not found in database."
        )
    events = get_events_by_well_id(well_id)
    return events

@app.post("/api/similar-wells", response_model=SimilarWellsResponse, tags=["Similarity"])
def find_similar_wells(query: WellQuery):
    """
    3. POST /api/similar-wells
    Input: current well parameters.
    Return:
    - top similar offset wells
    - similarity percentage (derived from model distance)
    - important matching parameters and explainability breakdown
    """
    matches, query_dict = similarity_engine.find_similar_wells(query)
    explanation = (
        f"Compared current parameters against historical offset wells using 8 standardized drilling features "
        f"(total depth, mud weight, pore pressure, ROP, WOB, torque, inclination, azimuth). "
        f"Top match '{matches[0].well_id}' exhibits {matches[0].similarity}% similarity "
        f"in the {matches[0].formation} formation."
    )
    return SimilarWellsResponse(
        query_parameters=query_dict,
        total_candidates=len(similarity_engine.wells_df) if similarity_engine.wells_df is not None else 0,
        top_k=len(matches),
        similar_wells=matches,
        explanation=explanation,
        is_synthetic=True
    )

@app.post("/api/experience-search", response_model=ExperienceSearchResponse, tags=["Experience Retrieval"])
def search_historical_experiences(query: WellQuery):
    """
    5. POST /api/experience-search
    Input: current well parameters.
    Return:
    - similar historical wells
    - relevant historical drilling events
    - event depth, event type, description, action taken, result
    - engineering evidence summary
    """
    result = similarity_engine.search_experiences(query)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
