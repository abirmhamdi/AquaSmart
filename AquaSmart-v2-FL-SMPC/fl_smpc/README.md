# fl_smpc -- ML / FL / FL+SMPC comparison

Implements the part of `sujet_stage_ete_ml_fl_smpc_aquaculture.pdf` that the
rest of the project (`pdl-combined-version.ipynb`, `aqua_smart/`) did not
cover: a real, reproducible comparison of **Centralized ML vs Local ML vs
Federated Learning vs FL+SMPC**, plus the Streamlit dashboard the subject
recommends (section 4.6).

## Why a new package instead of editing the notebook

The FL/SMPC simulation needs to instantiate several independent "clients"
and run repeated training/aggregation rounds -- that's much easier to get
right, test and reuse as plain Python modules than as notebook cells. The
notebook remains the place for one-off EDA/plots; this package is the
reproducible experiment code the subject asks for ("Notebooks
d'experimentation ou scripts reproductibles", section 7/10).

## What's new vs. the original project

| Gap identified in the original project | Fix in `fl_smpc/` |
|---|---|
| FL simulation (`aqua_smart/app/services/federated.py`) trained on **synthetic** per-pond data | `fl_smpc/data.py` splits the real 11-pond dataset into 11 real clients |
| No SMPC / secure aggregation anywhere in the project | `fl_smpc/experiments/smpc.py` -- pairwise additive masking |
| No Centralized vs Local vs FL vs FL+SMPC comparison | `fl_smpc/run_experiments.py` runs all 4, `fl_smpc/results/comparison_results.json` |
| Notebook's model leaderboard accidentally trained on `wqi_category`, a value computed from its own input features (see comment in `ml_models.py`) | `fl_smpc/experiments/ml_models.py` reruns Linear/Ridge/RF/XGBoost against the real `feed_ration_g` target |
| No Streamlit dashboard (subject recommends it) | `dashboard/app.py` |

## The dataset has no feed-amount label -- how the target was built

The raw IoT-pond CSVs record water quality + fish morphometrics, not actual
feed given. The subject explicitly allows generating the dataset ("Construire,
nettoyer ou generer un dataset...", section 4.2), so `feed_ration_g` is
computed deterministically from each row's **real** sensor readings using the
same domain feeding formula already implemented in
`aqua_smart/app/services/advisor.py` / `ml_service.py`
(temperature/DO/pH multipliers applied to fish weight, + small noise). This
keeps the label definition consistent everywhere in the project. It's a
proxy/simulated label, not a metered ground truth -- say so explicitly in the
report.

## Dashboard pages (`dashboard/app.py`)

Trimmed to 3 focused sections (collapsible left sidebar navigation under a centered title bar) (the Flask app already covers live prediction and
an About page isn't part of the subject's required content):

- **Dataset Overview** -- per-pond row counts, target distribution, sensor
  boxplots, correlation matrix.
- **ML Model Leaderboard** -- Linear/Ridge/RF/XGBoost comparison as a single
  annotated grouped bar chart (MAE/RMSE/R2), plus a predicted-vs-actual
  scatter plot per model (subject's "visualiser les predictions" requirement).
- **Approach Comparison** (Centralized vs Local vs FL vs FL+SMPC) -- the full comparison table,
  accuracy/communication/time/confidentiality bar charts, and the FL vs
  FL+SMPC convergence curves.

## Run it

```bash
pip install -r fl_smpc/requirements.txt

# 1. ML model comparison (subject 4.3)
python -m fl_smpc.experiments.ml_models

# 2. Centralized / Local / FL / FL+SMPC comparison (subject 4.4-4.8)
python -m fl_smpc.run_experiments --sample-cap 5000 --rounds 15

# 3. Dashboard (subject 4.6)
streamlit run dashboard/app.py
```

## How SMPC is implemented

Pairwise additive masking (a simplified secure-aggregation / additive
secret-sharing scheme): for every pair of clients `(i, j)` in a round, both
sides derive the same random mask vector `m_ij`. Client `i`'s weighted
contribution gets `+ m_ij / n_i`, client `j`'s gets `- m_ij / n_j`. Every
individual masked update the server receives is statistically
indistinguishable from noise, but summed across all clients the masks cancel
**exactly**, so the server recovers the correct FedAvg global model without
ever seeing a real individual update. `fl_smpc/experiments/smpc.py` reuses
`federated.py`'s training loop unchanged and only swaps the aggregation
function, so any metric difference between FL and FL+SMPC in the results is
due to masking overhead alone -- confirmed by the results file, where the two
approaches' MAE/RMSE/R2 match to float precision.

## Still open (not built here)

- The full `rapport de stage` (beyond the bibliographic study) and the
  10-15 slide presentation (subject section 10) are writing deliverables --
  not attempted here.
- SMPC currently assumes no client drops out mid-round; production secure
  aggregation (e.g. Bonawitz et al.) adds dropout recovery via real secret
  sharing (Shamir), which this simplified version does not implement.

## Also wired into the Flask app (`aqua_smart/`)

- `aqua_smart/app/services/federated.py`'s live FL demo now trains on the
  real 11 ponds (via `fl_smpc.data`, cycling through them if more simulated
  clients than real ponds are requested) instead of synthetic data, with a
  synthetic fallback if `fl_smpc/`/`dataset/` aren't reachable. Fixing this
  also surfaced and fixed a real bug: each client used to fit its OWN
  `RobustScaler`, which is incoherent with FedAvg (averaging raw weights
  across clients only makes sense if every client's weights operate on the
  same feature scale) -- it went unnoticed on synthetic data because all
  clients had near-identical distributions, but diverged on the real ponds'
  more varied sensor ranges. Now one shared scaler is fit once and passed to
  every client, plus gradient-norm clipping for small clients.
- `aqua_smart/ml_models/best_model.pkl` is now a real XGBoost model trained
  on the real dataset (`fl_smpc/train_production_model.py`), replacing the
  synthetic-data demo Ridge model `ml_service.py` used to auto-generate on
  first launch. Test R2 = 0.985.
