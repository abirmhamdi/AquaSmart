"""
ML model - uses Ridge regression + pickle (no Cython, no mmap, no joblib).
All numpy/sklearn imports are lazy so this module can be imported without
touching numpy before the server starts.
"""
import json, pickle, logging
from app.config import MODELS_DIR

logger  = logging.getLogger(__name__)
_model  = None
_scaler = None
_model_meta: dict = {}

FEATURES = [
    "temperature","dissolved_oxygen","ph","turbidity","ammonia","nitrate",
    "fish_weight_g","thermal_stress","do_deficit","do_ok","ph_deviation",
    "ph_acidic","ph_alkaline","turbidity_high","ammonia_toxic",
    "water_quality_index","env_stress_index","temp_x_do","ph_x_do",
    "turb_x_temp","temp_sq","growth_stage",
]


def _growth_stage(fw: float) -> int:
    """Growth-stage / "age" proxy required by the subject (4.2: "age ou
    stade de croissance"). No age field exists in the raw sensor data, so
    the stage is derived from fish weight via standard aquaculture growth
    bands -- kept identical to fl_smpc/data.py::_engineer for consistency."""
    if fw < 5:   return 0   # fry
    if fw < 50:  return 1   # fingerling
    if fw < 150: return 2   # juvenile
    if fw < 400: return 3   # grower
    return 4                # adult / market size


def _engineer(row: dict):
    import numpy as np
    t = row["temperature"];    do  = row["dissolved_oxygen"]
    ph = row["ph"];            tu  = row["turbidity"]
    am = row["ammonia"];       ni  = row.get("nitrate", 2.0)
    fw = row.get("fish_weight_g", 50.0)

    ts  = max(0, 20-t) + max(0, t-28)
    dod = max(0, 6.0-do)
    dok = int(do >= 5.0)
    phd = abs(ph - 7.0)
    pha = int(ph < 6.5)
    phl = int(ph > 8.5)
    th  = int(tu > 30)
    at  = int(am > 0.02)
    wqi = (100*(1-min(ts/10,1)) + min(do,8)/8*100 + 100-min(phd/3,1)*100) / 3
    si  = ts + dod + phd + th + at
    gs  = _growth_stage(fw)

    return np.array([t,do,ph,tu,am,ni,fw,ts,dod,dok,phd,pha,phl,th,at,
                     wqi,si,t*do,ph*do,tu*t,t**2,gs], dtype=np.float32)


def _build_demo_model():
    """Train Ridge regression on synthetic data and save with pickle."""
    import numpy as np
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import RobustScaler

    logger.info("Training demo model …")
    rng = np.random.default_rng(42);  n = 5000
    temp = rng.uniform(18,32,n);  do  = rng.uniform(2,10,n)
    ph   = rng.uniform(5.5,9.5,n); tu = rng.uniform(0,60,n)
    am   = rng.uniform(0,.08,n);   ni = rng.uniform(0,15,n)
    fw   = rng.uniform(10,300,n)

    base = fw*0.03
    tf   = np.where((temp>=22)&(temp<=26),1.1,np.where(temp<18,0.4,0.8))
    df   = np.where(do>=7,1.05,np.where(do>=3,0.5,0.0))
    pf   = np.where((ph>=6.8)&(ph<=8.2),1.0,np.where(ph<6.5,0.4,0.6))
    feed = np.clip(base*tf*df*pf + rng.normal(0,.5,n), 0, 50)

    X = np.array([_engineer({"temperature":temp[i],"dissolved_oxygen":do[i],
                              "ph":ph[i],"turbidity":tu[i],"ammonia":am[i],
                              "nitrate":ni[i],"fish_weight_g":fw[i]}) for i in range(n)])
    scaler = RobustScaler()
    Xs     = scaler.fit_transform(X)
    model  = Ridge(alpha=1.0)
    model.fit(Xs, feed)

    with open(MODELS_DIR/"demo_model.pkl","wb") as f:
        pickle.dump({"model":model,"scaler":scaler}, f, protocol=4)

    meta = {"model":"Ridge (Demo)","task":"regression","features":FEATURES,
            "training_samples":n,"note":"Demo model - run scripts/train_model.py for production."}
    (MODELS_DIR/"meta.json").write_text(json.dumps(meta,indent=2))
    logger.info("Demo model saved.")
    return model, scaler, meta


def load_model():
    global _model, _scaler, _model_meta
    if _model is not None:
        return _model, _scaler, _model_meta

    pkl   = MODELS_DIR / "demo_model.pkl"
    meta_f= MODELS_DIR / "meta.json"

    # Legacy: production model saved by train_model.py uses separate files
    prod = MODELS_DIR / "best_model.pkl"
    if prod.exists():
        with open(prod,"rb") as f: data = pickle.load(f)
        if isinstance(data, dict):
            _model, _scaler = data["model"], data["scaler"]
        else:
            _model = data
            scl = MODELS_DIR / "scaler.pkl"
            _scaler = pickle.load(open(scl,"rb")) if scl.exists() else None
        _model_meta = json.loads(meta_f.read_text()) if meta_f.exists() else {}
        logger.info("Production model loaded.")
        return _model, _scaler, _model_meta

    if pkl.exists():
        logger.info("Loading demo model …")
        with open(pkl,"rb") as f: data = pickle.load(f)
        if isinstance(data, dict):
            _model, _scaler = data["model"], data["scaler"]
        else:          # legacy single-object pkl
            _model  = data
            _scaler = None
        _model_meta = json.loads(meta_f.read_text()) if meta_f.exists() else {}
        return _model, _scaler, _model_meta

    _model, _scaler, _model_meta = _build_demo_model()
    return _model, _scaler, _model_meta


def predict(row: dict):
    global _model, _scaler
    if _model is None:
        load_model()
    try:
        import numpy as np
        feat   = _engineer(row).reshape(1,-1)
        scaled = _scaler.transform(feat) if _scaler is not None else feat
        return max(0.0, float(_model.predict(scaled)[0]))
    except Exception as e:
        logger.error("Prediction error: %s", e)
        return None


def get_model_info() -> dict:
    return _model_meta
