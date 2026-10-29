import random, math
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from app.services import advisor, ml_service

dashboard_bp = Blueprint("dashboard", __name__)


def _sim(t: float) -> dict:
    temp  = round(max(15, min(35, 24 + 3*math.sin(t*.5) + random.gauss(0,.3))), 2)
    do    = round(max(1,  min(12,  7 - 1.5*math.sin(t*.4) + random.gauss(0,.2))), 2)
    ph    = round(max(5.5,min(9.5, 7.3 + .5*math.sin(t*.3) + random.gauss(0,.1))), 2)
    turb  = round(max(0,  min(80,  15 + 8*abs(math.sin(t*.2)) + random.gauss(0,1))), 1)
    ammo  = round(max(0,  min(.1,  .008 + .005*abs(math.sin(t*.15)) + random.gauss(0,.001))), 4)
    nit   = round(max(0,  min(20,  3.5 + 1.5*abs(math.sin(t*.1)) + random.gauss(0,.2))), 2)
    wqi, _ = advisor.compute_wqi(temp, do, ph)
    strat   = advisor.determine_strategy(temp, do, ph, turb, ammo)
    return dict(temperature=temp, dissolved_oxygen=do, ph=ph,
                turbidity=turb, ammonia=ammo, nitrate=nit,
                wqi=wqi, strategy=strat)


@dashboard_bp.route("/api/dashboard/current")
def current():
    t = datetime.now().timestamp() / 3600
    r = _sim(t)
    alerts = advisor.get_parameter_alerts(r["temperature"], r["dissolved_oxygen"],
                                          r["ph"], r["turbidity"], r["ammonia"], r["nitrate"])
    _, cat = advisor.compute_wqi(r["temperature"], r["dissolved_oxygen"], r["ph"])
    r.update(wqi_category=cat, alerts=alerts, alert_count=len(alerts),
             timestamp=datetime.now().isoformat())
    return jsonify(r)


@dashboard_bp.route("/api/dashboard/history")
def history():
    hours = int(request.args.get("hours", 24))
    now   = datetime.now()
    step  = hours / 48
    out   = []
    for i in range(48):
        ts = now - timedelta(hours=hours - i*step)
        r  = _sim(ts.timestamp() / 3600)
        r["timestamp"] = ts.isoformat()
        out.append(r)
    return jsonify(out)


@dashboard_bp.route("/api/dashboard/stats")
def stats():
    info = ml_service.get_model_info()
    return jsonify({
        "model_name":       info.get("model", "GradientBoosting"),
        "task_type":        info.get("task", "regression"),
        "features_count":   len(info.get("features", [])),
        "training_samples": info.get("training_samples", 5000),
        "note":             info.get("note", ""),
        "features":         info.get("features", []),
        "model_score":      (info.get("test_metrics") or {}).get("r2"),   # R2 on held-out test data
    })


@dashboard_bp.route("/api/dashboard/ponds")
def ponds():
    out = []
    for i in range(1, 5):
        t = datetime.now().timestamp() / 3600 + i * 1.3
        r = _sim(t)
        _, cat = advisor.compute_wqi(r["temperature"], r["dissolved_oxygen"], r["ph"])
        out.append({"id": i, "name": f"Pond {i}",
                    "population": random.randint(200, 800),
                    "avg_weight_g": round(random.uniform(80, 250), 1),
                    **r, "wqi_category": cat})
    return jsonify(out)
