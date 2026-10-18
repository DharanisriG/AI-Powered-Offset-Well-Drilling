"""
Pydantic schemas and data models for AI-Powered Offset Well Platform.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class WellBase(BaseModel):
    well_id: str = Field(..., description="Unique well identifier, e.g. MO-B-101")
    field: str = Field(..., description="Oil & gas field, e.g. Mumbai Offshore, Bassein, Tapti")
    formation: str = Field(..., description="Target geological formation, e.g. Bassein Limestone")
    total_depth: float = Field(..., description="Measured depth in meters (m)")
    mud_weight: float = Field(..., description="Drilling fluid density in pounds per gallon (ppg)")
    pressure: float = Field(..., description="Pore/formation pressure in pounds per square inch (psi)")
    rop: float = Field(..., description="Rate of penetration in meters per hour (m/hr)")
    wob: float = Field(..., description="Weight on bit in thousands of pounds (klbs)")
    torque: float = Field(..., description="Surface torque in kilo foot-pounds (kft-lb)")
    inclination: float = Field(..., description="Wellbore inclination in degrees (0 = vertical)")
    azimuth: float = Field(..., description="Wellbore azimuth angle in degrees (0-360°)")
    is_synthetic: bool = Field(True, description="Flag indicating synthetic demonstration record")

class WellResponse(WellBase):
    pass

class DrillingEventResponse(BaseModel):
    event_id: str = Field(..., description="Unique event identifier, e.g. EVT-1001")
    well_id: str = Field(..., description="Associated offset well identifier")
    depth: float = Field(..., description="Depth where event occurred in meters (m)")
    event_type: str = Field(..., description="Class of drilling event (Lost Circulation, Gas Kick, etc.)")
    description: str = Field(..., description="Factual operational narrative of what occurred")
    action_taken: str = Field(..., description="Immediate mitigation or engineering action executed")
    result: str = Field(..., description="Outcome of the action taken")
    is_synthetic: bool = Field(True, description="Flag indicating synthetic demonstration record")

class WellQuery(BaseModel):
    total_depth: float = Field(..., ge=100.0, le=10000.0, description="Total planned depth (m)", examples=[3400.0])
    mud_weight: float = Field(..., ge=7.0, le=22.0, description="Mud weight (ppg)", examples=[11.2])
    pressure: float = Field(..., ge=500.0, le=20000.0, description="Estimated pore/formation pressure (psi)", examples=[4200.0])
    rop: float = Field(..., ge=0.0, le=100.0, description="Target or current ROP (m/hr)", examples=[12.0])
    wob: float = Field(..., ge=0.0, le=100.0, description="Weight on Bit (klbs)", examples=[16.0])
    torque: float = Field(..., ge=0.0, le=60.0, description="Torque (kft-lb)", examples=[13.5])
    inclination: float = Field(..., ge=0.0, le=120.0, description="Hole inclination (degrees)", examples=[14.0])
    azimuth: float = Field(..., ge=0.0, le=360.0, description="Hole azimuth (degrees)", examples=[210.0])
    top_k: Optional[int] = Field(3, ge=1, le=10, description="Number of top similar offset wells to retrieve")
    field: Optional[str] = Field(None, description="Optional filter by field name")
    formation: Optional[str] = Field(None, description="Optional filter by formation name")
    current_depth: Optional[float] = Field(None, description="Optional current bit depth (m) for proximity ranking")

class ParameterComparison(BaseModel):
    feature: str
    unit: str
    input_value: float
    matched_value: float
    difference: float
    match_quality: str

class SimilarWellMatch(BaseModel):
    well_id: str
    field: str
    formation: str
    similarity: float = Field(..., description="Calculated similarity percentage (0-100%)")
    distance: float = Field(..., description="Model Euclidean distance in standardized feature space")
    total_depth: float
    mud_weight: float
    pressure: float
    rop: float
    wob: float
    torque: float
    inclination: float
    azimuth: float
    parameter_breakdown: Dict[str, ParameterComparison]
    key_matching_factors: List[str]
    event_count: int

class SimilarWellsResponse(BaseModel):
    query_parameters: Dict[str, float]
    total_candidates: int
    top_k: int
    similar_wells: List[SimilarWellMatch]
    explanation: str
    is_synthetic: bool = True

class HistoricalExperienceItem(BaseModel):
    event_id: str
    well_id: str
    well_field: str
    well_formation: str
    well_similarity: float
    depth: float
    depth_proximity: Optional[str] = None
    event_type: str
    description: str
    action_taken: str
    result: str

class ExperienceSearchResponse(BaseModel):
    query_parameters: Dict[str, float]
    similar_wells: List[SimilarWellMatch]
    historical_experiences: List[HistoricalExperienceItem]
    evidence_summary: str
    recommended_actions_summary: List[str]
    is_synthetic: bool = True

class HealthResponse(BaseModel):
    status: str
    wells_count: int
    events_count: int
    is_synthetic: bool
    data_notice: str
