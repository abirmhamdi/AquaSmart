# 🐟 AquaSmart — Intelligent Fish Feeding System

A full-stack web application for intelligent fish feeding using ML and IoT sensor data.

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the app

```bash
python run.py
```

Open **http://localhost:8000** in your browser.

The app will automatically train a demo ML model on first launch if no production model is found.

---

## Train on Your Own Data

To use the actual IoT pond dataset for production accuracy:

```bash
# From a zip file
python scripts/train_model.py --data "tarung aqua data.zip"

# From a folder of CSV files
python scripts/train_model.py --data path/to/csv_folder/
```

Then restart `run.py` — the app will load the new model automatically.

---

## Features

| Page | Description |
|------|-------------|
| **Dashboard** | Live water quality metrics, WQI gauge, alerts, feeding strategy |
| **Ponds Monitor** | Multi-pond overview with per-pond status |
| **Predict & Recommend** | Enter parameters → ML model gives feeding recommendation |
| **Analytics** | 48h trend charts for all parameters + model info |
| **AquaBot Chat** | Domain-expert chatbot (no API key — rule-based NLP) |
| **About** | Project info, strategies, tech stack |

## Feeding Strategies

| Strategy | Condition | Feed Multiplier |
|----------|-----------|-----------------|
| ⛔ STOP     | Critical (temp <12°C or >35°C, DO <3 mg/L, ammonia >0.06) | ×0.0 |
| ⚠️ REDUCE   | Suboptimal parameters | ×0.55 |
| ✅ NORMAL   | Acceptable conditions | ×1.0 |
| 🆙 INCREASE | Excellent conditions | ×1.10 |

## Project Info

- **School:** SESAME — École Supérieure Privée des Sciences Appliquées et de Management
- **Supervisor:** Louay Tanazefti
