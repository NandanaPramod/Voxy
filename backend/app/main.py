"""
Voxy Backend - Main API
------------------------
This is the "bridge" that connects all the AI modules together.

Pipeline:
    Audio Upload
        -> Speech-to-Text        (ml/speech/transcriber.py)
        -> Voice Risk Analysis   (ml/voice/voice_detector.py)
        -> Scam Detection        (ml/scam/scam_detector.py)
        -> Risk Calculation      (ml/scam/risk_engine.py)
        -> Ledger                (backend/app/services/ledger.py)
        -> JSON Result           -> Frontend

IMPORTANT (beginner-friendly design):
This file tries to import each teammate's real function. If a teammate's
module isn't ready yet (or throws an error), we fall back to safe dummy
data instead of crashing. That way the whole system keeps running even
while pieces are still being built.
"""

import os
import shutil
import sys
import tempfile

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------------------------------------------
# Make sure Python can find the "ml" folder, which lives one level above
# backend/ at the project root:
#
#   Voxy/
#   ├── backend/app/main.py   <- we are here
#   └── ml/...
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


app = FastAPI(title="Voxy Backend")

# Allow the frontend (running on a different port, e.g. localhost:5173/3000)
# to call this backend during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# STEP 2: basic health check route
# ---------------------------------------------------------------------------
@app.get("/")
def read_root():
    return {"status": "Voxy backend is running"}


# ---------------------------------------------------------------------------
# Helpers that try to call each teammate's real function, and fall back to
# safe dummy data if the module isn't ready yet or raises an error.
# See "IF YOUR MODULE IS NOT READY" section of the team contract.
# ---------------------------------------------------------------------------

def run_transcription(audio_path: str) -> dict:
    try:
        from ml.speech.transcriber import transcribe_audio
        return transcribe_audio(audio_path)
    except Exception:
        return {"transcript": "Demo transcript unavailable."}


def run_voice_analysis(audio_path: str) -> dict:
    try:
        from ml.voice.voice_detector import analyze_voice
        return analyze_voice(audio_path)
    except Exception:
        return {"voice_risk": 50, "prediction": "UNKNOWN"}


def run_scam_analysis(transcript: str) -> dict:
    try:
        from ml.scam.scam_detector import analyze_scam
        return analyze_scam(transcript)
    except Exception:
        return {"scam_risk": 0, "threats": []}


def run_risk_engine(voice_result: dict, scam_result: dict) -> dict:
    try:
        from ml.scam.risk_engine import calculate_risk
        return calculate_risk(voice_result, scam_result)
    except Exception:
        # Simple placeholder logic so the pipeline still returns something
        # sensible if the real risk engine isn't ready yet.
        overall = round(
            (voice_result.get("voice_risk", 50) + scam_result.get("scam_risk", 0)) / 2
        )
        if overall >= 80:
            level = "CRITICAL"
        elif overall >= 60:
            level = "HIGH_RISK"
        elif overall >= 30:
            level = "SUSPICIOUS"
        else:
            level = "LOW"
        return {
            "overall_risk": overall,
            "risk_level": level,
            "recommended_action": "Exercise caution.",
        }


def run_ledger(final_result: dict) -> dict:
    try:
        from backend.app.services.ledger import record_scam_pattern
        return record_scam_pattern(final_result)
    except Exception:
        return {"ledger_status": "Not Recorded"}


# ---------------------------------------------------------------------------
# STEP 3 + 4 + 5: the main /analyze endpoint
# ---------------------------------------------------------------------------
@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    # Save the uploaded audio to a temporary file so teammates' functions
    # (which expect a file path) can read it.
    suffix = os.path.splitext(file.filename or "")[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        audio_path = tmp.name

    try:
        # 1. Speech-to-text
        transcript_result = run_transcription(audio_path)
        transcript = transcript_result.get("transcript", "")

        # 2. Voice authenticity
        voice_result = run_voice_analysis(audio_path)

        # 3. Scam detection (on the transcript)
        scam_result = run_scam_analysis(transcript)

        # 4. Combine into an overall risk score
        risk_result = run_risk_engine(voice_result, scam_result)

        # Assemble the final response before recording it in the ledger
        final_result = {
            "transcript": transcript,
            "voice_risk": voice_result.get("voice_risk", 50),
            "scam_risk": scam_result.get("scam_risk", 0),
            "overall_risk": risk_result.get("overall_risk", 50),
            "risk_level": risk_result.get("risk_level", "SUSPICIOUS"),
            "threats": scam_result.get("threats", []),
            "recommended_action": risk_result.get("recommended_action", "Exercise caution."),
        }

        # 5. Record the result in the ledger
        ledger_result = run_ledger(final_result)
        final_result["ledger_status"] = ledger_result.get("ledger_status", "Not Recorded")

        return final_result
    finally:
        # Clean up the temp audio file
        if os.path.exists(audio_path):
            os.remove(audio_path)
