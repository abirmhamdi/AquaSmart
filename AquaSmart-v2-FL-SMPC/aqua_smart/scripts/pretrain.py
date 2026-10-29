"""
Pre-train the demo ML model (Ridge regression, saved with pickle).
Run once before starting the server:  python scripts/pretrain.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import MODELS_DIR
from app.services.ml_service import _build_demo_model

pkl = MODELS_DIR / "demo_model.pkl"

# Always regenerate if it's the old joblib/GBM format
needs_rebuild = True
if pkl.exists():
    try:
        import pickle
        with open(pkl,"rb") as f:
            data = pickle.load(f)
        # New format is a dict with 'model' and 'scaler' keys
        if isinstance(data, dict) and "model" in data and "scaler" in data:
            from sklearn.linear_model import Ridge
            if isinstance(data["model"], Ridge):
                needs_rebuild = False
                print("Demo model already exists (Ridge, pickle format) — skipping.")
                print(f"Found: {pkl}")
    except Exception:
        needs_rebuild = True

if needs_rebuild:
    print("Training demo model (Ridge regression)…")
    _build_demo_model()
    print(f"Saved to: {pkl}")

print("Pre-training complete. You can now run: python run.py")
