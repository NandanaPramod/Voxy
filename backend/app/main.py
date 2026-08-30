"""
Voxy Backend - Main API

Pipeline:

Audio Upload
    ↓
Speech-to-Text
    ↓
Voice Risk Analysis
    ↓
Scam Detection
    ↓
Risk Calculation
    ↓
Ledger
    ↓
JSON Result
    ↓
Frontend

Each module has a fallback so the backend can continue
working during team integration.
"""

import os
import shutil
import sys
import tempfile

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# PROJECT PATH
# ============================================================

# main.py is inside:
# Voxy/backend/app/main.py
#
# Go up 2 levels:
# app -> backend -> Voxy

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

if PROJECT_ROOT not in sys.path:

    sys.path.insert(
        0,
        PROJECT_ROOT
    )


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Voxy Backend",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def read_root():

    return {
        "status": "Voxy backend is running"
    }


# ============================================================
# TRANSCRIPTION MODULE
# ============================================================

def run_transcription(audio_path: str):

    try:

        from ml.speech.transcriber import (
            transcribe_audio
        )

        return transcribe_audio(
            audio_path
        )

    except Exception as error:

        print(
            "Transcription module error:",
            error
        )

        return {
            "transcript": "Demo transcript unavailable."
        }


# ============================================================
# VOICE ANALYSIS MODULE
# ============================================================

def run_voice_analysis(audio_path: str):

    try:

        from ml.voice.voice_detector import analyze_voice

        return analyze_voice(audio_path)

    except Exception as error:

        print(
            "Voice analysis module error:",
            error
        )

        return {
            "voice_risk": 50,
            "prediction": "UNKNOWN"
        }


# ============================================================
# SCAM DETECTION MODULE
# ============================================================

def run_scam_analysis(transcript: str):

    try:

        from ml.scam.scam_detector import analyze_scam

        return analyze_scam(transcript)

    except Exception as error:

        print(
            "Scam detection module error:",
            error
        )

        return {
            "scam_risk": 0,
            "threats": []
        }


# ============================================================
# RISK ENGINE
# ============================================================

def run_risk_engine(
    voice_result: dict,
    scam_result: dict
):

    try:

        from ml.scam.scam_detector import calculate_risk

        return calculate_risk(
            voice_result,
            scam_result
        )

    except Exception as error:

        print(
            "Risk engine error:",
            error
        )

        voice_risk = voice_result.get(
            "voice_risk",
            50
        )

        scam_risk = scam_result.get(
            "scam_risk",
            0
        )

        overall_risk = round(
            (voice_risk + scam_risk) / 2
        )

        if overall_risk >= 80:

            risk_level = "CRITICAL"

            recommended_action = (
                "End the call immediately and verify "
                "the caller independently."
            )

        elif overall_risk >= 60:

            risk_level = "HIGH_RISK"

            recommended_action = (
                "Do not send money or share "
                "personal information."
            )

        elif overall_risk >= 30:

            risk_level = "SUSPICIOUS"

            recommended_action = (
                "Exercise caution and verify the caller."
            )

        else:

            risk_level = "LOW"

            recommended_action = (
                "No major scam indicators detected."
            )

        return {
            "overall_risk": overall_risk,
            "risk_level": risk_level,
            "recommended_action": recommended_action
        }


# ============================================================
# LEDGER MODULE
# ============================================================

def run_ledger(final_result: dict):
    try:
        from backend.app.services.ledger import record_scam_pattern

        result = record_scam_pattern(final_result)

        print("LEDGER SUCCESS:", result)

        return result

    except Exception as error:
        print("LEDGER ERROR:", repr(error))

        return {
            "ledger_status": "Not Recorded"
        }


# ============================================================
# MAIN ANALYZE ENDPOINT
# ============================================================

@app.post("/analyze")

def analyze(
    file: UploadFile = File(...)
):

    # Get original file extension.
    suffix = os.path.splitext(
        file.filename or ""
    )[1]

    # Default to WAV if extension is missing.
    if not suffix:

        suffix = ".wav"


    # --------------------------------------------------------
    # Save uploaded file temporarily.
    # --------------------------------------------------------

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temporary_file:

        shutil.copyfileobj(
            file.file,
            temporary_file
        )

        audio_path = temporary_file.name


    try:

        # ====================================================
        # STEP 1: SPEECH TO TEXT
        # ====================================================

        print("STEP 1: starting transcription...")

        transcription_result = run_transcription(
            audio_path
        )

        print("STEP 1: done")

        transcript = transcription_result.get(
            "transcript",
            ""
        )


        # ====================================================
        # STEP 2: VOICE ANALYSIS
        # ====================================================

        print("STEP 2: starting voice analysis...")

        voice_result = run_voice_analysis(
            audio_path
        )

        print("STEP 2: done")


        # ====================================================
        # STEP 3: SCAM DETECTION
        # ====================================================

        print("STEP 3: starting scam detection...")

        scam_result = run_scam_analysis(
            transcript
        )

        print("STEP 3: done")


        # ====================================================
        # STEP 4: RISK CALCULATION
        # ====================================================

        print("STEP 4: starting risk engine...")

        risk_result = run_risk_engine(
            voice_result,
            scam_result
        )

        print("STEP 4: done")


        # ====================================================
        # STEP 5: CREATE FINAL RESULT
        # ====================================================

        final_result = {

            "transcript": transcript,

            "voice_risk": voice_result.get(
                "voice_risk",
                50
            ),

            "scam_risk": scam_result.get(
                "scam_risk",
                0
            ),

            "overall_risk": risk_result.get(
                "overall_risk",
                50
            ),

            "risk_level": risk_result.get(
                "risk_level",
                "SUSPICIOUS"
            ),

            "threats": scam_result.get(
                "threats",
                []
            ),

            "recommended_action": risk_result.get(
                "recommended_action",
                "Exercise caution."
            )
        }


        # ====================================================
        # STEP 6: LEDGER
        #
        # Only suspicious or high-risk patterns are recorded.
        # ====================================================

        print("STEP 6: starting ledger...")

        if final_result["overall_risk"] >= 60:

            ledger_result = run_ledger(
                final_result
            )

        else:

            ledger_result = {

                "ledger_status": "Not Recorded"
            }

        print("STEP 6: done")


        # Add ledger information.

        final_result.update(
            ledger_result
        )


        # ====================================================
        # RETURN RESULT
        # ====================================================

        print("ALL STEPS DONE — returning result")

        return final_result


    finally:

        # ----------------------------------------------------
        # Delete temporary uploaded audio file.
        # ----------------------------------------------------

        if os.path.exists(audio_path):

            os.remove(audio_path)


# ============================================================
# LEDGER VERIFICATION ENDPOINT
# ============================================================
@app.get("/ledger/verify")
def verify_ledger_endpoint():

    try:
        from backend.app.services.ledger import verify_ledger

        return verify_ledger()

    except Exception as error:

        print(
            "Ledger verification error:",
            error
        )

        return {
            "valid": False,
            "error": str(error)
        }