from flask import Blueprint, request, jsonify
from app.services.federated import get_server
from app.services.ml_service import _engineer

federated_bp = Blueprint("federated", __name__)


@federated_bp.route("/api/federated/train", methods=["POST"])
def train():
    d = request.get_json(force=True)
    server = get_server()
    ok, msg = server.start_training(
        n_rounds=int(d.get("n_rounds", 10)),
        n_ponds=int(d.get("n_ponds", 11)),
        dp_noise=float(d.get("dp_noise", 0.0)),
    )
    return jsonify({"started": ok, "message": msg})


@federated_bp.route("/api/federated/status")
def status():
    return jsonify(get_server().get_state())


@federated_bp.route("/api/federated/predict", methods=["POST"])
def fl_predict():
    server = get_server()
    if server.status not in ("done", "training"):
        return jsonify({"error": "No federated model yet. Start training first."}), 400
    d = request.get_json(force=True)
    features = _engineer({
        "temperature":      float(d.get("temperature", 24)),
        "dissolved_oxygen": float(d.get("dissolved_oxygen", 7)),
        "ph":               float(d.get("ph", 7.2)),
        "turbidity":        float(d.get("turbidity", 15)),
        "ammonia":          float(d.get("ammonia", 0.01)),
        "nitrate":          float(d.get("nitrate", 2.0)),
        "fish_weight_g":    float(d.get("fish_weight_g", 80)),
    })
    pred = server.predict(features)
    return jsonify({
        "federated_prediction_g": round(pred, 4) if pred is not None else None,
        "model": "FedAvg + SMPC Ridge",
        "rounds_completed": server.current_round,
    })
