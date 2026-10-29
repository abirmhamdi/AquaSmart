from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "ml_models"
DATA_DIR = BASE_DIR / "data"
FRONTEND_DIR = BASE_DIR / "frontend"

MODELS_DIR.mkdir(exist_ok=True)

# Optimal water parameter ranges for tilapia/common pond fish
PARAM_RANGES = {
    "temperature": {"min": 20, "max": 28, "crit_lo": 12, "crit_hi": 35, "unit": "°C", "ideal": (22, 26)},
    "dissolved_oxygen": {"min": 5.0, "max": 9.0, "crit_lo": 3.0, "crit_hi": 12.0, "unit": "mg/L", "ideal": (6, 8)},
    "ph": {"min": 6.5, "max": 8.5, "crit_lo": 5.5, "crit_hi": 9.5, "unit": "", "ideal": (7.0, 8.0)},
    "turbidity": {"min": 0, "max": 30, "crit_lo": 0, "crit_hi": 60, "unit": "NTU", "ideal": (5, 20)},
    "ammonia": {"min": 0, "max": 0.02, "crit_lo": 0, "crit_hi": 0.1, "unit": "mg/L", "ideal": (0, 0.01)},
    "nitrate": {"min": 0, "max": 10, "crit_lo": 0, "crit_hi": 30, "unit": "mg/L", "ideal": (0, 5)},
}

APP_VERSION = "1.0.0"
APP_NAME = "AquaSmart - Intelligent Fish Feeding System"
