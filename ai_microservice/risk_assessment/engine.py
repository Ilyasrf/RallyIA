from shared.database import Property


_RISK_MAP = {
    "low": 20,
    "medium": 50,
    "high": 80,
}

_ALIGNMENT_MATRIX = {
    ("low", "low"): ("Well-aligned", 0),
    ("low", "medium"): ("Moderate", 15),
    ("low", "high"): ("Mismatched", 40),
    ("medium", "low"): ("Moderate", 10),
    ("medium", "medium"): ("Well-aligned", 0),
    ("medium", "high"): ("Moderate", 15),
    ("high", "low"): ("Mismatched", 30),
    ("high", "medium"): ("Moderate", 10),
    ("high", "high"): ("Well-aligned", 0),
}

_EXPERIENCE_MODIFIER = {
    "beginner": 1.15,
    "intermediate": 1.0,
    "advanced": 0.85,
    "expert": 0.80,
}


def assess_risk(property: Property, user_risk_tolerance: str, user_experience: str) -> dict:
    tolerance = user_risk_tolerance.strip().lower()
    experience = user_experience.strip().lower()
    prop_risk = (property.risk_rating or "medium").strip().lower()

    base = _RISK_MAP.get(prop_risk, 50)

    lock_in = min(property.lock_in_years * 5, 30)

    yield_val = property.expected_yield if property.expected_yield else 5.0
    yield_factor = max(min((yield_val - 5.0) * 10, 30), 0)

    alignment_label, alignment_penalty = _ALIGNMENT_MATRIX.get(
        (tolerance, prop_risk), ("Moderate", 15)
    )

    raw_score = base * 0.40 + lock_in * 0.25 + yield_factor * 0.20 + alignment_penalty * 0.15

    exp_mod = _EXPERIENCE_MODIFIER.get(experience, 1.0)
    overall = min(round(raw_score * exp_mod, 1), 100)

    if overall <= 33:
        level = "Low"
    elif overall <= 66:
        level = "Medium"
    else:
        level = "High"

    explanation = _build_explanation(base, lock_in, yield_factor, yield_val,
                                     alignment_label, tolerance, property.lock_in_years,
                                     experience)

    return {
        "overall_score": overall,
        "risk_level": level,
        "breakdown": {
            "base_risk": round(base, 1),
            "lock_in_penalty": round(lock_in, 1),
            "yield_factor": round(yield_factor, 1),
            "user_alignment": round(alignment_penalty, 1),
        },
        "user_alignment": alignment_label,
        "explanation": explanation,
    }


def _build_explanation(base, lock_in, yield_factor, yield_val,
                       alignment_label, tolerance, lock_in_years, experience):
    parts = []

    if base <= 30:
        parts.append("Low base risk")
    elif base <= 60:
        parts.append("Moderate base risk")
    else:
        parts.append("High base risk")

    if lock_in_years <= 1:
        parts.append("short lock-in period allows quick exit")
    elif lock_in >= 20:
        parts.append(f"{lock_in_years}-year lock-in reduces liquidity")
    elif lock_in >= 10:
        parts.append(f"{lock_in_years}-year lock-in is manageable")
    else:
        parts.append(f"{lock_in_years}-year lock-in is short")

    if yield_factor >= 20:
        parts.append(f"{yield_val}% yield is above average (higher upside but more volatility)")
    elif yield_factor >= 10:
        parts.append(f"{yield_val}% yield is slightly above baseline")
    else:
        parts.append(f"{yield_val}% yield is conservative and stable")

    if alignment_label == "Well-aligned":
        parts.append(f"well-aligned with your {tolerance} risk tolerance")
    elif alignment_label == "Mismatched":
        parts.append(f"does not match your {tolerance} risk tolerance — proceed with caution")
    else:
        parts.append(f"partially matches your {tolerance} risk tolerance")

    if experience == "beginner":
        parts.append("score adjusted upward for beginner experience")

    return ". ".join(parts) + "."
