// This object matches EXACTLY the JSON shape defined in the
// team's integration contract (Section 7 — Required Final
// Response Format). When the real backend is ready, the response
// from POST /analyze will look identical to this, so nothing in
// ResultsDashboard.jsx needs to change.

export const MOCK_RESULT = {
  transcript:
    'Hello, this is calling from your bank\'s security department. Your account will be blocked in 24 hours due to suspicious activity. To verify your identity, please share the OTP you just received.',
  voice_risk: 78,
  scam_risk: 92,
  overall_risk: 86,
  risk_level: 'CRITICAL',
  threats: ['Bank Impersonation', 'OTP Request', 'Urgency'],
  recommended_action:
    'Do not share your OTP or any financial information. Hang up and call your bank directly using the number on your card.',
  ledger_status: 'Recorded',
}
