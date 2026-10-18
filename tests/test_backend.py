"""
Backend API and Engine Unit/Integration Tests.
Tests all endpoints:
- Health check
- Available wells listing & filtering
- Single well retrieval
- Well historical events retrieval
- Explainable KNN similarity search
- Historical drilling experience retrieval
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import init_db
from backend.similarity import similarity_engine

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Ensure database and similarity model are initialized before tests run."""
    init_db(force_reload=False)
    similarity_engine.fit()

@pytest.fixture
def client():
    """Provide a TestClient instance."""
    with TestClient(app) as test_client:
        yield test_client

# 1. Health endpoint test
def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["wells_count"] > 0
    assert data["events_count"] > 0
    assert data["is_synthetic"] is True
    assert "Synthetic dataset" in data["data_notice"]

# 2. Wells listing test
def test_list_wells(client):
    response = client.get("/api/wells")
    assert response.status_code == 200
    wells = response.json()
    assert isinstance(wells, list)
    assert len(wells) >= 20
    # Check well fields
    first_well = wells[0]
    assert "well_id" in first_well
    assert "field" in first_well
    assert "formation" in first_well
    assert "total_depth" in first_well
    assert "mud_weight" in first_well

def test_list_wells_with_filter(client):
    response = client.get("/api/wells?field=Mumbai%20Offshore")
    assert response.status_code == 200
    wells = response.json()
    assert len(wells) > 0
    for w in wells:
        assert w["field"] == "Mumbai Offshore"

# 3. Single well retrieval test
def test_get_well_by_id_success(client):
    response = client.get("/api/wells/MO-B-101")
    assert response.status_code == 200
    well = response.json()
    assert well["well_id"] == "MO-B-101"
    assert well["field"] == "Mumbai Offshore"
    assert well["formation"] == "Bassein Limestone"
    assert well["total_depth"] == 3450.0

def test_get_well_by_id_not_found(client):
    response = client.get("/api/wells/NON-EXISTENT-999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

# 4. Well events retrieval test
def test_get_well_events(client):
    response = client.get("/api/wells/MO-B-101/events")
    assert response.status_code == 200
    events = response.json()
    assert isinstance(events, list)
    assert len(events) >= 1
    first_event = events[0]
    assert first_event["well_id"] == "MO-B-101"
    assert "depth" in first_event
    assert "event_type" in first_event
    assert "description" in first_event
    assert "action_taken" in first_event
    assert "result" in first_event

# 5. Similar wells search test
def test_similar_wells_search(client):
    # Query parameters resembling Bassein Limestone drilling profile
    payload = {
        "total_depth": 3460.0,
        "mud_weight": 11.3,
        "pressure": 4270.0,
        "rop": 12.0,
        "wob": 16.5,
        "torque": 13.8,
        "inclination": 15.0,
        "azimuth": 212.0,
        "top_k": 3
    }
    response = client.post("/api/similar-wells", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert "similar_wells" in result
    similar_wells = result["similar_wells"]
    assert len(similar_wells) == 3

    # Check top match
    top_match = similar_wells[0]
    assert "well_id" in top_match
    assert "similarity" in top_match
    # Similarity should be high for parameters closely matching MO-B-101
    assert top_match["similarity"] > 80.0
    assert "distance" in top_match
    assert "parameter_breakdown" in top_match
    assert "key_matching_factors" in top_match

    # Ensure parameter breakdown includes all 8 features
    breakdown = top_match["parameter_breakdown"]
    for feat in ["total_depth", "mud_weight", "pressure", "rop", "wob", "torque", "inclination", "azimuth"]:
        assert feat in breakdown
        assert "input_value" in breakdown[feat]
        assert "matched_value" in breakdown[feat]
        assert "difference" in breakdown[feat]

# 6. Experience search test
def test_experience_search(client):
    # Overpressured gas sand scenario resembling Tapti Daman sand
    payload = {
        "total_depth": 3000.0,
        "mud_weight": 12.9,
        "pressure": 5500.0,
        "rop": 21.5,
        "wob": 21.8,
        "torque": 15.7,
        "inclination": 36.0,
        "azimuth": 142.0,
        "top_k": 3,
        "current_depth": 2750.0
    }
    response = client.post("/api/experience-search", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "similar_wells" in data
    assert "historical_experiences" in data
    assert "evidence_summary" in data

    # Verify similar wells returned
    assert len(data["similar_wells"]) >= 1

    # Verify historical experiences returned
    experiences = data["historical_experiences"]
    assert len(experiences) >= 1

    # Check that events contain all required narrative columns
    for exp in experiences:
        assert exp["well_id"] is not None
        assert exp["depth"] > 0
        assert exp["event_type"] is not None
        assert len(exp["description"]) > 10
        assert len(exp["action_taken"]) > 10
        assert len(exp["result"]) > 5
        assert exp["well_similarity"] > 0

    # For an overpressured Tapti profile, historical gas kick events should be retrieved
    event_types = [e["event_type"] for e in experiences]
    assert any("Gas Kick" in et or "Wellbore Influx" in et for et in event_types)
