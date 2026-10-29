"""
Data layer for the ML / Federated Learning / FL+SMPC comparison.

Loads the 11 real IoT pond CSVs (dataset/), normalises their inconsistent
column names, engineers the same feature set already used by the aqua_smart
app (thermal stress, DO deficit, WQI, ...), and derives a feed-ration
regression target.

IMPORTANT — methodological note (documented, not hidden):
The raw IoT-pond dataset (a public aquaculture sensor dataset) records water
quality + fish morphometrics but does NOT contain an actual "feed amount fed"
column. The internship subject explicitly allows generating the dataset
("Construire, nettoyer ou generer un dataset...", section 4.2), so the
target used here — `feed_ration_g` — is derived deterministically from each
row's real sensor readings via the same domain-expert feeding formula
already implemented in aqua_smart/app/services/advisor.py and
ml_service.py (temperature / dissolved-oxygen / pH multipliers applied to
fish weight), plus a small noise term to emulate real-world label
imprecision. This keeps the label definition consistent across the whole
project (notebook demo model, Flask app demo model, and this FL/SMPC
pipeline all agree on what "feed ration" means), while being transparent
that it is a simulated/proxy label rather than a metered ground truth.
"""
from __future__ import annotations

import glob
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(os.path.dirname(HERE), "dataset")

FEATURE_COLS = [
    "temperature", "dissolved_oxygen", "ph", "turbidity", "ammonia", "nitrate",
    "fish_weight_g", "thermal_stress", "do_deficit", "do_ok", "ph_deviation",
    "ph_acidic", "ph_alkaline", "turbidity_high", "ammonia_toxic",
    "water_quality_index", "env_stress_index", "temp_x_do", "ph_x_do",
    "turb_x_temp", "temp_sq", "growth_stage",
]
TARGET_COL = "feed_ration_g"

# ── Column name normalisation (schema differs across the 11 files) ─────────
_COL_ALIASES = {
    "temperature":      ["temperature", "temp"],
    "turbidity":        ["turbidity", "turb"],
    "dissolved_oxygen": ["dissolved oxygen", "disolved oxygen", "dissolvedoxygen"],
    "ph":               ["ph"],
    "ammonia":          ["ammonia"],
    "nitrate":          ["nitrate"],
    "population":       ["population"],
    "fish_length":      ["length"],
    "fish_weight_g":    ["weight"],
}


def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename = {}
    for col in df.columns:
        key = col.strip().lower()
        for canon, aliases in _COL_ALIASES.items():
            if any(a in key for a in aliases):
                rename[col] = canon
                break
    df = df.rename(columns=rename)
    keep = [c for c in _COL_ALIASES if c in df.columns]
    return df[keep].copy()


def _engineer(df: pd.DataFrame) -> pd.DataFrame:
    """Same engineered features as aqua_smart/app/services/ml_service.py::_engineer,
    vectorised over a DataFrame instead of a single row."""
    t, do, ph = df["temperature"], df["dissolved_oxygen"], df["ph"]
    tu, am = df["turbidity"], df["ammonia"]
    ni = df.get("nitrate", pd.Series(2.0, index=df.index))
    fw = df.get("fish_weight_g", pd.Series(50.0, index=df.index))

    out = pd.DataFrame(index=df.index)
    out["temperature"] = t
    out["dissolved_oxygen"] = do
    out["ph"] = ph
    out["turbidity"] = tu
    out["ammonia"] = am
    out["nitrate"] = ni
    out["fish_weight_g"] = fw
    out["thermal_stress"] = np.maximum(0, 20 - t) + np.maximum(0, t - 28)
    out["do_deficit"] = (6.0 - do).clip(lower=0)
    out["do_ok"] = (do >= 5.0).astype(int)
    out["ph_deviation"] = (ph - 7.0).abs()
    out["ph_acidic"] = (ph < 6.5).astype(int)
    out["ph_alkaline"] = (ph > 8.5).astype(int)
    out["turbidity_high"] = (tu > 30).astype(int)
    out["ammonia_toxic"] = (am > 0.02).astype(int)
    out["water_quality_index"] = (
        100 * (1 - (out["thermal_stress"] / 10).clip(0, 1))
        + do.clip(0, 8) / 8 * 100
        + 100 - (out["ph_deviation"] / 3).clip(0, 1) * 100
    ) / 3
    out["env_stress_index"] = (
        out["thermal_stress"] + out["do_deficit"] + out["ph_deviation"]
        + out["turbidity_high"] + out["ammonia_toxic"]
    )
    out["temp_x_do"] = t * do
    out["ph_x_do"] = ph * do
    out["turb_x_temp"] = tu * t
    out["temp_sq"] = t ** 2
    # Growth stage / "age" proxy required by the subject (section 4.2:
    # "age ou stade de croissance"). The dataset has no fish age, so the
    # stage is derived from fish weight using standard aquaculture growth
    # bands (ordinal: 0=fry, 1=fingerling, 2=juvenile, 3=grower, 4=adult).
    out["growth_stage"] = np.select(
        [fw < 5, fw < 50, fw < 150, fw < 400],
        [0, 1, 2, 3],
        default=4,
    ).astype(np.float32)
    return out


def _derive_feed_target(feat: pd.DataFrame, rng: np.random.Generator) -> np.ndarray:
    """Domain-expert feeding formula (same shape as advisor.py / ml_service.py),
    applied to REAL sensor rows to produce a proxy regression target."""
    t, do, ph, fw = feat["temperature"], feat["dissolved_oxygen"], feat["ph"], feat["fish_weight_g"]
    base = fw * 0.03
    tf = np.where((t >= 22) & (t <= 26), 1.1, np.where(t < 18, 0.4, 0.8))
    dof = np.where(do >= 7, 1.05, np.where(do >= 3, 0.5, 0.0))
    pf = np.where((ph >= 6.8) & (ph <= 8.2), 1.0, np.where(ph < 6.5, 0.4, 0.6))
    noise = rng.normal(0, 0.05 * (base.abs() + 1e-6))
    return np.clip(base * tf * dof * pf + noise, 0, None).astype(np.float32)


def load_pond(path: str, sample_cap: int = 8000, seed: int = 0) -> pd.DataFrame:
    """Load, clean, feature-engineer and label one pond CSV.
    Downsampled to `sample_cap` rows (ponds are logged every ~1 min so
    consecutive rows are highly autocorrelated -- a random subsample keeps
    training tractable without materially changing the signal)."""
    raw = pd.read_csv(path, low_memory=False)
    df = _normalise_columns(raw)
    for c in ["temperature", "dissolved_oxygen", "ph", "turbidity", "ammonia", "nitrate", "fish_weight_g"]:
        if c not in df.columns:
            df[c] = np.nan
    num_cols = ["temperature", "dissolved_oxygen", "ph", "turbidity", "ammonia", "nitrate", "fish_weight_g"]
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce")
    df[num_cols] = df[num_cols].replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=["temperature", "dissolved_oxygen", "ph", "turbidity", "ammonia", "fish_weight_g"])
    df = df[(df["fish_weight_g"] > 0) & (df["fish_weight_g"] < 2000)]
    df = df[(df["temperature"].between(5, 40)) & (df["ph"].between(3, 11))]
    # A handful of sensor rows carry corrupted/sentinel readings (e.g. ammonia
    # in the thousands) -- clip to plausible aquaculture ranges rather than
    # dropping, since the rest of that row is usually still valid.
    df["ammonia"] = df["ammonia"].clip(0, 5)
    df["nitrate"] = df["nitrate"].clip(0, 100)
    df["turbidity"] = df["turbidity"].clip(0, 500)

    if len(df) == 0:
        return pd.DataFrame(columns=FEATURE_COLS + [TARGET_COL])

    if len(df) > sample_cap:
        df = df.sample(n=sample_cap, random_state=seed)

    feat = _engineer(df)
    rng = np.random.default_rng(seed)
    feat[TARGET_COL] = _derive_feed_target(feat, rng)
    return feat.reset_index(drop=True)


def load_all_clients(sample_cap: int = 8000) -> dict[str, pd.DataFrame]:
    """One entry per pond CSV = one FL client / farm, as required by the
    subject ("simuler plusieurs bassins ou fermes comme clients independants")."""
    clients = {}
    for i, path in enumerate(sorted(glob.glob(os.path.join(DATASET_DIR, "*.csv")))):
        name = os.path.splitext(os.path.basename(path))[0]
        df = load_pond(path, sample_cap=sample_cap, seed=i)
        if len(df) >= 50:
            clients[name] = df
    return clients


if __name__ == "__main__":
    clients = load_all_clients()
    for name, df in clients.items():
        print(f"{name:<14} rows={len(df):>6}  feed_ration_g mean={df[TARGET_COL].mean():.3f}")
    total = sum(len(d) for d in clients.values())
    print(f"\n{len(clients)} clients, {total} total rows")
