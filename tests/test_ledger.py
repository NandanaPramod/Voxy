"""
tests/test_ledger.py
---------------------
Owner: Member 6 (Scam Pattern Ledger + Testing)

Run with:
    pytest tests/test_ledger.py -v

These tests use a FRESH, isolated ledger database for every single test
(a temp file), so tests never interfere with each other or with the
real data/scam_ledger.db used by the rest of the app.
"""

import os
import sys
import json
import sqlite3
import hashlib

import pytest

# Make sure Python can find backend/app/services/ledger.py no matter
# where pytest is invoked from.
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "app", "services")),
)

import ledger  # noqa: E402


# ---------------------------------------------------------------------------
# Fixture: give every test a brand-new, empty ledger database file
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def isolated_ledger_db(tmp_path, monkeypatch):
    """
    Point ledger.DB_PATH at a temporary file for the duration of each test,
    so tests don't pollute (or get confused by) the real ledger database.
    """
    temp_db = tmp_path / "test_scam_ledger.db"
    monkeypatch.setattr(ledger, "DB_PATH", str(temp_db))
    monkeypatch.setattr(ledger, "_DATA_DIR", str(tmp_path))
    yield temp_db


# ---------------------------------------------------------------------------
# Sample inputs
# ---------------------------------------------------------------------------
NORMAL_CALL_RESULT = {
    "transcript": "Hi Mom, just checking in, call you later tonight.",
    "voice_risk": 5,
    "scam_risk": 8,
    "overall_risk": 10,
    "risk_level": "LOW",
    "threats": [],
    "recommended_action": "No action needed.",
}

HUMAN_SCAM_CALL_RESULT = {
    "transcript": "Hello, your bank account will be blocked. Please share the OTP now.",
    "voice_risk": 72,
    "scam_risk": 90,
    "overall_risk": 82,
    "risk_level": "CRITICAL",
    "threats": ["Bank Impersonation", "OTP Request", "Urgency"],
    "recommended_action": "End the call immediately.",
}

AI_VOICE_SCAM_RESULT = {
    "transcript": "This is your bank's automated security line. Confirm your account number.",
    "voice_risk": 88,
    "scam_risk": 75,
    "overall_risk": 84,
    "risk_level": "CRITICAL",
    "threats": ["Synthetic Voice Detected", "Bank Impersonation", "Account Number Request"],
    "recommended_action": "End the call immediately.",
}


# ---------------------------------------------------------------------------
# 1. Normal transcript / call -> LOW risk recorded correctly
# ---------------------------------------------------------------------------
def test_normal_call_is_recorded():
    response = ledger.record_scam_pattern(NORMAL_CALL_RESULT)
    assert response == {"ledger_status": "Recorded"}

    conn = sqlite3.connect(ledger.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT risk_score, risk_level, threats FROM scam_ledger")
    row = cursor.fetchone()
    conn.close()

    assert row[0] == 10
    assert row[1] == "LOW"
    assert json.loads(row[2]) == []


# ---------------------------------------------------------------------------
# 2. Obvious human scam transcript -> HIGH/CRITICAL risk recorded correctly
# ---------------------------------------------------------------------------
def test_human_scam_call_is_recorded():
    response = ledger.record_scam_pattern(HUMAN_SCAM_CALL_RESULT)
    assert response == {"ledger_status": "Recorded"}

    conn = sqlite3.connect(ledger.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT risk_score, risk_level, threats FROM scam_ledger")
    row = cursor.fetchone()
    conn.close()

    assert row[0] == 82
    assert row[1] == "CRITICAL"
    threats = json.loads(row[2])
    assert "Bank Impersonation" in threats
    assert "OTP Request" in threats
    assert "Urgency" in threats


# ---------------------------------------------------------------------------
# 3. Possible AI voice scam -> HIGH/CRITICAL risk recorded correctly
# ---------------------------------------------------------------------------
def test_ai_voice_scam_call_is_recorded():
    response = ledger.record_scam_pattern(AI_VOICE_SCAM_RESULT)
    assert response == {"ledger_status": "Recorded"}

    conn = sqlite3.connect(ledger.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT risk_level FROM scam_ledger")
    row = cursor.fetchone()
    conn.close()

    assert row[0] in ("HIGH", "CRITICAL")


# ---------------------------------------------------------------------------
# 4. Missing audio / missing fields handling
#    The ledger never touches audio directly, but it must not crash if
#    optional fields (like transcript) are missing from the result dict.
# ---------------------------------------------------------------------------
def test_missing_optional_fields_does_not_crash():
    minimal_result = {
        "overall_risk": 50,
        "risk_level": "MEDIUM",
        "threats": ["Unknown Caller"],
        # no "transcript" key at all, simulating missing/failed audio pipeline
    }
    response = ledger.record_scam_pattern(minimal_result)
    assert response == {"ledger_status": "Recorded"}


# ---------------------------------------------------------------------------
# 5. Ledger record creation -> row actually exists with correct structure
# ---------------------------------------------------------------------------
def test_ledger_record_has_expected_columns():
    ledger.record_scam_pattern(HUMAN_SCAM_CALL_RESULT)

    conn = sqlite3.connect(ledger.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(scam_ledger)")
    columns = [col[1] for col in cursor.fetchall()]
    conn.close()

    expected_columns = [
        "id", "timestamp", "risk_score", "risk_level",
        "threats", "previous_hash", "current_hash",
    ]
    assert columns == expected_columns


# ---------------------------------------------------------------------------
# 6. Multiple ledger records can be created
# ---------------------------------------------------------------------------
def test_multiple_records_are_created():
    ledger.record_scam_pattern(NORMAL_CALL_RESULT)
    ledger.record_scam_pattern(HUMAN_SCAM_CALL_RESULT)
    ledger.record_scam_pattern(AI_VOICE_SCAM_RESULT)

    conn = sqlite3.connect(ledger.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM scam_ledger")
    count = cursor.fetchone()[0]
    conn.close()

    assert count == 3


# ---------------------------------------------------------------------------
# 7. Previous hash linking: record 2's previous_hash == record 1's current_hash
# ---------------------------------------------------------------------------
def test_previous_hash_links_correctly():
    ledger.record_scam_pattern(NORMAL_CALL_RESULT)
    ledger.record_scam_pattern(HUMAN_SCAM_CALL_RESULT)
    ledger.record_scam_pattern(AI_VOICE_SCAM_RESULT)

    conn = sqlite3.connect(ledger.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, previous_hash, current_hash FROM scam_ledger ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()

    assert rows[0][1] == ledger.GENESIS_HASH
    assert rows[1][1] == rows[0][2]
    assert rows[2][1] == rows[1][2]


# ---------------------------------------------------------------------------
# 8. SHA-256 hash generation: hashes are 64-char hex strings and deterministic
# ---------------------------------------------------------------------------
def test_hash_is_valid_sha256_and_deterministic():
    ledger.record_scam_pattern(HUMAN_SCAM_CALL_RESULT)

    conn = sqlite3.connect(ledger.DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT timestamp, risk_score, risk_level, threats, previous_hash, current_hash "
        "FROM scam_ledger"
    )
    row = cursor.fetchone()
    conn.close()

    timestamp, risk_score, risk_level, threats_json, previous_hash, current_hash = row

    # 64 hex characters = SHA-256 output length
    assert len(current_hash) == 64
    int(current_hash, 16)  # will raise if not valid hex

    # Recomputing with the same inputs must give the exact same hash.
    recalculated = ledger._calculate_hash(
        timestamp, risk_score, risk_level, threats_json, previous_hash
    )
    assert recalculated == current_hash

    # Sanity check against hashlib directly.
    raw_string = f"{timestamp}|{risk_score}|{risk_level}|{threats_json}|{previous_hash}"
    assert hashlib.sha256(raw_string.encode("utf-8")).hexdigest() == current_hash


# ---------------------------------------------------------------------------
# 9. Ledger verification passes on an untouched chain
# ---------------------------------------------------------------------------
def test_verify_ledger_valid_chain():
    ledger.record_scam_pattern(NORMAL_CALL_RESULT)
    ledger.record_scam_pattern(HUMAN_SCAM_CALL_RESULT)
    ledger.record_scam_pattern(AI_VOICE_SCAM_RESULT)

    result = ledger.verify_ledger()
    assert result == {"valid": True}


# ---------------------------------------------------------------------------
# 9b. Ledger verification on an empty ledger is still valid (nothing to break)
# ---------------------------------------------------------------------------
def test_verify_ledger_empty_is_valid():
    result = ledger.verify_ledger()
    assert result == {"valid": True}


# ---------------------------------------------------------------------------
# TAMPERING TEST: modifying an old record must be detected
# ---------------------------------------------------------------------------
def test_tampering_is_detected():
    ledger.record_scam_pattern(NORMAL_CALL_RESULT)
    ledger.record_scam_pattern(HUMAN_SCAM_CALL_RESULT)
    ledger.record_scam_pattern(AI_VOICE_SCAM_RESULT)

    # Chain must be valid before tampering.
    assert ledger.verify_ledger() == {"valid": True}

    # Tamper with record 1's risk_score directly in the DB,
    # WITHOUT recalculating/updating its current_hash.
    conn = sqlite3.connect(ledger.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE scam_ledger SET risk_score = 999 WHERE id = 1")
    conn.commit()
    conn.close()

    # Chain must now be detected as broken.
    assert ledger.verify_ledger() == {"valid": False}