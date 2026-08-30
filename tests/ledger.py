"""
ledger.py
---------
Owner: Member 6 (Scam Pattern Ledger + Testing)

Purpose:
Store the FINAL analysis result (from the Risk Engine) into a simple
tamper-evident hash chain built on top of SQLite + SHA-256.

This is NOT a real blockchain. It is a simple "hash chain":
each new record stores the hash of the previous record, so if anyone
edits an old record later, the chain breaks and verify_ledger() will
detect it.

Rules followed:
- No raw audio is ever stored.
- No unnecessary external packages (only sqlite3, hashlib, json,
  datetime, os -> all from the Python standard library).
- Function names / return formats are exactly as specified by the
  team contract. Do not rename or change them.
"""

import sqlite3
import hashlib
import json
import os
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# Make the path robust so this works no matter where the script is run from
# (project root, backend folder, tests folder, etc.).
# This file lives at: backend/app/services/ledger.py
# We walk up 3 levels to reach the project root, then into data/.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", "..", ".."))
_DATA_DIR = os.path.join(_PROJECT_ROOT, "data")
DB_PATH = os.path.join(_DATA_DIR, "scam_ledger.db")

TABLE_NAME = "scam_ledger"

# The "previous_hash" used for the very first record in the chain.
GENESIS_HASH = "0" * 64


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _ensure_data_dir():
    """Make sure the data/ folder exists before we try to create the DB."""
    os.makedirs(_DATA_DIR, exist_ok=True)


def _get_connection():
    """Open a connection to the ledger database, creating folders as needed."""
    _ensure_data_dir()
    return sqlite3.connect(DB_PATH)


def _init_db():
    """Create the scam_ledger table if it doesn't already exist."""
    conn = _get_connection()
    cursor = conn.cursor()
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
    conn.commit()
    conn.close()


def _calculate_hash(timestamp, risk_score, risk_level, threats_json, previous_hash):
    """
    Deterministically calculate a SHA-256 hash for a record.

    IMPORTANT: The exact same fields, in the exact same order/format,
    must be used both when creating a record AND when verifying it.
    """
    raw_string = f"{timestamp}|{risk_score}|{risk_level}|{threats_json}|{previous_hash}"
    return hashlib.sha256(raw_string.encode("utf-8")).hexdigest()


def _get_last_record(cursor):
    """Return the most recently inserted record (by id), or None if empty."""
    cursor.execute(
        f"SELECT id, timestamp, risk_score, risk_level, threats, previous_hash, current_hash "
        f"FROM {TABLE_NAME} ORDER BY id DESC LIMIT 1"
    )
    return cursor.fetchone()


# ---------------------------------------------------------------------------
# REQUIRED FUNCTION #1
# ---------------------------------------------------------------------------
def record_scam_pattern(result):
    """
    Store the final analysis result into the tamper-evident ledger.

    Input (result) example:
    {
        "transcript": "Hello, your bank account will be blocked.",
        "voice_risk": 72,
        "scam_risk": 90,
        "overall_risk": 82,
        "risk_level": "CRITICAL",
        "threats": ["Bank Impersonation", "OTP Request", "Urgency"],
        "recommended_action": "End the call immediately."
    }

    Only the risk score, risk level, and threats are stored.
    Raw audio and transcript are NOT stored in the ledger.

    Returns:
        {"ledger_status": "Recorded"}
    """
    _init_db()

    # Pull only the fields the ledger is allowed to store.
    risk_score = result.get("overall_risk", 0)
    risk_level = result.get("risk_level", "UNKNOWN")
    threats = result.get("threats", [])

    # json.dumps with sort_keys keeps this deterministic every time.
    threats_json = json.dumps(threats, sort_keys=True)

    timestamp = datetime.now(timezone.utc).isoformat()

    conn = _get_connection()
    cursor = conn.cursor()

    last_record = _get_last_record(cursor)
    previous_hash = last_record[6] if last_record else GENESIS_HASH

    current_hash = _calculate_hash(
        timestamp, risk_score, risk_level, threats_json, previous_hash
    )

    cursor.execute(
        f"""
        INSERT INTO {TABLE_NAME}
            (timestamp, risk_score, risk_level, threats, previous_hash, current_hash)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (timestamp, risk_score, risk_level, threats_json, previous_hash, current_hash),
    )
    conn.commit()
    conn.close()

    return {"ledger_status": "Recorded"}


# ---------------------------------------------------------------------------
# REQUIRED FUNCTION #2
# ---------------------------------------------------------------------------
def verify_ledger():
    """
    Verify the integrity of the entire ledger chain.

    For every record, in order:
      1. previous_hash must match the previous record's current_hash
         (or GENESIS_HASH for the first record).
      2. Recalculate current_hash from the stored record data.
      3. The recalculated hash must match the stored current_hash.

    Returns:
        {"valid": True}  -> ledger is untampered
        {"valid": False} -> ledger has been tampered with
    """
    _init_db()

    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT id, timestamp, risk_score, risk_level, threats, previous_hash, current_hash "
        f"FROM {TABLE_NAME} ORDER BY id ASC"
    )
    records = cursor.fetchall()
    conn.close()

    expected_previous_hash = GENESIS_HASH

    for record in records:
        (_id, timestamp, risk_score, risk_level, threats_json,
         previous_hash, current_hash) = record

        # 1. Check the chain link to the previous record.
        if previous_hash != expected_previous_hash:
            return {"valid": False}

        # 2. Recalculate the hash from the stored data.
        recalculated_hash = _calculate_hash(
            timestamp, risk_score, risk_level, threats_json, previous_hash
        )

        # 3. Compare recalculated hash with the stored hash.
        if recalculated_hash != current_hash:
            return {"valid": False}

        # This record's current_hash becomes the expected previous_hash
        # for the next record in the chain.
        expected_previous_hash = current_hash

    return {"valid": True}