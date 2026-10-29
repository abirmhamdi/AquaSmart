"""
Approach 3/4 -- Federated Learning (FedAvg).
Each pond trains locally, only the model UPDATE (weights) is sent to the
server, which aggregates by a sample-weighted average:
    w_global = sum_k (n_k / N) * w_k
Real data never leaves the client -- this replaces the synthetic-data FL
demo in aqua_smart/app/services/federated.py with one trained on the
actual 11-pond dataset.
Confidentiality: MEDIUM -- raw data stays local, but the raw parameter
updates themselves are visible to the server and could in principle leak
information about a client's local data distribution.
"""
from __future__ import annotations

import time
import numpy as np
from sklearn.preprocessing import RobustScaler

from fl_smpc.data import FEATURE_COLS, TARGET_COL
from fl_smpc.common import gd_update, evaluate, get_params, split_params, make_global_test_set, N_FEATURES, PARAM_BYTES


def _split_train_test(clients, scaler, test_frac, seed):
    rng = np.random.default_rng(seed)
    out = {}
    for name, df in clients.items():
        X = scaler.transform(df[FEATURE_COLS].values)
        y = df[TARGET_COL].values
        idx = rng.permutation(len(df))
        n_test = max(1, int(len(df) * test_frac))
        out[name] = (X[idx[n_test:]], y[idx[n_test:]])
    return out


def run(clients: dict, n_rounds: int = 15, test_frac: float = 0.2, seed: int = 42,
        aggregator=None) -> dict:
    """`aggregator(updates: list[(params, n_samples, client_name)]) -> np.ndarray`
    lets fl_smpc/experiments/smpc.py reuse this exact training loop and only
    swap out HOW updates get combined -- so FL and FL+SMPC differ in
    exactly one place, the aggregation step."""
    t0 = time.time()

    import pandas as pd
    pooled = pd.concat(clients.values(), ignore_index=True)
    scaler = RobustScaler().fit(pooled[FEATURE_COLS].values)
    X_test, y_test = make_global_test_set(clients, scaler, test_frac, seed)
    train_sets = _split_train_test(clients, scaler, test_frac, seed)

    rng = np.random.default_rng(seed)
    global_w, global_b = np.zeros(N_FEATURES), 0.0
    history = []
    n_messages = 0
    comm_bytes = 0

    if aggregator is None:
        def aggregator(updates):
            total = sum(n for _, n, _ in updates)
            w_sum = sum((n / total) * p for p, n, _ in updates)
            return w_sum

    for rnd in range(1, n_rounds + 1):
        updates = []
        for name, (X, y) in train_sets.items():
            w, b = gd_update(X, y, global_w.copy(), global_b, epochs=5, rng=rng)
            updates.append((get_params(w, b), len(X), name))
            n_messages += 1               # client -> server upload
            comm_bytes += PARAM_BYTES

        new_params = aggregator(updates)
        global_w, global_b = split_params(new_params)
        n_messages += len(train_sets)     # server -> clients broadcast of new global model
        comm_bytes += len(train_sets) * PARAM_BYTES

        m = evaluate(X_test, y_test, global_w, global_b)
        history.append({"round": rnd, **m})

    elapsed = time.time() - t0

    return {
        "approach": "Federated Learning (FedAvg)",
        "confidentiality": "Medium",
        "confidentiality_note": "Raw data stays local; only model parameter updates are exchanged.",
        "metrics": history[-1] and {k: history[-1][k] for k in ("mae", "rmse", "r2")},
        "history": history,
        "time_sec": elapsed,
        "n_messages": n_messages,
        "comm_bytes": comm_bytes,
        "n_rounds": n_rounds,
        "n_clients": len(clients),
        "n_test_rows": len(y_test),
    }
