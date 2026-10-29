"""
Approach 1/4 -- Centralized ML.
All pond data is pooled on a single server before training.
Confidentiality: LOW -- every client's raw sensor rows are transferred and
visible to the central server.
"""
from __future__ import annotations

import time
import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler

from fl_smpc.data import FEATURE_COLS, TARGET_COL
from fl_smpc.common import gd_update, evaluate, make_global_test_set, N_FEATURES


def run(clients: dict, test_frac: float = 0.2, seed: int = 42) -> dict:
    t0 = time.time()

    pooled = pd.concat(clients.values(), ignore_index=True)
    scaler = RobustScaler().fit(pooled[FEATURE_COLS].values)

    X_test, y_test = make_global_test_set(clients, scaler, test_frac, seed)

    rng = np.random.default_rng(seed)
    train_idx = rng.permutation(len(pooled))
    n_test_pooled = int(len(pooled) * test_frac)
    train_rows = pooled.iloc[train_idx[n_test_pooled:]]

    X_train = scaler.transform(train_rows[FEATURE_COLS].values)
    y_train = train_rows[TARGET_COL].values

    w = np.zeros(N_FEATURES)
    b = 0.0
    w, b = gd_update(X_train, y_train, w, b, epochs=15, rng=rng)

    metrics = evaluate(X_test, y_test, w, b)
    elapsed = time.time() - t0

    # Communication cost: the ENTIRE raw dataset must be uploaded to the
    # server once (this is precisely the privacy weakness this approach has).
    raw_bytes = int(pooled[FEATURE_COLS + [TARGET_COL]].memory_usage(deep=False).sum())

    return {
        "approach": "Centralized ML",
        "confidentiality": "Low",
        "confidentiality_note": "All raw client data is transferred to and visible on the central server.",
        "metrics": metrics,
        "time_sec": elapsed,
        "n_messages": len(clients),  # one raw-data upload per client
        "comm_bytes": raw_bytes,
        "n_train_rows": len(train_rows),
        "n_test_rows": len(y_test),
    }
