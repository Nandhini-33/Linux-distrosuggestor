"""
SQLite database management for Linux Distribution Advisor.
Stores recommendation sessions, community recommendation statistics, and catalog data.
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

DB_PATH = "distro_advisor.db"

def get_connection():
    """Create and return a database connection with dict-like row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize SQLite tables."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        ram TEXT NOT NULL,
        experience TEXT NOT NULL,
        purpose TEXT NOT NULL,
        cpu TEXT NOT NULL,
        storage TEXT NOT NULL,
        preference TEXT NOT NULL,
        prev_experience TEXT NOT NULL,
        recommended_distro TEXT NOT NULL,
        match_percentage INTEGER NOT NULL,
        alternatives_json TEXT NOT NULL,
        reasons_json TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recommendation_id INTEGER,
        rating INTEGER,
        comment TEXT,
        created_at TEXT,
        FOREIGN KEY (recommendation_id) REFERENCES recommendations(id)
    )
    """)

    conn.commit()
    conn.close()

def save_recommendation(user_input: Dict[str, Any], result: Dict[str, Any]) -> int:
    """Store recommendation query and returned result into SQLite."""
    conn = get_connection()
    cursor = conn.cursor()

    best = result.get("best_match", {})
    alternatives = result.get("alternatives", [])
    alt_summary = [{"name": a.get("name"), "match": a.get("match_percentage")} for a in alternatives]

    cursor.execute("""
    INSERT INTO recommendations (
        timestamp, ram, experience, purpose, cpu, storage, preference,
        prev_experience, recommended_distro, match_percentage,
        alternatives_json, reasons_json
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        user_input.get("ram", "N/A"),
        user_input.get("experience", "N/A"),
        user_input.get("purpose", "N/A"),
        user_input.get("cpu", "N/A"),
        user_input.get("storage", "N/A"),
        user_input.get("preference", "N/A"),
        user_input.get("prev_experience", "N/A"),
        best.get("name", "Unknown"),
        best.get("match_percentage", 0),
        json.dumps(alt_summary),
        json.dumps(best.get("reasons", []))
    ))

    rec_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rec_id

def get_recent_recommendations(limit: int = 6) -> List[Dict[str, Any]]:
    """Retrieve recent recommendation records for the trends feed."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, timestamp, ram, experience, purpose, cpu, recommended_distro, match_percentage
        FROM recommendations
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_distro_popularity() -> List[Dict[str, Any]]:
    """Aggregate top recommended distros across all queries."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT recommended_distro, COUNT(*) as count, AVG(match_percentage) as avg_match
        FROM recommendations
        GROUP BY recommended_distro
        ORDER BY count DESC
        LIMIT 5
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_latest_recommendation() -> Optional[Dict[str, Any]]:
    """Retrieve the most recent recommendation query and result."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM recommendations
        ORDER BY id DESC
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    r = dict(row)
    try:
        reasons = json.loads(r.get("reasons_json", "[]"))
    except Exception:
        reasons = []
    try:
        alts = json.loads(r.get("alternatives_json", "[]"))
    except Exception:
        alts = []

    return {
        "id": r.get("id"),
        "best_match": {
            "name": r.get("recommended_distro"),
            "match_percentage": r.get("match_percentage"),
            "reasons": reasons
        },
        "user_input": {
            "ram": r.get("ram"),
            "cpu": r.get("cpu"),
            "storage": r.get("storage"),
            "experience": r.get("experience"),
            "purpose": r.get("purpose"),
            "preference": r.get("preference"),
            "prev_experience": r.get("prev_experience")
        },
        "alternatives": alts
    }

