def calculate_risk(voice_result, scam_result):
    """
    TODO (Member 5): replace this with the real risk-combination logic.
    Must return: {"overall_risk": 0-100, "risk_level": "...", "recommended_action": "..."}
    """
    overall = round((voice_result.get("voice_risk", 50) + scam_result.get("scam_risk", 0)) / 2)
    if overall >= 80:
        level = "CRITICAL"
    elif overall >= 60:
        level = "HIGH_RISK"
    elif overall >= 30:
        level = "SUSPICIOUS"
    else:
        level = "LOW"
    return {"overall_risk": overall, "risk_level": level, "recommended_action": "Exercise caution."}
