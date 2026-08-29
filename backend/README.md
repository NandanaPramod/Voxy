# Voxy Backend

## What this is

The FastAPI bridge that connects all the Voxy modules together. Right now
it runs fully end-to-end using **placeholder logic** for the modules that
teammates haven't finished yet — nothing is broken or blocked.

## How to run it

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000 — you should see:
```json
{"status": "Voxy backend is running"}
```

## Testing the /analyze endpoint

Go to http://127.0.0.1:8000/docs (FastAPI's built-in test page), open
`POST /analyze`, click "Try it out", upload any audio file, and hit
Execute. You'll get back the full JSON result shape, even before the ML
modules are finished.

## How the pipeline connects to teammates' work

`app/main.py` tries to import each teammate's real function from the `ml/`
folder. **If a module isn't there yet, or throws an error, it silently
falls back to safe dummy data** — so you never have to wait on anyone.

| Module | Expected file | Expected function |
|---|---|---|
| Speech-to-text | `ml/speech/transcriber.py` | `transcribe_audio(audio_path)` |
| Voice authenticity | `ml/voice/voice_detector.py` | `analyze_voice(audio_path)` |
| Scam detection | `ml/scam/scam_detector.py` | `analyze_scam(transcript)` |
| Risk engine | `ml/scam/risk_engine.py` | `calculate_risk(voice_result, scam_result)` |
| Ledger | `backend/app/services/ledger.py` | `record_scam_pattern(final_result)` |

**You never need to edit `main.py` when a teammate finishes their module.**
As soon as they push their file with the exact function name and output
shape from the team contract, the backend picks it up automatically.

The `ml/` folder here currently contains placeholder stub files (each
with a `TODO` comment) so the project runs standalone. Teammates should
replace the contents of *their own file* with real logic — the function
name, inputs, and output shape must stay exactly as documented.

## Folder structure

```text
backend/
├── requirements.txt
├── README.md
└── app/
    ├── main.py          <- you are mainly working here
    ├── __init__.py
    ├── api/             <- reserved for future route splitting
    ├── models/          <- reserved for future request/response schemas
    └── services/
        └── ledger.py    <- Member 6 owns this (ledger + testing)
```
