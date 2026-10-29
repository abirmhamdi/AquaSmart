# Secure feeding-ration prediction in smart aquaculture

Internship project (SESAME, ING4 S2, supervisor Louay
Tanazefti) implementing `sujet_stage_ete_ml_fl_smpc_aquaculture.pdf`: study,
compare and visualise Centralized ML, Local ML, Federated Learning and
FL+SMPC for predicting fish feed rations from IoT water-quality sensors.

## Project layout

```
dataset/                       11 real IoT-pond CSVs (one pond = one farm/client)
pdl-combined-version.ipynb     EDA, cleaning, feature engineering, model zoo (notebook)
aqua_smart/                    Flask web app -- live dashboard, predictions, chatbot
fl_smpc/                       Centralized / Local / FL / FL+SMPC comparison (see fl_smpc/README.md)
dashboard/app.py               Streamlit dashboard for the fl_smpc comparison (subject 4.6)
```

## Quick start

```bash
# Flask demo app (dashboard, predictions, ponds monitor, chatbot)
# -- ml_models/best_model.pkl is a real XGBoost model trained on the actual
#    dataset (fl_smpc/train_production_model.py), and its Federated Learning
#    demo trains on the real 11 ponds too.
cd aqua_smart && pip install -r requirements.txt && python run.py

# ML / FL / FL+SMPC comparison + its Streamlit dashboard
pip install -r fl_smpc/requirements.txt
python -m fl_smpc.experiments.ml_models          # Linear/Ridge/RF/XGBoost leaderboard
python -m fl_smpc.run_experiments                # Centralized vs Local vs FL vs FL+SMPC
python -m fl_smpc.train_production_model         # (re)trains aqua_smart's real model
streamlit run dashboard/app.py
```

## Subject coverage

| Subject requirement | Where |
|---|---|
| 4.1 Etude bibliographique | `report/bibliographic_study.md` |
| 4.2 Preparation des donnees (incl. growth stage / age proxy) | `pdl-combined-version.ipynb`, `fl_smpc/data.py` |
| 4.3 Modeles ML (Linear/Ridge/RF/XGBoost, MAE/RMSE/R2) | `pdl-combined-version.ipynb`, `fl_smpc/experiments/ml_models.py` |
| 4.4 Apprentissage federe (FedAvg, plusieurs clients) | `fl_smpc/experiments/federated.py`; `aqua_smart/app/services/federated.py` now also trains on the real 11 ponds (was synthetic) |
| 4.5 Agregation securisee SMPC | `fl_smpc/experiments/smpc.py` |
| 4.6 Tableau de bord (Streamlit) | `dashboard/app.py` -- 3 sections: Dataset Overview, ML Model Leaderboard (incl. predictions viz), Approach Comparison (Centralized vs Local vs FL vs FL+SMPC) |
| 7 Tableau comparatif des approches | `fl_smpc/results/comparison_results.json`, dashboard page "Centralized vs Local vs FL vs FL+SMPC" |
| 10 Rapport final + presentation | `report/bibliographic_study.md` written; full report + slides not attempted here |

See `fl_smpc/README.md` for the detailed methodology, in particular how the
`feed_ration_g` target was derived (the real dataset has no feed-amount
column) and how the SMPC layer works.
