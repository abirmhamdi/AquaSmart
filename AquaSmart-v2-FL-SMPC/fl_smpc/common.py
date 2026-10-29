"""
Shared model, metrics and cost-accounting utilities.

A single linear model family (Ridge regression, trained by gradient steps)
is used across all four approaches so the comparison is apples-to-apples --
FedAvg / secure aggregation only make sense to compare when every approach
aggregates the SAME kind of model parameters. This mirrors the design
already used in aqua_smart/app/services/federated.py.
"""
from __future__ import annotations

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import RobustScaler

from fl_smpc.data import FEATURE_COLS, TARGET_COL

ALPHA = 1.0
LR = 0.01
LOCAL_EPOCHS = 5
N_FEATURES = len(FEATURE_COLS)

PARAM_BYTES = (N_FEATURES + 1) * 8  # float64 weight vector + bias, per message


def get_params(w, b):
    return np.append(w, b)


def split_params(p):
    return p[:-1].copy(), float(p[-1])


def gd_update(X, y, w, b, epochs=LOCAL_EPOCHS, lr=LR, alpha=ALPHA, rng=None, clip=5.0):
    """Local SGD training step used identically by Local, FL and FL+SMPC
    (only what happens to the *result* differs between the three).
    Gradients are norm-clipped: small clients (as few as ~500 rows) can
    otherwise produce noisy batch gradients that diverge."""
    rng = rng or np.random.default_rng(0)
    n = X.shape[0]
    batch = max(32, n // 8)
    for _ in range(epochs):
        idx = rng.permutation(n)
        for start in range(0, n, batch):
            ib = idx[start:start + batch]
            Xb, yb = X[ib], y[ib]
            err = Xb @ w + b - yb
            gw = (2 / len(ib)) * (Xb.T @ err) + 2 * alpha * w
            gb = (2 / len(ib)) * err.sum()
            gnorm = np.sqrt(np.sum(gw ** 2) + gb ** 2)
            if gnorm > clip:
                scale = clip / (gnorm + 1e-12)
                gw, gb = gw * scale, gb * scale
            w = w - lr * gw
            b = b - lr * gb
    return w, b


def evaluate(X, y, w, b) -> dict:
    pred = X @ w + b
    return {
        "mae": float(mean_absolute_error(y, pred)),
        "rmse": float(np.sqrt(mean_squared_error(y, pred))),
        "r2": float(r2_score(y, pred)),
    }


def make_global_test_set(clients: dict, scaler: RobustScaler, test_frac: float = 0.2, seed: int = 42):
    """A held-out slice from EVERY client, scaled with the globally-fit
    scaler, so all four approaches are graded on the same yardstick."""
    rng = np.random.default_rng(seed)
    X_parts, y_parts = [], []
    for df in clients.values():
        n_test = max(1, int(len(df) * test_frac))
        idx = rng.permutation(len(df))[:n_test]
        X_parts.append(df[FEATURE_COLS].values[idx])
        y_parts.append(df[TARGET_COL].values[idx])
    X = np.vstack(X_parts)
    y = np.concatenate(y_parts)
    return scaler.transform(X), y
