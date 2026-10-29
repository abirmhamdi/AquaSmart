"""
Replaces aqua_smart's placeholder demo model (Ridge trained on synthetic
data, auto-generated on first launch by ml_service.py) with a real model
trained on the real 11-pond dataset, using the same feature/target
definitions as the rest of fl_smpc/.

Picks the best-performing model type found by fl_smpc/experiments/ml_models.py
(XGBoost or Random Forest, whichever wins on RMSE) and saves it to
aqua_smart/ml_models/best_model.pkl + meta.json in exactly the format
app/services/ml_service.py already knows how to load -- no app code changes
needed, the Flask app just needs a restart to pick it up.

Usage:
    python -m fl_smpc.train_production_model
"""
from __future__ import annotations

import json
import os
import pickle
import time

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import pandas as pd

from fl_smpc.data import load_all_clients, FEATURE_COLS, TARGET_COL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(ROOT, "aqua_smart", "ml_models")

try:
    import xgboost as xgb
    XGB_OK = True
except ImportError:
    XGB_OK = False


def main(sample_cap: int = 20000, seed: int = 42):
    print(f"Loading real dataset (cap={sample_cap} rows/pond) ...")
    clients = load_all_clients(sample_cap=sample_cap)
    pooled = pd.concat(clients.values(), ignore_index=True)
    print(f"  {len(clients)} ponds, {len(pooled):,} rows total")

    X = pooled[FEATURE_COLS].values
    y = pooled[TARGET_COL].values
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.15, random_state=seed)

    scaler = RobustScaler().fit(X_tr)
    X_tr_s, X_te_s = scaler.transform(X_tr), scaler.transform(X_te)

    if XGB_OK:
        model = xgb.XGBRegressor(n_estimators=300, max_depth=5, learning_rate=0.08,
                                  random_state=seed, verbosity=0)
        model_name = "XGBoost"
    else:
        model = RandomForestRegressor(n_estimators=250, max_depth=12, random_state=seed, n_jobs=-1)
        model_name = "Random Forest"

    print(f"Training {model_name} on {len(X_tr):,} rows ...")
    t0 = time.time()
    model.fit(X_tr_s, y_tr)
    train_time = time.time() - t0

    pred = model.predict(X_te_s)
    metrics = {
        "mae": float(mean_absolute_error(y_te, pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_te, pred))),
        "r2": float(r2_score(y_te, pred)),
    }
    print(f"  test MAE={metrics['mae']:.4f}  RMSE={metrics['rmse']:.4f}  R2={metrics['r2']:.4f}  "
          f"({train_time:.1f}s)")

    os.makedirs(MODELS_DIR, exist_ok=True)
    with open(os.path.join(MODELS_DIR, "best_model.pkl"), "wb") as f:
        pickle.dump({"model": model, "scaler": scaler}, f, protocol=4)

    meta = {
        "model": model_name,
        "task": "regression",
        "target": TARGET_COL,
        "features": FEATURE_COLS,
        "training_samples": len(X_tr),
        "test_samples": len(X_te),
        "test_metrics": metrics,
        "source": "real 11-pond dataset via fl_smpc.data (previously: synthetic demo model)",
        "note": "Trained by fl_smpc/train_production_model.py",
    }
    with open(os.path.join(MODELS_DIR, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(f"Saved -> {MODELS_DIR}/best_model.pkl + meta.json")
    print("Restart the Flask app (python run.py) to pick up the real model.")


if __name__ == "__main__":
    main()
