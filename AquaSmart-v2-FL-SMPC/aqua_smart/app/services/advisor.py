"""
Rule-based + ML hybrid recommendation engine.
Mirrors the FishFeedingAdvisor from the notebook.
"""
from typing import Optional


THRESHOLDS = dict(
    temp_lo=20, temp_hi=28, temp_crit_lo=12, temp_crit_hi=35,
    do_min=5.0, do_crit=3.0,
    ph_min=6.5, ph_max=8.5,
    turb_max=30,
    ammo_tox=0.02, ammo_crit=0.06,
    nitrate_max=10,
)

STRATEGIES = {
    "STOP":     {"msg": "Do NOT feed - critical water conditions. Take immediate corrective action.", "mult": 0.0, "color": "#ef4444"},
    "REDUCE":   {"msg": "Reduce feeding by 30-50%. Suboptimal conditions detected.", "mult": 0.55, "color": "#f97316"},
    "NORMAL":   {"msg": "Normal feeding recommended. Conditions are within acceptable range.", "mult": 1.0, "color": "#22c55e"},
    "INCREASE": {"msg": "Excellent conditions - you may increase feed by ~10%.", "mult": 1.10, "color": "#3b82f6"},
}


def compute_wqi(temperature: float, dissolved_oxygen: float, ph: float) -> tuple[float, str]:
    """Water Quality Index (0-100) and category."""
    T = THRESHOLDS
    thermal_stress = max(0, T["temp_lo"] - temperature) + max(0, temperature - T["temp_hi"])
    w_temp = 100 * (1 - min(thermal_stress / 10, 1))
    w_do   = min(dissolved_oxygen, 8) / 8 * 100
    ph_dev = abs(ph - 7.0)
    w_ph   = 100 - min(ph_dev / 3, 1) * 100
    wqi    = round((w_temp + w_do + w_ph) / 3, 2)
    if wqi >= 80:   category = "Excellent"
    elif wqi >= 60: category = "Good"
    elif wqi >= 40: category = "Fair"
    else:           category = "Poor"
    return wqi, category


def determine_strategy(temperature: float, dissolved_oxygen: float, ph: float,
                       turbidity: float, ammonia: float) -> str:
    T = THRESHOLDS
    # Critical stop conditions
    if (temperature < T["temp_crit_lo"] or temperature > T["temp_crit_hi"]
            or dissolved_oxygen < T["do_crit"] or ammonia > T["ammo_crit"]):
        return "STOP"
    # Suboptimal conditions
    if (temperature < T["temp_lo"] or temperature > T["temp_hi"]
            or dissolved_oxygen < T["do_min"]
            or ph < T["ph_min"] or ph > T["ph_max"]
            or turbidity > T["turb_max"]
            or ammonia > T["ammo_tox"]):
        return "REDUCE"
    # Excellent conditions
    if (T["temp_lo"] + 2 <= temperature <= T["temp_hi"] - 2
            and dissolved_oxygen >= 7.0
            and 6.8 <= ph <= 8.0
            and turbidity < 10):
        return "INCREASE"
    return "NORMAL"


def get_parameter_alerts(temperature: float, dissolved_oxygen: float, ph: float,
                         turbidity: float, ammonia: float, nitrate: float) -> list:
    T = THRESHOLDS
    alerts = []

    if temperature < T["temp_crit_lo"] or temperature > T["temp_crit_hi"]:
        alerts.append({"param": "Temperature", "value": temperature, "unit": "°C", "severity": "critical",
                        "message": f"Critical temperature! Optimal: 22-26°C"})
    elif temperature < T["temp_lo"] or temperature > T["temp_hi"]:
        alerts.append({"param": "Temperature", "value": temperature, "unit": "°C", "severity": "warning",
                        "message": f"Temperature out of optimal range (20-28°C)"})

    if dissolved_oxygen < T["do_crit"]:
        alerts.append({"param": "Dissolved O₂", "value": dissolved_oxygen, "unit": "mg/L", "severity": "critical",
                        "message": "Critical DO! Fish may suffocate. Aerate immediately."})
    elif dissolved_oxygen < T["do_min"]:
        alerts.append({"param": "Dissolved O₂", "value": dissolved_oxygen, "unit": "mg/L", "severity": "warning",
                        "message": "Low dissolved oxygen (< 5 mg/L). Increase aeration."})

    if ph < T["ph_min"] or ph > T["ph_max"]:
        sev = "critical" if ph < 5.5 or ph > 9.5 else "warning"
        alerts.append({"param": "pH", "value": ph, "unit": "", "severity": sev,
                        "message": f"pH out of range (6.5-8.5). Current: {ph}"})

    if turbidity > T["turb_max"]:
        alerts.append({"param": "Turbidity", "value": turbidity, "unit": "NTU", "severity": "warning",
                        "message": "High turbidity reduces light penetration and O₂ production."})

    if ammonia > T["ammo_crit"]:
        alerts.append({"param": "Ammonia", "value": ammonia, "unit": "mg/L", "severity": "critical",
                        "message": "Toxic ammonia level! Perform water change immediately."})
    elif ammonia > T["ammo_tox"]:
        alerts.append({"param": "Ammonia", "value": ammonia, "unit": "mg/L", "severity": "warning",
                        "message": "Elevated ammonia. Reduce feeding & check filtration."})

    if nitrate > T["nitrate_max"]:
        alerts.append({"param": "Nitrate", "value": nitrate, "unit": "mg/L", "severity": "info",
                        "message": "Elevated nitrate. Consider partial water exchange."})

    return alerts


def build_recommendation(
    temperature: float, dissolved_oxygen: float, ph: float,
    turbidity: float, ammonia: float, nitrate: float,
    fish_weight_g: float, population: int, base_feed_kg: float,
    ml_prediction_g: Optional[float] = None
) -> dict:
    strategy = determine_strategy(temperature, dissolved_oxygen, ph, turbidity, ammonia)
    wqi, wqi_cat = compute_wqi(temperature, dissolved_oxygen, ph)
    alerts = get_parameter_alerts(temperature, dissolved_oxygen, ph, turbidity, ammonia, nitrate)
    info = STRATEGIES[strategy]

    if ml_prediction_g and ml_prediction_g > 0:
        # ML predicts per-fish feed in grams, scale to total kg
        total_feed_g = ml_prediction_g * population
        base_feed_from_ml = total_feed_g / 1000
        final_feed_kg = base_feed_from_ml * info["mult"]
    else:
        final_feed_kg = base_feed_kg * info["mult"]

    # Sanity clamp
    final_feed_kg = max(0, round(final_feed_kg, 3))

    confidence = "High" if not alerts else ("Low" if strategy == "STOP" else "Medium")

    return {
        "strategy": strategy,
        "message": info["msg"],
        "color": info["color"],
        "recommended_feed_kg": final_feed_kg,
        "ml_prediction_g": round(ml_prediction_g, 4) if ml_prediction_g else None,
        "water_quality_index": wqi,
        "wqi_category": wqi_cat,
        "multiplier": info["mult"],
        "parameter_alerts": alerts,
        "confidence": confidence,
    }
