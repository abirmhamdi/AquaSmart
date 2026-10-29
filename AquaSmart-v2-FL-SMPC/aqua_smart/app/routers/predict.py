from flask import Blueprint, request, jsonify
from app.services import ml_service, advisor

predict_bp = Blueprint("predict", __name__)


@predict_bp.route("/api/predict", methods=["POST"])
def predict():
    d = request.get_json(force=True)
    row = {
        "temperature":      float(d["temperature"]),
        "dissolved_oxygen": float(d["dissolved_oxygen"]),
        "ph":               float(d["ph"]),
        "turbidity":        float(d["turbidity"]),
        "ammonia":          float(d["ammonia"]),
        "nitrate":          float(d.get("nitrate", 2.0)),
        "fish_weight_g":    float(d.get("fish_weight_g", 50.0)),
    }
    population    = int(d.get("population", 100))
    base_feed_kg  = float(d.get("base_feed_kg", 5.0))

    ml_pred = ml_service.predict(row)
    result  = advisor.build_recommendation(
        temperature=row["temperature"], dissolved_oxygen=row["dissolved_oxygen"],
        ph=row["ph"], turbidity=row["turbidity"], ammonia=row["ammonia"],
        nitrate=row["nitrate"], fish_weight_g=row["fish_weight_g"],
        population=population, base_feed_kg=base_feed_kg,
        ml_prediction_g=ml_pred,
    )
    result.pop("color", None)
    return jsonify(result)
