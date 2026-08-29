"""
tests/demo_scenarios.py
------------------------
Owner: Member 6 (Scam Pattern Ledger + Testing)

A simple, readable script (not pytest) that demonstrates the ledger
working end-to-end, using the REAL database at data/scam_ledger.db.

Run with:
    python tests/demo_scenarios.py

What it does:
    1. Starts with a clean ledger (deletes any old demo DB file).
    2. Records 3 demo scenarios (normal call, human scam call,
       possible AI voice scam).
    3. Verifies the ledger is valid and prints the hash chain.
    4. Tampers with an old record on purpose.
    5. Verifies again to prove tampering is detected.
"""

import os
import sys
import sqlite3

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "app", "services")),
)

import ledger  # noqa: E402


# ---------------------------------------------------------------------------
# Demo scenario inputs (these represent the "Final Analysis Result" that
# would normally come from the Risk Engine)
# ---------------------------------------------------------------------------
SCENARIO_1_NORMAL_CALL = {
    "transcript": "Hey, are we still on for lunch tomorrow?",
    "voice_risk": 4,
    "scam_risk": 6,
    "overall_risk": 10,
    "risk_level": "LOW",
    "threats": [],
    "recommended_action": "No action needed.",
}

SCENARIO_2_HUMAN_SCAM_CALL = {
    "transcript": "Hello, your bank account will be blocked. Please share the OTP now.",
    "voice_risk": 72,
    "scam_risk": 90,
    "overall_risk": 82,
    "risk_level": "CRITICAL",
    "threats": ["Bank Impersonation", "OTP Request", "Urgency"],
    "recommended_action": "End the call immediately.",
}

SCENARIO_3_AI_VOICE_SCAM = {
    "transcript": "This is your bank's automated line. Please confirm your account number.",
    "voice_risk": 88,
    "scam_risk": 75,
    "overall_risk": 84,
    "risk_level": "CRITICAL",
    "threats": ["Synthetic Voice Detected", "Bank Impersonation", "Account Number Request"],
    "recommended_action": "End the call immediately.",
}


def _print_header(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def _print_ledger_table():
    conn = sqlite3.connect(ledger.DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, risk_score, risk_level, threats, previous_hash, current_hash "
        "FROM scam_ledger ORDER BY id ASC"
    )
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        record_id, risk_score, risk_level, threats, previous_hash, current_hash = row
        print(f"\nRecord #{record_id}")
        print(f"  risk_score     : {risk_score}")
        print(f"  risk_level     : {risk_level}")
        print(f"  threats        : {threats}")
        print(f"  previous_hash  : {previous_hash[:16]}...")
        print(f"  current_hash   : {current_hash[:16]}...")


def run_demo():
    # Start clean so the demo output is predictable every time it's run.
    if os.path.exists(ledger.DB_PATH):
        os.remove(ledger.DB_PATH)

    _print_header("SCENARIO 1: Normal Call (expected LOW risk)")
    result_1 = ledger.record_scam_pattern(SCENARIO_1_NORMAL_CALL)
    print("record_scam_pattern() returned:", result_1)

    _print_header("SCENARIO 2: Human Scam Call - Bank/OTP (expected HIGH/CRITICAL risk)")
    result_2 = ledger.record_scam_pattern(SCENARIO_2_HUMAN_SCAM_CALL)
    print("record_scam_pattern() returned:", result_2)

    _print_header("SCENARIO 3: Possible AI Voice Scam (expected HIGH/CRITICAL risk)")
    result_3 = ledger.record_scam_pattern(SCENARIO_3_AI_VOICE_SCAM)
    print("record_scam_pattern() returned:", result_3)

    _print_header("LEDGER CONTENTS (hash chain)")
    _print_ledger_table()

    _print_header("VERIFYING LEDGER (should be valid, untouched chain)")
    verification = ledger.verify_ledger()
    print("verify_ledger() returned:", verification)

    _print_header("TAMPERING TEST: modifying Record #1's risk_score directly in SQLite")
    conn = sqlite3.connect(ledger.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE scam_ledger SET risk_score = 999 WHERE id = 1")
    conn.commit()
    conn.close()
    print("Record #1 risk_score has been changed to 999 without updating its hash.")

    _print_header("VERIFYING LEDGER AGAIN (should now be INVALID)")
    verification_after_tampering = ledger.verify_ledger()
    print("verify_ledger() returned:", verification_after_tampering)

    _print_header("DEMO COMPLETE")
    print(f"Database file: {ledger.DB_PATH}")


if __name__ == "__main__":
    run_demo()