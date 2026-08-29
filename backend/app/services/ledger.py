"""
Voxy - Scam Pattern Ledger

A simple tamper-evident hash chain using:
- SQLite
- SHA-256

This is NOT a real blockchain.

Only scam-related metadata is stored.
Raw audio and transcript are NOT stored.
"""

import sqlite3
import hashlib
import json
import os
from datetime import datetime, timezone


# ============================================================
# PATH CONFIGURATION
# ============================================================

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

# ledger.py is inside:
# backend/app/services/
#
# Going up 3 levels reaches project root.

PROJECT_ROOT = os.path.abspath(
    os.path.join(THIS_DIR, "..", "..", "..")
)

DATA_DIR = os.path.join(PROJECT_ROOT, "data")

DB_PATH = os.path.join(
    DATA_DIR,
    "scam_ledger.db"
)

TABLE_NAME = "scam_ledger"

GENESIS_HASH = "0" * 64


# ============================================================
# DATABASE HELPERS
# ============================================================

def ensure_data_directory():
    """Create the data directory if it does not exist."""

    os.makedirs(DATA_DIR, exist_ok=True)


def get_connection():
    """Create a SQLite connection."""

    ensure_data_directory()

    return sqlite3.connect(DB_PATH)


def initialize_database():
    """Create the ledger table if it does not already exist."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            timestamp TEXT NOT NULL,

            risk_score INTEGER NOT NULL,

            risk_level TEXT NOT NULL,

            threats TEXT NOT NULL,

            previous_hash TEXT NOT NULL,

            current_hash TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()


# ============================================================
# HASH FUNCTIONS
# ============================================================

def calculate_hash(
    timestamp,
    risk_score,
    risk_level,
    threats_json,
    previous_hash
):
    """
    Generate a SHA-256 hash.

    The same data and same order must always be used.
    """

    raw_data = (
        f"{timestamp}|"
        f"{risk_score}|"
        f"{risk_level}|"
        f"{threats_json}|"
        f"{previous_hash}"
    )

    return hashlib.sha256(
        raw_data.encode("utf-8")
    ).hexdigest()


def get_last_record(cursor):
    """Get the newest record in the ledger."""

    cursor.execute(
        f"""
        SELECT
            id,
            timestamp,
            risk_score,
            risk_level,
            threats,
            previous_hash,
            current_hash

        FROM {TABLE_NAME}

        ORDER BY id DESC

        LIMIT 1
        """
    )

    return cursor.fetchone()


# ============================================================
# MAIN FUNCTION: RECORD SCAM PATTERN
# ============================================================

def record_scam_pattern(result):
    """
    Store a suspicious/high-risk scam pattern.

    Expected input:

    {
        "overall_risk": 82,
        "risk_level": "CRITICAL",
        "threats": [
            "Urgency",
            "Money Request"
        ]
    }

    Raw audio is NOT stored.
    Transcript is NOT stored.

    Returns:

    {
        "ledger_status": "Recorded",
        "record_hash": "...",
        "previous_hash": "..."
    }
    """

    initialize_database()

    risk_score = int(
        result.get("overall_risk", 0)
    )

    risk_level = result.get(
        "risk_level",
        "UNKNOWN"
    )

    threats = result.get(
        "threats",
        []
    )

    # Keep JSON deterministic.
    threats_json = json.dumps(
        threats,
        sort_keys=True
    )

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    connection = get_connection()
    cursor = connection.cursor()

    try:

        last_record = get_last_record(cursor)

        if last_record:
            previous_hash = last_record[6]
        else:
            previous_hash = GENESIS_HASH

        current_hash = calculate_hash(
            timestamp,
            risk_score,
            risk_level,
            threats_json,
            previous_hash
        )

        cursor.execute(
            f"""
            INSERT INTO {TABLE_NAME}
            (
                timestamp,
                risk_score,
                risk_level,
                threats,
                previous_hash,
                current_hash
            )

            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                timestamp,
                risk_score,
                risk_level,
                threats_json,
                previous_hash,
                current_hash
            )
        )

        connection.commit()

        return {
            "ledger_status": "Recorded",
            "record_hash": current_hash,
            "previous_hash": previous_hash
        }

    finally:

        connection.close()


# ============================================================
# VERIFY LEDGER
# ============================================================

def verify_ledger():
    """
    Verify the entire hash chain.

    Returns:

    {"valid": True}

    if everything is correct.

    Returns:

    {"valid": False}

    if tampering is detected.
    """

    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        f"""
        SELECT
            id,
            timestamp,
            risk_score,
            risk_level,
            threats,
            previous_hash,
            current_hash

        FROM {TABLE_NAME}

        ORDER BY id ASC
        """
    )

    records = cursor.fetchall()

    connection.close()

    expected_previous_hash = GENESIS_HASH

    for record in records:

        (
            record_id,
            timestamp,
            risk_score,
            risk_level,
            threats_json,
            previous_hash,
            current_hash
        ) = record

        # Check chain connection.
        if previous_hash != expected_previous_hash:

            return {
                "valid": False
            }

        # Recalculate hash.
        recalculated_hash = calculate_hash(
            timestamp,
            risk_score,
            risk_level,
            threats_json,
            previous_hash
        )

        # Check hash integrity.
        if recalculated_hash != current_hash:

            return {
                "valid": False
            }

        expected_previous_hash = current_hash

    return {
        "valid": True
    }