"""
Subject section 4.3 -- "Comparer au minimum : Linear Regression, Ridge
Regression, Random Forest et XGBoost ou Gradient Boosting. Evaluer les
modeles avec MAE, RMSE et R2."

Note: the original pdl-combined-version.ipynb notebook's auto target-picker
ended up selecting `wqi_category` as TARGET (see cell 20's printed output:
`Target: "wqi_category"`) because it matched a TGT_KW keyword before any
feed/weight column was checked. wqi_category is itself arithmetically
derived from thermal_stress / DO / pH -- features that stayed in the
training matrix -- so that leaderboard was effectively scoring how well a
model can reconstruct a value from (most of) its own inputs. This script
reruns the same style of comparison against the fl_smpc.data target
(`feed_ration_g`, derived independently from the domain feeding formula,
see fl_smpc/data.py) so the leaderboard numbers are meaningful.
"""
from __future__ import annotations

import json
import os
import time

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from fl_smpc.data import load_all_clients, FEATURE_COLS, TARGET_COL

RESULTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "results", "ml_comparison.json")

try:
    import xgboost as xgb
    XGB_OK = True
except ImportError:
    XGB_OK = False


def run(sample_cap: int = 5000, seed: int = 42) -> dict:
    clients = load_all_clients(sample_cap=sample_cap)
    pooled = pd.concat(clients.values(), ignore_index=True)

    X = pooled[FEATURE_COLS].values
    y = pooled[TARGET_COL].values
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=seed)

    scaler = RobustScaler().fit(X_tr)
    X_tr_s, X_te_s = scaler.transform(X_tr), scaler.transform(X_te)

    models = {
        "Linear Regression": LinearRegression(),
        "Ridge Regression": Ridge(alpha=1.0),
        "Random Forest": RandomForestRegressor(n_estimators=200, max_depth=12, random_state=seed, n_jobs=-1),
        ("XGBoost" if XGB_OK else "Gradient Boosting"): (
            xgb.XGBRegressor(n_estimators=300, max_depth=5, learning_rate=0.08,
                              random_state=seed, verbosity=0)
            if XGB_OK else
            GradientBoostingRegressor(n_estimators=200, max_depth=4, learning_rate=0.08, random_state=seed)
        ),
    }

    results = []
    pred_samples = {}
    rng = np.random.default_rng(seed)
    for name, model in models.items():
        t0 = time.time()
        model.fit(X_tr_s, y_tr)
        pred = model.predict(X_te_s)
        results.append({
            "model": name,
            "mae": float(mean_absolute_error(y_te, pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_te, pred))),
            "r2": float(r2_score(y_te, pred)),
            "train_time_sec": time.time() - t0,
        })
        # Small subsample of (true, predicted) pairs per model, for the
        # dashboard's "visualise predictions" requirement (subject 4.6) --
        # keeps ml_comparison.json small instead of dumping the full test set.
        idx = rng.choice(len(y_te), size=min(300, len(y_te)), replace=False)
        pred_samples[name] = {"y_true": y_te[idx].tolist(), "y_pred": pred[idx].tolist()}

    results.sort(key=lambda r: r["rmse"])
    out = {"target": TARGET_COL, "n_train": len(y_tr), "n_test": len(y_te),
           "leaderboard": results, "prediction_samples": pred_samples}

    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(out, f, indent=2)
    return out


if __name__ == "__main__":
    out = run()
    print(f"Target: {out['target']}  (train={out['n_train']}, test={out['n_test']})\n")
    for r in out["leaderboard"]:
        print(f"  {r['model']:<20} MAE={r['mae']:.4f}  RMSE={r['rmse']:.4f}  R2={r['r2']:.4f}  "
              f"({r['train_time_sec']:.2f}s)")
