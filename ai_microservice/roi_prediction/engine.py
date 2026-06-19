from shared.database import Property


_LOCATION_APPRECIATION = {
    "casablanca": 3.5,
    "marrakech": 4.0,
    "rabat": 3.0,
    "tangier": 4.5,
    "fes": 2.5,
    "kenitra": 3.0,
    "agadir": 2.5,
    "oujda": 2.0,
    "tanger": 4.5,
}

_RISK_PREMIUM = {
    "low": 1.0,
    "medium": 1.1,
    "high": 1.25,
}

_TYPE_MODIFIER = {
    "commercial": 1.1,
    "residential": 1.0,
    "mixed-use": 1.05,
    "industrial": 1.15,
    "land": 1.2,
}


def predict_roi(property: Property, capital: float, lock_in_years: int) -> dict:
    base_yield = property.expected_yield if property.expected_yield else 5.0

    location_key = (property.location or "").strip().lower()
    location_appreciation = 0.0
    for key, rate in _LOCATION_APPRECIATION.items():
        if key in location_key:
            location_appreciation = rate
            break

    risk_key = (property.risk_rating or "medium").strip().lower()
    risk_premium = _RISK_PREMIUM.get(risk_key, 1.0)

    type_key = (property.property_type or "").strip().lower()
    type_modifier = _TYPE_MODIFIER.get(type_key, 1.0)

    raw_annual = base_yield + location_appreciation
    adjusted_annual = raw_annual * risk_premium * type_modifier
    total_return_pct = round(adjusted_annual * lock_in_years, 2)

    annual_return_mad = round(capital * adjusted_annual / 100, 2)
    total_return_mad = round(annual_return_mad * lock_in_years, 2)

    explanation = _build_explanation(base_yield, location_appreciation, risk_premium,
                                     type_modifier, adjusted_annual, annual_return_mad,
                                     total_return_mad, capital, lock_in_years)

    return {
        "annual_return_pct": round(adjusted_annual, 2),
        "total_return_pct": total_return_pct,
        "annual_return_mad": annual_return_mad,
        "total_return_mad": total_return_mad,
        "breakdown": {
            "base_yield": round(base_yield, 2),
            "location_appreciation": round(location_appreciation, 2),
            "risk_premium": round(risk_premium, 2),
            "property_type_modifier": round(type_modifier, 2),
        },
        "explanation": explanation,
    }


def _build_explanation(base_yield, location_appr, risk_prem, type_mod,
                       adjusted_annual, annual_mad, total_mad, capital, lock_in):
    parts = []

    parts.append(f"Projected annual return of {adjusted_annual:.1f}%")

    if base_yield > 0:
        parts.append(f"base yield of {base_yield:.1f}%")
    if location_appr > 0:
        parts.append(f"location appreciation of {location_appr:.1f}%")

    if risk_prem > 1.0:
        parts.append(f"adjusted up for {risk_prem:.2f}x risk premium")
    if type_mod != 1.0:
        parts.append(f"modified by {type_mod:.2f}x for property type")

    total_invested = capital
    parts.append(
        f"on a {total_invested:.0f} MAD investment over {lock_in} years, "
        f"that is approximately {annual_mad:.0f} MAD/year ({total_mad:.0f} MAD total)"
    )

    return ". ".join(parts) + "."
