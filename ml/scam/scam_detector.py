"""
scam_detector.py
-----------------
Scam Detection + Risk Engine module for the Voxy / VoxVeritas SIH 2026 project.

Owner: Monu (branch: scam-risk)
Responsibility: Scam Detection (analyze_scam) + Risk Engine (calculate_risk)

This module is intentionally kept simple, explainable, and dependency-free
(uses only Python's standard library) so it can be understood, tested, and
integrated quickly by the rest of the team.

Design notes / prototype limitations (documented on purpose):
- Detection is based on regex/keyword pattern matching + a simple weighted
  score. It is NOT a trained ML/NLP model. This is intentional for an SIH
  prototype: it is fast, fully explainable, and easy to justify to judges,
  but it will miss cleverly worded scams and can still be fooled by
  phrasing not covered by the patterns below.
- False-positive reduction uses simple negation-window checks (e.g. "never
  share your OTP"), not true NLP negation/dependency parsing. It handles the
  common cases from the brief but is not bulletproof.
- Future extension (not implemented now, kept simple on purpose): add
  Tamil/Hindi keyword pattern sets alongside the English ones, and a small
  ML classifier trained on real labelled call transcripts later.
"""

from __future__ import annotations

import re
from typing import TypedDict


# ---------------------------------------------------------------------------
# Type definitions (for readability / editor support only — no runtime cost)
# ---------------------------------------------------------------------------

class ScamResult(TypedDict):
    scam_risk: int
    threats: list[str]


class VoiceResult(TypedDict, total=False):
    voice_risk: int


class RiskResult(TypedDict):
    overall_risk: int
    risk_level: str
    recommended_action: str


# ---------------------------------------------------------------------------
# SECTION 1: Scam category definitions
# ---------------------------------------------------------------------------
# Each category maps to:
#   - a severity weight (how dangerous this signal is, out of 100)
#   - a list of regex patterns describing REQUEST-style phrasing (not just
#     the bare presence of a sensitive word).
#
# Patterns are written to catch common paraphrasing, not one fixed sentence.

CATEGORY_WEIGHTS: dict[str, int] = {
    "OTP Request": 30,
    "CVV Request": 25,
    "PIN Request": 25,
    "Bank Impersonation": 25,
    "KYC Scam": 20,
    "Account Blocked Threat": 20,
    "Urgency": 15,
    "Payment Request": 20,
    "UPI Request": 20,
    "Police/Arrest Threat": 25,
    "Sensitive Information Request": 30,
}

CATEGORY_PATTERNS: dict[str, list[str]] = {
    "OTP Request": [
        r"\b(tell|share|give|send|provide|read out|type in|enter)\b.{0,20}\b(otp|one[\s-]?time password|verification code|security code)\b",
        r"\bwhat('?s| is)\b.{0,15}\b(otp|one[\s-]?time password|verification code)\b",
        r"\b(otp|one[\s-]?time password|verification code)\b.{0,20}\b(please|now|immediately|required|needed)\b",
    ],
    "CVV Request": [
        r"\b(tell|share|give|send|provide|read out|type in|enter)\b.{0,20}\bcvv\b",
        r"\bcvv\b.{0,20}\b(number|code|please|now|required|needed)\b",
        r"\b(3|three)[\s-]digit\b.{0,15}\b(code|number)\b.{0,15}\bcard\b",
    ],
    "PIN Request": [
        r"\b(tell|share|give|send|provide|read out|type in|enter)\b.{0,20}\b(pin|atm pin|card pin)\b",
        r"\b(pin|atm pin|card pin)\b.{0,20}\b(number|please|now|required|needed)\b",
    ],
    "Bank Impersonation": [
        r"\b(i am|this is|calling from|speaking from)\b.{0,20}\b(your bank|bank official|bank representative|bank department|bank branch)\b",
        r"\b(bank manager|bank officer|bank executive)\b.{0,20}\b(calling|speaking)\b",
        r"\bfrom\b.{0,10}\b(sbi|hdfc|icici|axis bank|rbi)\b",
    ],
    "KYC Scam": [
        r"\bkyc\b.{0,20}\b(expired|expire|pending|update|verify|verification|incomplete|suspend|suspended)\b",
        r"\b(complete|update|verify)\b.{0,15}\byour kyc\b",
    ],
    "Account Blocked Threat": [
        r"\b(account|card|sim)\b.{0,20}\b(will be|going to be|about to be)\b.{0,10}\b(blocked|suspended|deactivated|frozen|closed)\b",
        r"\b(account|card|sim)\b.{0,15}\b(blocked|suspended|deactivated|frozen)\b.{0,15}\b(immediately|today|soon|unless)\b",
    ],
    "Urgency": [
        r"\b(immediately|urgent|urgently|right now|within\s+\d+\s*(minutes|hours)|last chance|final warning|act now|do it now)\b",
    ],
    "Payment Request": [
        r"\b(make|send|pay|transfer|deposit)\b.{0,20}\b(the )?payment\b",
        r"\b(pay|deposit)\b.{0,15}\b(fine|fee|penalty|charges)\b.{0,15}\b(immediately|now|today)\b",
    ],
    "UPI Request": [
        r"\b(upi|google pay|gpay|phonepe|paytm)\b.{0,20}\b(id|number|pin|payment|transfer|scan|qr)\b",
        r"\bscan\b.{0,15}\b(this )?qr( code)?\b",
    ],
    "Police/Arrest Threat": [
        r"\b(cyber crime|cyber cell|police|court|legal)\b.{0,20}\b(case|complaint|warrant|notice)\b.{0,20}\b(against you|registered|filed)\b",
        r"\byou will be\b.{0,15}\barrested\b",
        r"\b(arrest|jail|warrant)\b.{0,20}\b(unless|if you don't|if you do not)\b",
    ],
    "Sensitive Information Request": [
        r"\b(share|tell|give|send|provide)\b.{0,20}\b(aadhaar|aadhar|pan card|passport number|account number|bank details)\b",
        r"\b(aadhaar|aadhar|pan card|passport number|account number)\b.{0,15}\b(number|details)\b.{0,15}\b(please|now|required|needed)\b",
    ],
}

# Words that, when found in a sentence, suggest the speaker is warning
# AGAINST sharing information rather than requesting it — used to reduce
# obvious false positives such as "never share your OTP with anyone."
NEGATION_CUES = [
    "never share", "never give", "never tell", "don't share", "do not share",
    "dont share", "won't ask", "will not ask", "wont ask", "should not share",
    "shouldn't share", "please don't", "please do not", "avoid sharing",
    "don't give", "do not give", "don't reveal", "do not reveal",
]


def _split_sentences(transcript: str) -> list[str]:
    """Split a transcript into rough sentences for localized pattern checks."""
    parts = re.split(r"(?<=[.!?])\s+", transcript.strip())
    return [p for p in parts if p]


def _sentence_has_negation(sentence: str) -> bool:
    """Return True if the sentence looks like a warning, not a request."""
    lowered = sentence.lower()
    return any(cue in lowered for cue in NEGATION_CUES)


# ---------------------------------------------------------------------------
# SECTION 2: Scam Detection
# ---------------------------------------------------------------------------

def analyze_scam(transcript: str) -> ScamResult:
    """
    Analyze a call transcript for scam-related signals.

    Args:
        transcript: The full text of a call (already transcribed to text).

    Returns:
        A dictionary with:
            - "scam_risk": int, 0-100
            - "threats": list of detected scam category names (each category
              appears at most once, even if multiple patterns/keywords for
              that category are found in the transcript).

    Note:
        This is a rule-based prototype (regex + keyword patterns + a simple
        negation check), not a trained NLP model. It is meant to be fast and
        explainable for an SIH 2026 demo, not production-grade accuracy.
    """
    if not transcript or not transcript.strip():
        return {"scam_risk": 0, "threats": []}

    sentences = _split_sentences(transcript)
    detected_categories: set[str] = set()

    for sentence in sentences:
        lowered_sentence = sentence.lower()

        # Skip sentences that look like warnings/disclaimers rather than
        # actual requests (basic false-positive guard).
        if _sentence_has_negation(lowered_sentence):
            continue

        for category, patterns in CATEGORY_PATTERNS.items():
            if category in detected_categories:
                continue  # already counted this category once
            for pattern in patterns:
                if re.search(pattern, lowered_sentence):
                    detected_categories.add(category)
                    break

    # Weighted scoring: sum the weight of each unique detected category.
    raw_score = sum(CATEGORY_WEIGHTS[category] for category in detected_categories)
    scam_risk = min(raw_score, 100)  # cap at 100

    return {
        "scam_risk": scam_risk,
        "threats": sorted(detected_categories, key=lambda c: -CATEGORY_WEIGHTS[c]),
    }


# ---------------------------------------------------------------------------
# SECTION 3: Risk Engine
# ---------------------------------------------------------------------------

VOICE_WEIGHT = 0.4
SCAM_WEIGHT = 0.6

RISK_LEVELS: list[tuple[int, int, str, str]] = [
    (0, 29, "LOW", "No immediate threat detected"),
    (30, 59, "SUSPICIOUS", "Exercise caution"),
    (60, 79, "HIGH RISK", "Do not share personal information"),
    (80, 100, "CRITICAL", "End the call immediately"),
]


def _classify_risk(overall_risk: int) -> tuple[str, str]:
    """Map a 0-100 overall risk score to (risk_level, recommended_action)."""
    for low, high, level, action in RISK_LEVELS:
        if low <= overall_risk <= high:
            return level, action
    return "LOW", "No immediate threat detected"  # defensive fallback


def calculate_risk(voice_result: VoiceResult, scam_result: ScamResult) -> RiskResult:
    """
    Combine voice-based risk and scam/conversation-based risk into a single
    overall risk score, using a simple explainable weighted formula:

        overall_risk = (voice_risk * VOICE_WEIGHT) + (scam_risk * SCAM_WEIGHT)

    Scam risk is weighted higher than voice risk because the conversation
    content is direct evidence of scam behavior, while voice analysis only
    estimates the likelihood that the voice is AI-generated.

    Args:
        voice_result: dict from the teammate's voice detection module,
            expected to contain "voice_risk" (0-100). Missing/invalid
            values are treated as 0.
        scam_result: dict from analyze_scam(), containing "scam_risk"
            (0-100) and "threats".

    Returns:
        A dictionary with "overall_risk", "risk_level", and
        "recommended_action".
    """
    voice_risk = voice_result.get("voice_risk", 0) if voice_result else 0
    scam_risk = scam_result.get("scam_risk", 0) if scam_result else 0

    # Defensive clamping in case an upstream module sends an out-of-range value.
    voice_risk = max(0, min(100, voice_risk))
    scam_risk = max(0, min(100, scam_risk))

    overall_risk = round((voice_risk * VOICE_WEIGHT) + (scam_risk * SCAM_WEIGHT))
    overall_risk = max(0, min(100, overall_risk))

    risk_level, recommended_action = _classify_risk(overall_risk)

    return {
        "overall_risk": overall_risk,
        "risk_level": risk_level,
        "recommended_action": recommended_action,
    }


# ---------------------------------------------------------------------------
# SECTION 4: Local testing (does NOT run when the backend imports this file)
# ---------------------------------------------------------------------------

def _run_local_tests() -> None:
    """Quick manual test cases covering the scenarios from the SIH brief."""

    test_cases = [
        ("Normal conversation", "Hey, are we meeting tomorrow for lunch?"),
        ("OTP scam", "I am calling from your bank. Your account will be blocked immediately. Tell me your OTP now."),
        ("KYC scam", "Your KYC has expired. Complete your KYC immediately or your account will be suspended."),
        ("Police/arrest scam", "This is cyber crime police. A legal case has been registered against you. You will be arrested unless you make the payment."),
        ("UPI/payment scam", "Send the payment immediately through UPI. Scan this QR code now."),
        ("Negation / false positive", "Never share your OTP, PIN, or CVV with anyone."),
    ]

    print("=" * 70)
    print("SCAM DETECTOR — LOCAL TEST RUN")
    print("=" * 70)

    for label, transcript in test_cases:
        result = analyze_scam(transcript)
        print(f"\n[{label}]")
        print(f"Transcript: {transcript}")
        print(f"Result: {result}")

    print("\n" + "=" * 70)
    print("RISK ENGINE — LOCAL TEST RUN")
    print("=" * 70)

    voice_result = {"voice_risk": 70}
    scam_result = analyze_scam("Your bank account will be blocked. Tell me your OTP.")
    final_result = calculate_risk(voice_result, scam_result)
    print(f"\nvoice_result = {voice_result}")
    print(f"scam_result  = {scam_result}")
    print(f"final_result = {final_result}")


if __name__ == "__main__":
    _run_local_tests()