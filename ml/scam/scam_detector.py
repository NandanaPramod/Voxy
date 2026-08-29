"""
scam_detector.py
-----------------
Scam Detection + Risk Engine module for the Voxy / VoxVeritas SIH 2026 project.

Owner: Monu (branch: scam-risk)
Responsibility: Scam Detection (analyze_scam) + Risk Engine (calculate_risk)

This module is intentionally kept simple, explainable, and dependency-free
(uses only Python's standard library) so it can be understood, tested, and
integrated quickly by the rest of the team.

Design notes / prototype limitations:
- Detection is based on regex/keyword pattern matching + a simple weighted
  score. It is NOT a trained ML/NLP model. This is intentional for an SIH
  prototype: it is fast, fully explainable, and easy to justify to judges,
  but it will miss cleverly worded scams and can still be fooled by
  phrasing not covered by the patterns below.
- False-positive reduction uses simple negation-window checks (e.g.
  "never share your OTP"), not true NLP negation/dependency parsing.
  It handles the common cases from the brief but is not bulletproof.
- Future extension (not implemented now, kept simple on purpose): add
  Tamil/Hindi keyword pattern sets alongside the English ones, and a small
  ML classifier trained on real labelled call transcripts later.
"""

from __future__ import annotations

import re
from typing import TypedDict


# ---------------------------------------------------------------------------
# Type definitions
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

    # OTP / verification code requests
    "OTP Request": [
        r"\b(tell|share|give|send|provide|read out|type in|enter)\b.{0,20}\b(otp|one[\s-]?time password|verification code|security code)\b",
        r"\bwhat('?s| is)\b.{0,15}\b(otp|one[\s-]?time password|verification code)\b",
        r"\b(otp|one[\s-]?time password|verification code)\b.{0,20}\b(please|now|immediately|required|needed)\b",
    ],

    # CVV requests
    "CVV Request": [
        r"\b(tell|share|give|send|provide|read out|type in|enter)\b.{0,20}\bcvv\b",
        r"\bcvv\b.{0,20}\b(please|now|immediately|required|needed)\b",
    ],

    # PIN requests
    "PIN Request": [
        r"\b(tell|share|give|send|provide|read out|type in|enter)\b.{0,20}\b(pin|atm pin|upi pin)\b",
        r"\b(pin|atm pin|upi pin)\b.{0,20}\b(please|now|immediately|required|needed)\b",
    ],

    # Bank impersonation
    "Bank Impersonation": [
        r"\b(calling|speaking)\b.{0,20}\b(from|with)\b.{0,20}\b(bank|banking|branch)\b",
        r"\b(i am|i'm|this is)\b.{0,20}\b(from|with)\b.{0,20}\b(your )?(bank|banking|branch)\b",
        r"\b(bank|bank officer|bank manager|bank representative)\b.{0,20}\b(calling|speaking)\b",
    ],

    # KYC-related scams
    "KYC Scam": [
        r"\bkyc\b.{0,30}\b(expired|expire|update|verify|verification|complete|suspend|blocked)\b",
        r"\b(update|verify|complete|submit)\b.{0,20}\bkyc\b",
        r"\bkyc\b.{0,20}\b(required|mandatory|needed|pending)\b",
    ],

    # Account blocking / suspension threats
    "Account Blocked Threat": [
        r"\b(account|bank account|card)\b.{0,30}\b(blocked|block|suspended|suspend|deactivated|deactivate|closed|close)\b",
        r"\b(block|suspend|deactivate|close)\b.{0,20}\b(your )?(account|card)\b",
    ],

    # Urgency / pressure
    "Urgency": [
        r"\b(immediately|urgent|urgently|right now|act now|hurry|asap)\b",
        r"\b(within|in)\b.{0,10}\b(minutes?|hours?)\b",
        r"\bdon't delay\b",
    ],

    # Payment requests
    "Payment Request": [
        r"\b(send|transfer|pay|make|deposit)\b.{0,30}\b(payment|money|amount|cash|funds)\b",
        r"\b(payment|money|amount|cash|funds)\b.{0,20}\b(send|transfer|pay)\b",
        r"\b(make a payment|send money|transfer money)\b",
    ],

    # UPI requests
    "UPI Request": [
        r"\b(send|transfer|pay)\b.{0,20}\b(through|via|using)\b.{0,10}\bupi\b",
        r"\bupi\b.{0,30}\b(payment|transfer|send|pay)\b",
        r"\bscan\b.{0,20}\b(qr|qr code)\b",
        r"\bupi pin\b",
    ],

    # Police / arrest / legal threats
    "Police/Arrest Threat": [
        r"\b(police|cyber crime|cybercrime|court|legal case)\b.{0,40}\b(arrest|arrested|case|crime|complaint|warrant)\b",
        r"\b(arrest|arrested|jail|prison|warrant)\b.{0,30}\b(you|your)\b",
        r"\b(you|your)\b.{0,30}\b(arrest|arrested|jail|prison|warrant)\b",
    ],

    # Sensitive personal / financial information
    "Sensitive Information Request": [
        r"\b(tell|share|give|send|provide|read out|enter)\b.{0,25}\b(account number|bank details|card number|password|secret|personal details)\b",
        r"\b(share|give|send|provide)\b.{0,20}\b(personal information|personal details|bank details)\b",
    ],
}


# ---------------------------------------------------------------------------
# Basic false-positive / negation protection
# ---------------------------------------------------------------------------

NEGATION_CUES = [
    "never share",
    "never give",
    "never tell",
    "don't share",
    "do not share",
    "dont share",
    "won't ask",
    "will not ask",
    "wont ask",
    "should not share",
    "shouldn't share",
    "please don't",
    "please do not",
    "avoid sharing",
    "don't give",
    "do not give",
    "don't reveal",
    "do not reveal",
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
        Dictionary containing:
        - scam_risk: integer from 0 to 100
        - threats: detected scam category names

    Note:
        This is a rule-based prototype using regex, keyword patterns,
        weighted scoring, and basic negation handling.
    """

    if not transcript or not transcript.strip():
        return {
            "scam_risk": 0,
            "threats": []
        }

    sentences = _split_sentences(transcript)
    detected_categories: set[str] = set()

    for sentence in sentences:

        lowered_sentence = sentence.lower()

        # Avoid obvious warning/disclaimer sentences.
        if _sentence_has_negation(lowered_sentence):
            continue

        for category, patterns in CATEGORY_PATTERNS.items():

            # Count each category only once.
            if category in detected_categories:
                continue

            for pattern in patterns:

                if re.search(pattern, lowered_sentence):
                    detected_categories.add(category)
                    break

    # Calculate weighted score.
    raw_score = sum(
        CATEGORY_WEIGHTS[category]
        for category in detected_categories
    )

    # Keep score between 0 and 100.
    scam_risk = min(raw_score, 100)

    return {
        "scam_risk": scam_risk,
        "threats": sorted(
            detected_categories,
            key=lambda category: -CATEGORY_WEIGHTS[category]
        ),
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
    """Map a 0-100 risk score to a risk level and recommended action."""

    for low, high, level, action in RISK_LEVELS:

        if low <= overall_risk <= high:
            return level, action

    return "LOW", "No immediate threat detected"


def calculate_risk(
    voice_result: VoiceResult,
    scam_result: ScamResult
) -> RiskResult:
    """
    Combine voice risk and scam risk using an explainable formula.

    Formula:

        Overall Risk =
            (Voice Risk × 0.4) +
            (Scam Risk × 0.6)
    """

    voice_risk = (
        voice_result.get("voice_risk", 0)
        if voice_result
        else 0
    )

    scam_risk = (
        scam_result.get("scam_risk", 0)
        if scam_result
        else 0
    )

    # Defensive clamping.
    voice_risk = max(0, min(100, voice_risk))
    scam_risk = max(0, min(100, scam_risk))

    overall_risk = round(
        (voice_risk * VOICE_WEIGHT)
        + (scam_risk * SCAM_WEIGHT)
    )

    overall_risk = max(0, min(100, overall_risk))

    risk_level, recommended_action = _classify_risk(
        overall_risk
    )

    return {
        "overall_risk": overall_risk,
        "risk_level": risk_level,
        "recommended_action": recommended_action,
    }


# ---------------------------------------------------------------------------
# SECTION 4: Automatic local testing
# ---------------------------------------------------------------------------

def _run_local_tests() -> None:
    """
    Run predefined test cases covering common scam scenarios.
    """

    test_cases = [

        (
            "Normal conversation",
            "Hey, are we meeting tomorrow for lunch?"
        ),

        (
            "OTP scam",
            "I am calling from your bank. Your account will be blocked immediately. Tell me your OTP now."
        ),

        (
            "KYC scam",
            "Your KYC has expired. Complete your KYC immediately or your account will be suspended."
        ),

        (
            "Police/arrest scam",
            "This is cyber crime police. A legal case has been registered against you. You will be arrested unless you make the payment."
        ),

        (
            "UPI/payment scam",
            "Send the payment immediately through UPI. Scan this QR code now."
        ),

        (
            "Negation / false positive",
            "Never share your OTP, PIN, or CVV with anyone."
        ),
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

    voice_result = {
        "voice_risk": 70
    }

    scam_result = analyze_scam(
        "Your bank account will be blocked. Tell me your OTP."
    )

    final_result = calculate_risk(
        voice_result,
        scam_result
    )

    print(f"\nvoice_result = {voice_result}")
    print(f"scam_result  = {scam_result}")
    print(f"final_result = {final_result}")


# ---------------------------------------------------------------------------
# SECTION 5: Interactive manual testing
# ---------------------------------------------------------------------------

def _run_interactive_test() -> None:
    """
    Allow the user to enter custom transcripts from the terminal.

    This is only for local testing.
    It does not run when the backend imports this module.
    """

    print("\n" + "=" * 70)
    print("INTERACTIVE SCAM TEST")
    print("=" * 70)

    print("Type a transcript and press Enter.")
    print("Type 'exit' to stop.\n")

    while True:

        transcript = input("Enter transcript: ").strip()

        if transcript.lower() == "exit":
            print("\nExiting interactive test.")
            break

        if not transcript:
            print("Please enter a transcript.\n")
            continue

        result = analyze_scam(transcript)

        print("\nResult:")
        print(f"Scam Risk: {result['scam_risk']}/100")

        if result["threats"]:

            print("Detected Threats:")

            for threat in result["threats"]:
                print(f"  - {threat}")

        else:
            print("Detected Threats: None")

        print()


# ---------------------------------------------------------------------------
# Run local tests only when this file is executed directly.
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    _run_local_tests()

    _run_interactive_test()