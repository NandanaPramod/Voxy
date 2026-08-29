// Central place mapping the backend's risk_level string to colors.
// Keeping this in one file means every component (gauge, badges,
// action card) always agrees on what "CRITICAL" looks like.

export const RISK_THEME = {
  LOW: {
    color: 'var(--risk-low)',
    bg: 'var(--risk-low-bg)',
    label: 'Low Risk',
    message: 'This call looks safe.',
  },
  SUSPICIOUS: {
    color: 'var(--risk-suspicious)',
    bg: 'var(--risk-suspicious-bg)',
    label: 'Suspicious',
    message: 'Some patterns are worth a second look.',
  },
  'HIGH RISK': {
    color: 'var(--risk-high)',
    bg: 'var(--risk-high-bg)',
    label: 'High Risk',
    message: 'Multiple scam signals detected.',
  },
  HIGH: {
    color: 'var(--risk-high)',
    bg: 'var(--risk-high-bg)',
    label: 'High Risk',
    message: 'Multiple scam signals detected.',
  },
  CRITICAL: {
    color: 'var(--risk-critical)',
    bg: 'var(--risk-critical-bg)',
    label: 'Critical',
    message: 'Strong signs of an active scam.',
  },
}

export function getRiskTheme(level) {
  return RISK_THEME[level?.toUpperCase()] || RISK_THEME.SUSPICIOUS
}
