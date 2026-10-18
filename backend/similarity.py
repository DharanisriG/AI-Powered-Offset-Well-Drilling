"""
AI Similarity and Historical Experience Retrieval Engine.
Uses Scikit-Learn StandardScaler and NearestNeighbors (KNN) to perform
explainable, metric-driven offset well similarity search and event retrieval.
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

from backend.database import get_wells_dataframe, get_events_for_wells, DB_PATH
from backend.models import (
    WellQuery,
    SimilarWellMatch,
    ParameterComparison,
    HistoricalExperienceItem,
    SimilarWellsResponse,
    ExperienceSearchResponse
)

FEATURE_COLUMNS = [
    "total_depth",
    "mud_weight",
    "pressure",
    "rop",
    "wob",
    "torque",
    "inclination",
    "azimuth",
]

FEATURE_UNITS = {
    "total_depth": "m",
    "mud_weight": "ppg",
    "pressure": "psi",
    "rop": "m/hr",
    "wob": "klbs",
    "torque": "kft-lb",
    "inclination": "deg",
    "azimuth": "deg",
}

FEATURE_LABELS = {
    "total_depth": "Total Depth",
    "mud_weight": "Mud Weight",
    "pressure": "Formation Pressure",
    "rop": "Rate of Penetration (ROP)",
    "wob": "Weight on Bit (WOB)",
    "torque": "Drilling Torque",
    "inclination": "Hole Inclination",
    "azimuth": "Hole Azimuth",
}

# Calibration constant for converting standardized Euclidean distance into similarity percentage
# Score = 100 / (1 + DISTANCE_GAMMA * distance)
DISTANCE_GAMMA = 0.35

class OffsetWellSimilarityEngine:
    """
    Explainable AI engine for finding similar offset wells and retrieving
    relevant historical drilling experiences/events.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.scaler: Optional[StandardScaler] = None
        self.knn: Optional[NearestNeighbors] = None
        self.wells_df: Optional[pd.DataFrame] = None
        self.is_fitted: bool = False
        self.model_cache_path = os.path.join(os.path.dirname(__file__), "similarity_model.joblib")

    def fit(self, force_refit: bool = False) -> None:
        """
        Fit the StandardScaler and NearestNeighbors model on historical wells.
        Loads from database and caches to joblib.
        """
        self.wells_df = get_wells_dataframe(self.db_path)
        if self.wells_df.empty:
            raise ValueError("No historical wells found in database to fit similarity model.")

        # Ensure all feature columns exist and are numeric
        X = self.wells_df[FEATURE_COLUMNS].astype(float).values

        # Standardize features (mean=0, variance=1)
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        # NearestNeighbors using Euclidean metric
        n_neighbors = min(len(self.wells_df), 10)
        self.knn = NearestNeighbors(n_neighbors=n_neighbors, metric="euclidean", algorithm="auto")
        self.knn.fit(X_scaled)

        self.is_fitted = True

        # Cache artifacts with joblib
        try:
            joblib.dump({
                "scaler": self.scaler,
                "knn": self.knn,
                "feature_columns": FEATURE_COLUMNS
            }, self.model_cache_path)
        except Exception as e:
            print(f"[Similarity] Notice: model caching skipped ({e})")

        print(f"[Similarity Engine] Fitted KNN model on {len(self.wells_df)} offset wells with {len(FEATURE_COLUMNS)} drilling features.")

    def _ensure_fitted(self) -> None:
        if not self.is_fitted or self.scaler is None or self.knn is None or self.wells_df is None:
            self.fit()

    @staticmethod
    def distance_to_similarity(distance: float) -> float:
        """
        Mathematically derive similarity percentage from standardized Euclidean distance:
        similarity = 100 / (1 + 0.35 * distance)
        Guarantees:
        - Exact match (d=0) -> 100.0%
        - Monotonically decreases as distance increases
        - Bounded between 0% and 100%
        """
        if distance < 0:
            return 0.0
        score = 100.0 / (1.0 + DISTANCE_GAMMA * distance)
        return round(float(np.clip(score, 0.0, 100.0)), 1)

    def find_similar_wells(self, query: WellQuery) -> Tuple[List[SimilarWellMatch], Dict[str, float]]:
        """
        Find top-k similar offset wells based on drilling parameters.
        Returns explainable parameter breakdowns and similarity scores.
        """
        self._ensure_fitted()
        assert self.wells_df is not None and self.scaler is not None and self.knn is not None

        query_dict = {
            "total_depth": float(query.total_depth),
            "mud_weight": float(query.mud_weight),
            "pressure": float(query.pressure),
            "rop": float(query.rop),
            "wob": float(query.wob),
            "torque": float(query.torque),
            "inclination": float(query.inclination),
            "azimuth": float(query.azimuth),
        }

        query_vector = np.array([[query_dict[col] for col in FEATURE_COLUMNS]], dtype=float)
        query_scaled = self.scaler.transform(query_vector)

        # Handle optional field/formation filtering or global search
        candidate_df = self.wells_df.copy()
        if query.field:
            filtered = candidate_df[candidate_df["field"].str.lower() == query.field.lower()]
            if not filtered.empty:
                candidate_df = filtered
        if query.formation:
            filtered = candidate_df[candidate_df["formation"].str.lower() == query.formation.lower()]
            if not filtered.empty:
                candidate_df = filtered

        # If filtering reduced candidates, calculate distances against candidate subset
        candidate_indices = candidate_df.index.values
        candidate_features = self.wells_df.loc[candidate_indices, FEATURE_COLUMNS].values
        candidate_scaled = self.scaler.transform(candidate_features)

        # Compute Euclidean distance to all candidate wells
        diffs = candidate_scaled - query_scaled
        distances = np.linalg.norm(diffs, axis=1)

        # Sort by distance
        k = min(query.top_k or 3, len(candidate_df))
        sorted_order = np.argsort(distances)[:k]

        matched_results: List[SimilarWellMatch] = []

        # Get events count for all wells to include in well summary
        from backend.database import get_connection
        conn = get_connection(self.db_path)
        cur = conn.cursor()

        for idx in sorted_order:
            row_idx = candidate_indices[idx]
            well_row = self.wells_df.loc[row_idx]
            dist = float(distances[idx])
            similarity = self.distance_to_similarity(dist)

            # Count historical events for this well
            cur.execute("SELECT COUNT(*) as cnt FROM drilling_events WHERE well_id = ?;", (str(well_row["well_id"]),))
            event_cnt = cur.fetchone()["cnt"]

            # Compute explainability parameter breakdown
            parameter_breakdown: Dict[str, ParameterComparison] = {}
            feature_z_diffs = []

            for col_idx, col in enumerate(FEATURE_COLUMNS):
                in_val = query_dict[col]
                match_val = float(well_row[col])
                diff = round(match_val - in_val, 2)
                z_diff = abs(query_scaled[0, col_idx] - candidate_scaled[idx, col_idx])
                feature_z_diffs.append((z_diff, col, in_val, match_val, diff))

                if z_diff < 0.35:
                    match_quality = "Strong Match"
                elif z_diff < 0.85:
                    match_quality = "Close Match"
                elif z_diff < 1.50:
                    match_quality = "Moderate Difference"
                else:
                    match_quality = "Noticeable Difference"

                parameter_breakdown[col] = ParameterComparison(
                    feature=col,
                    unit=FEATURE_UNITS[col],
                    input_value=round(in_val, 2),
                    matched_value=round(match_val, 2),
                    difference=diff,
                    match_quality=match_quality
                )

            # Sort features by closest standardized match to generate explainability bullet points
            feature_z_diffs.sort(key=lambda x: x[0])
            key_factors = []
            for _, col, in_val, match_val, diff in feature_z_diffs[:3]:
                sign = "+" if diff > 0 else ""
                key_factors.append(
                    f"{FEATURE_LABELS[col]}: matched {match_val} vs current {in_val} {FEATURE_UNITS[col]} ({sign}{diff} {FEATURE_UNITS[col]})"
                )

            matched_results.append(SimilarWellMatch(
                well_id=str(well_row["well_id"]),
                field=str(well_row["field"]),
                formation=str(well_row["formation"]),
                similarity=similarity,
                distance=round(dist, 3),
                total_depth=float(well_row["total_depth"]),
                mud_weight=float(well_row["mud_weight"]),
                pressure=float(well_row["pressure"]),
                rop=float(well_row["rop"]),
                wob=float(well_row["wob"]),
                torque=float(well_row["torque"]),
                inclination=float(well_row["inclination"]),
                azimuth=float(well_row["azimuth"]),
                parameter_breakdown=parameter_breakdown,
                key_matching_factors=key_factors,
                event_count=event_cnt
            ))

        conn.close()
        return matched_results, query_dict

    def search_experiences(self, query: WellQuery) -> ExperienceSearchResponse:
        """
        Execute full knowledge retrieval:
        1. Find similar offset wells.
        2. Retrieve historical drilling events and actions taken on those wells.
        3. Formulate evidence summary for the drilling engineer.
        """
        similar_wells, query_dict = self.find_similar_wells(query)
        well_ids = [w.well_id for w in similar_wells]
        well_sim_map = {w.well_id: w for w in similar_wells}

        events_raw = get_events_for_wells(well_ids, self.db_path)

        historical_experiences: List[HistoricalExperienceItem] = []
        for evt in events_raw:
            w_info = well_sim_map.get(evt["well_id"])
            w_field = w_info.field if w_info else "Unknown"
            w_formation = w_info.formation if w_info else "Unknown"
            w_sim = w_info.similarity if w_info else 0.0

            # Proximity check relative to current depth or total depth
            proximity_desc = None
            ref_depth = query.current_depth if query.current_depth else query.total_depth
            depth_delta = abs(evt["depth"] - ref_depth)
            if depth_delta <= 150:
                proximity_desc = f"Critical Proximity (within {int(depth_delta)}m of target depth)"
            elif depth_delta <= 350:
                proximity_desc = f"Nearby Interval (within {int(depth_delta)}m)"
            else:
                proximity_desc = f"Section Depth: {int(evt['depth'])}m"

            historical_experiences.append(HistoricalExperienceItem(
                event_id=str(evt["event_id"]),
                well_id=str(evt["well_id"]),
                well_field=w_field,
                well_formation=w_formation,
                well_similarity=w_sim,
                depth=float(evt["depth"]),
                depth_proximity=proximity_desc,
                event_type=str(evt["event_type"]),
                description=str(evt["description"]),
                action_taken=str(evt["action_taken"]),
                result=str(evt["result"]),
            ))

        # Sort experiences primarily by well similarity (desc) and depth proximity
        historical_experiences.sort(key=lambda x: x.well_similarity, reverse=True)

        # Formulate engineering evidence summary
        event_types = list(set(e.event_type for e in historical_experiences))
        top_well = similar_wells[0] if similar_wells else None

        if historical_experiences:
            summary = (
                f"Identified {len(similar_wells)} top matching offset wells with up to {top_well.similarity}% similarity. "
                f"Historical records show {len(historical_experiences)} relevant drilling events in similar formations "
                f"({', '.join(event_types)}). Precedents indicate key actions taken and resolved outcomes."
            )
        else:
            summary = (
                f"Identified {len(similar_wells)} matching offset wells, but no critical drilling incidents were logged "
                f"under these exact operational envelopes, indicating historically stable operations."
            )

        # Extract distinct recommended actions
        distinct_actions = []
        for e in historical_experiences:
            action_snippet = f"[{e.event_type}] on {e.well_id} ({int(e.depth)}m): {e.action_taken} -> Result: {e.result}"
            if action_snippet not in distinct_actions:
                distinct_actions.append(action_snippet)

        return ExperienceSearchResponse(
            query_parameters=query_dict,
            similar_wells=similar_wells,
            historical_experiences=historical_experiences,
            evidence_summary=summary,
            recommended_actions_summary=distinct_actions[:5],
            is_synthetic=True
        )

# Global engine instance
similarity_engine = OffsetWellSimilarityEngine()
