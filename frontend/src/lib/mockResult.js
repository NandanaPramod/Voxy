// Mock analysis result used while the backend (POST /analyze) is not ready.
// Shape matches the Voxy backend contract exactly so the UI needs no changes
// when you switch lib/api.js USE_MOCK to false.

export function getMockResult(/* file */) {
  return {
    transcript:
      "Hello, this is your bank's fraud department. We've detected unusual activity on your account and your bank account will be blocked in the next 30 minutes unless you verify your identity now. Please provide the OTP sent to your phone immediately. Do not hang up, and do not tell anyone, or your account will be permanently locked.",
    voice_risk: 78,
    scam_risk: 92,
    overall_risk: 86,
    risk_level: "CRITICAL",
    threats: ["Bank Impersonation", "OTP Request", "Urgency", "Threat of Account Lock"],
    recommended_action:
      "End the call immediately and do not share any personal or financial information.",
    ledger_status: "Recorded",
  };
}
