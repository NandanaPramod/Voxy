// Risk level definitions for Voxy.
// 0-29 LOW, 30-59 SUSPICIOUS, 60-79 HIGH RISK, 80-100 CRITICAL

export const RISK_LEVELS = [
  { max: 29, label: "LOW", token: "safe", hex: "#2DE0A8", bg: "rgba(45,224,168,0.12)", border: "rgba(45,224,168,0.45)" },
  { max: 59, label: "SUSPICIOUS", token: "warn", hex: "#FFB020", bg: "rgba(255,176,32,0.12)", border: "rgba(255,176,32,0.45)" },
  { max: 79, label: "HIGH RISK", token: "danger", hex: "#FF4D6D", bg: "rgba(255,77,109,0.12)", border: "rgba(255,77,109,0.45)" },
  { max: 100, label: "CRITICAL", token: "critical", hex: "#FF2D55", bg: "rgba(255,45,85,0.12)", border: "rgba(255,45,85,0.45)" },
];

export function getRiskLevel(score) {
  const s = Math.max(0, Math.min(100, Number(score) || 0));
  return RISK_LEVELS.find((l) => s <= l.max) ?? RISK_LEVELS[RISK_LEVELS.length - 1];
}

export function riskHex(score) {
  return getRiskLevel(score).hex;
}
