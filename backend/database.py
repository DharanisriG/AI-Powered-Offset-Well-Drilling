"""
Database access and initialization module for AI-Powered Offset Well Platform.
Uses SQLite for local, zero-config persistence of synthetic well and event data.
"""

import os
import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional

# Project path resolution
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
DB_PATH = os.path.join(BACKEND_DIR, "drilling_knowledge.db")
DEFAULT_WELLS_CSV = os.path.join(PROJECT_ROOT, "dataset", "wells.csv")
DEFAULT_EVENTS_CSV = os.path.join(PROJECT_ROOT, "dataset", "drilling_events.csv")

IS_SYNTHETIC_DATA = True

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Create and return a SQLite database connection with row factory enabled."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # Enable foreign key support in SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(
    db_path: str = DB_PATH,
    wells_csv: str = DEFAULT_WELLS_CSV,
    events_csv: str = DEFAULT_EVENTS_CSV,
    force_reload: bool = False
) -> None:
    """
    Initialize SQLite database schema and seed with synthetic dataset if empty or forced.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wells (
            well_id TEXT PRIMARY KEY,
            field TEXT NOT NULL,
            formation TEXT NOT NULL,
            total_depth REAL NOT NULL,
            mud_weight REAL NOT NULL,
            pressure REAL NOT NULL,
            rop REAL NOT NULL,
            wob REAL NOT NULL,
            torque REAL NOT NULL,
            inclination REAL NOT NULL,
            azimuth REAL NOT NULL,
            is_synthetic INTEGER DEFAULT 1
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS drilling_events (
            event_id TEXT PRIMARY KEY,
            well_id TEXT NOT NULL,
            depth REAL NOT NULL,
            event_type TEXT NOT NULL,
            description TEXT NOT NULL,
            action_taken TEXT NOT NULL,
            result TEXT NOT NULL,
            is_synthetic INTEGER DEFAULT 1,
            FOREIGN KEY (well_id) REFERENCES wells (well_id) ON DELETE CASCADE
        );
    """)

    conn.commit()

    # Check if seeding is required
    cursor.execute("SELECT COUNT(*) as count FROM wells;")
    well_count = cursor.fetchone()["count"]

    if well_count == 0 or force_reload:
        print("[Database] Seeding SQLite database from synthetic CSV datasets...")
        if force_reload:
            cursor.execute("DELETE FROM drilling_events;")
            cursor.execute("DELETE FROM wells;")
            conn.commit()

        if not os.path.exists(wells_csv) or not os.path.exists(events_csv):
            # Run generator if CSVs not found
            from scripts.generate_synthetic_data import generate_csv_files
            generate_csv_files()

        wells_df = pd.read_csv(wells_csv)
        events_df = pd.read_csv(events_csv)

        # Insert wells
        for _, row in wells_df.iterrows():
            cursor.execute("""
                INSERT OR REPLACE INTO wells 
                (well_id, field, formation, total_depth, mud_weight, pressure, rop, wob, torque, inclination, azimuth, is_synthetic)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                str(row["well_id"]),
                str(row["field"]),
                str(row["formation"]),
                float(row["total_depth"]),
                float(row["mud_weight"]),
                float(row["pressure"]),
                float(row["rop"]),
                float(row["wob"]),
                float(row["torque"]),
                float(row["inclination"]),
                float(row["azimuth"]),
            ))

        # Insert drilling events
        for _, row in events_df.iterrows():
            cursor.execute("""
                INSERT OR REPLACE INTO drilling_events 
                (event_id, well_id, depth, event_type, description, action_taken, result, is_synthetic)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                str(row["event_id"]),
                str(row["well_id"]),
                float(row["depth"]),
                str(row["event_type"]),
                str(row["description"]),
                str(row["action_taken"]),
                str(row["result"]),
            ))

        cursor.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES ('data_source', 'SYNTHETIC_DEMO_DATASET');")
        cursor.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES ('disclaimer', 'Indian Offshore synthetic scenarios for hackathon demo');")
        conn.commit()
        print(f"[Database] Successfully seeded {len(wells_df)} wells and {len(events_df)} historical drilling events.")

    conn.close()

def get_all_wells(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Retrieve all wells from the database."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM wells ORDER BY well_id ASC;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_well_by_id(well_id: str, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    """Retrieve a specific well by its ID."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM wells WHERE well_id = ?;", (well_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_events_by_well_id(well_id: str, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Retrieve all historical drilling events for a specific well."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM drilling_events WHERE well_id = ? ORDER BY depth ASC;", (well_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_events_for_wells(well_ids: List[str], db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Retrieve historical drilling events for a list of well IDs."""
    if not well_ids:
        return []
    conn = get_connection(db_path)
    cursor = conn.cursor()
    placeholders = ",".join(["?"] * len(well_ids))
    cursor.execute(
        f"SELECT * FROM drilling_events WHERE well_id IN ({placeholders}) ORDER BY depth ASC;",
        well_ids
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_all_events(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Retrieve all historical drilling events in the database."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM drilling_events ORDER BY depth ASC;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_wells_dataframe(db_path: str = DB_PATH) -> pd.DataFrame:
    """Fetch all wells directly into a pandas DataFrame."""
    conn = get_connection(db_path)
    df = pd.read_sql_query("SELECT * FROM wells;", conn)
    conn.close()
    return df

def get_db_stats(db_path: str = DB_PATH) -> Dict[str, Any]:
    """Return database health statistics and synthetic status."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM wells;")
    well_count = cursor.fetchone()["count"]
    cursor.execute("SELECT COUNT(*) as count FROM drilling_events;")
    event_count = cursor.fetchone()["count"]
    conn.close()
    return {
        "status": "healthy",
        "wells_count": well_count,
        "events_count": event_count,
        "is_synthetic": IS_SYNTHETIC_DATA,
        "data_notice": "Synthetic dataset simulating Indian offshore drilling operations (Mumbai Offshore, Bassein, Tapti, Ratna, Heera, Daman, Mukta)."
    }
