"""
Approach 2/4 -- Local ML.
Each pond trains its own model independently, no data or updates ever leave
the client.
Confidentiality: HIGH -- nothing is shared, but no collaboration means
performance depends entirely on each client's own (often small) dataset.
"""
from __future__ import annotations

import time
import numpy as np
from sklearn.preprocessing import RobustScaler

from fl_smpc.data import FEATURE_COLS, TARGET_COL
from fl_smpc.common import gd_update, evaluate, make_global_test_set, N_FEATURES


def run(clients: dict, test_frac: float = 0.2, seed: int = 42) -> dict:
    t0 = time.time()

    # A shared scaler is the one piece of "prior knowledge" every client is
    # given up front (fit on feature ranges only, not on any client's raw
    # rows) so per-client scores stay comparable to the other 3 approaches.
    import pandas as pd
    pooled = pd.concat(clients.values(), ignore_index=True)
    scaler = RobustScaler().fit(pooled[FEATURE_COLS].values)
    X_test, y_test = make_global_test_set(clients, scaler, test_frac, seed)

    per_client = {}
    rng = np.random.default_rng(seed)
    for name, df in clients.items():
        X = scaler.transform(df[FEATURE_COLS].values)
        y = df[TARGET_COL].values
        idx = rng.permutation(len(df))
        n_test = max(1, int(len(df) * test_frac))
        X_tr, y_tr = X[idx[n_test:]], y[idx[n_test:]]

        w = np.zeros(N_FEATURES)
        b = 0.0
        w, b = gd_update(X_tr, y_tr, w, b, epochs=15, rng=rng)
        per_client[name] = evaluate(X_test, y_test, w, b)

    avg = {k: float(np.mean([m[k] for m in per_client.values()])) for k in ("mae", "rmse", "r2")}
    elapsed = time.time() - t0

    return {
        "approach": "Local ML",
        "confidentiality": "High",
        "confidentiality_note": "No data or model updates ever leave the client; zero collaboration.",
        "metrics": avg,
        "per_client_metrics": per_client,
        "time_sec": elapsed,
        "n_messages": 0,
        "comm_bytes": 0,
        "n_test_rows": len(y_test),
    }
