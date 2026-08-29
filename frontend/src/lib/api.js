import { getMockResult } from "./mockResult";

// ---------------------------------------------------------------------------
// Voxy frontend → backend connection
//
// For now this returns MOCK data so the UI works without the backend.
// When the FastAPI backend is ready, set USE_MOCK to false.
//
// The backend must expose:  POST /analyze
// It should accept a multipart form field named "audio" containing the file,
// and return JSON in this exact shape:
//
// {
//   "transcript": "Hello, your bank account will be blocked.",
//   "voice_risk": 72,
//   "scam_risk": 90,
//   "overall_risk": 82,
//   "risk_level": "CRITICAL",
//   "threats": ["Bank Impersonation", "OTP Request", "Urgency"],
//   "recommended_action": "End the call immediately.",
//   "ledger_status": "Recorded"
// }
// ---------------------------------------------------------------------------

export const USE_MOCK = true;

// Change this to your backend URL when it is live.
export const BACKEND_URL = "http://localhost:8000/analyze";

export async function analyzeAudio(file) {
  if (!file) {
    throw new Error("No audio file provided.");
  }

  if (USE_MOCK) {
    // Simulate processing time for the loading screen.
    await new Promise((resolve) => setTimeout(resolve, 2600));
    return getMockResult(file);
  }

  const formData = new FormData();
  formData.append("audio", file);

  const response = await fetch(BACKEND_URL, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Backend error: " + response.status);
  }

  return response.json();
}
