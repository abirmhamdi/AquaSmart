"""
Train the AquaSmart ML model from your actual IoT pond CSV data.

Usage:
    python scripts/train_model.py --data path/to/data.zip
    python scripts/train_model.py --data path/to/csv_folder/

The script will:
  1. Load all CSV files from the given path (or zip)
  2. Apply the same feature engineering as the notebook
  3. Train a GradientBoosting model (or XGBoost if available)
  4. Save artefacts to ml_models/ for the web app to load
"""
import os, sys, glob, zipfile, json, pickle, warnings
import argparse
import numpy as np
import pandas as pd
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
warnings.filterwarnings('ignore')

MODELS_DIR = ROOT / "ml_models"
MODELS_DIR.mkdir(exist_ok=True)

# ─── Column name normalisation ───────────────────────────────
COL_MAP = {
    "temperature":       ["temperature", "temp", "TEMPERATURE"],
    "dissolved_oxygen":  ["dissolved oxygen", "dissolved_o2", "disolved oxygen", "do", "o2", "DISOLVED OXYGEN", "Dissolved Oxygen (g/ml)"],
    "ph":                ["ph", "pH", "PH"],
    "turbidity":         ["turbidity", "turb", "TURBIDITY"],
    "ammonia":           ["ammonia", "nh3", "AMMONIA"],
    "nitrate":           ["nitrate", "no3", "NITRATE"],
    "fish_weight":       ["weight", "fish_weight", "Weight", "Fish_weight(g)"],
    "population":        ["population", "Population"],
    "feed_amount":       ["feed_amount", "feed amount", "Food Amount (g)", "feeding_amount", "fish food amount (g)"],
}


def find_col(df, candidates):
    for c in candidates:
        for col in df.columns:
            if col.strip().lower() == c.lower() or c.lower() in col.strip().lower():
                return col
    return None


def load_csvs(source: str) -> pd.DataFrame:
    dfs = []
    if source.endswith('.zip'):
        with zipfile.ZipFile(source, 'r') as z:
            for name in z.namelist():
                if name.endswith('.csv'):
                    with z.open(name) as f:
                        try:
                            df = pd.read_csv(f, low_memory=False)
                            dfs.append(df)
                            print(f"  Loaded: {name}  {df.shape}")
                        except Exception as e:
                            print(f"  Skip {name}: {e}")
    else:
        for path in glob.glob(os.path.join(source, '**', '*.csv'), recursive=True):
            try:
                df = pd.read_csv(path, low_memory=False)
                dfs.append(df)
                print(f"  Loaded: {os.path.basename(path)}  {df.shape}")
            except Exception as e:
                print(f"  Skip {path}: {e}")

    if not dfs:
        raise ValueError("No CSV files found.")

    # concat files that share the same columns
    base = max(dfs, key=len)
    compatible = [d for d in dfs if set(d.columns) == set(base.columns)]
    result = pd.concat(compatible if len(compatible) > 1 else [base], ignore_index=True)
    print(f"\nTotal rows: {len(result):,}")
    return result


def preprocess(df: pd.DataFrame) -> tuple:
    # Normalise column names
    rename = {}
    for std_name, candidates in COL_MAP.items():
        col = find_col(df, candidates)
        if col:
            rename[col] = std_name

    df.rename(columns=rename, inplace=True)
    print("Mapped columns:", {v: k for k, v in rename.items()})

    # Parse datetime if present
    for col in df.columns:
        if any(k in col.lower() for k in ['time', 'date', 'created']):
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                if df[col].notna().mean() > 0.5:
                    df['hour_of_day'] = df[col].dt.hour
                    df['day_of_week'] = df[col].dt.dayofweek
                    df['month']       = df[col].dt.month
                    break
            except: pass

    # Ensure numeric
    numeric_needed = ['temperature', 'dissolved_oxygen', 'ph', 'turbidity', 'ammonia', 'nitrate', 'fish_weight']
    for c in numeric_needed:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')

    # Drop rows with no key features
    key_cols = [c for c in ['temperature', 'dissolved_oxygen', 'ph'] if c in df.columns]
    df = df.dropna(subset=key_cols)
    df = df.drop_duplicates()
    print(f"After cleaning: {len(df):,} rows")

    # Outlier clipping
    for col in ['temperature', 'dissolved_oxygen', 'ph', 'turbidity', 'ammonia', 'nitrate']:
        if col in df.columns:
            Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            IQR = Q3 - Q1
            df[col] = df[col].clip(Q1 - 3*IQR, Q3 + 3*IQR)

    # Feature engineering
    temp = df.get('temperature', pd.Series(np.full(len(df), 24)))
    do   = df.get('dissolved_oxygen', pd.Series(np.full(len(df), 7)))
    ph   = df.get('ph', pd.Series(np.full(len(df), 7)))
    turb = df.get('turbidity', pd.Series(np.full(len(df), 15)))
    ammo = df.get('ammonia', pd.Series(np.full(len(df), 0.01)))
    fw   = df.get('fish_weight', pd.Series(np.full(len(df), 80)))

    df['thermal_stress']  = (temp - 28).clip(lower=0) + (20 - temp).clip(lower=0)
    df['do_deficit']      = (6.0 - do).clip(lower=0)
    df['do_ok']           = (do >= 5.0).astype(int)
    df['ph_deviation']    = (ph - 7.0).abs()
    df['ph_acidic']       = (ph < 6.5).astype(int)
    df['ph_alkaline']     = (ph > 8.5).astype(int)
    df['turbidity_high']  = (turb > 30).astype(int)
    df['ammonia_toxic']   = (ammo > 0.02).astype(int)
    df['env_stress_index']= df['thermal_stress'] + df['do_deficit'] + df['ph_deviation'] + df['turbidity_high'] + df['ammonia_toxic']

    w_temp = 100 * (1 - (df['thermal_stress'] / 10).clip(0, 1))
    w_do   = do.clip(0, 8) / 8 * 100
    w_ph   = 100 - df['ph_deviation'].clip(0, 3) / 3 * 100
    df['water_quality_index'] = (w_temp + w_do + w_ph) / 3

    df['temp_x_do']   = temp * do
    df['ph_x_do']     = ph * do
    df['turb_x_temp'] = turb * temp
    df['temp_sq']     = temp ** 2

    # Lag / rolling
    for col, alias in [('dissolved_oxygen', 'Dissolved Oxygen (g/ml)')]:
        src = 'dissolved_oxygen' if 'dissolved_oxygen' in df.columns else None
        if src:
            df[f'{src}_lag1']       = df[src].shift(1).fillna(method='bfill')
            df[f'{src}_lag2']       = df[src].shift(2).fillna(method='bfill')
            df[f'{src}_roll_mean']  = df[src].rolling(6, min_periods=1).mean()
            df[f'{src}_roll_std']   = df[src].rolling(6, min_periods=1).std().fillna(0)
            df[f'{src}_diff1']      = df[src].diff(1).fillna(0)

    if 'ph' in df.columns:
        df['PH_diff1'] = df['ph'].diff(1).fillna(0)

    # Time features
    if 'hour_of_day' not in df.columns:
        df['hour_of_day'] = 12
        df['day_of_week'] = 0
        df['month']       = 6
    df['month_sin'] = np.sin(2 * np.pi * df.get('month', 6) / 12)
    df['month_cos'] = np.cos(2 * np.pi * df.get('month', 6) / 12)

    # Fish weight column
    if 'fish_weight' in df.columns:
        df['Fish_weight(g)'] = df['fish_weight']
    else:
        df['Fish_weight(g)'] = 80.0

    # pH alias
    if 'ph' in df.columns:
        df['PH'] = df['ph']

    if 'nitrate' in df.columns:
        df['nitrate(g/ml)'] = df['nitrate']
    else:
        df['nitrate(g/ml)'] = 2.0

    # DO aliases for the feature list
    if 'dissolved_oxygen' in df.columns:
        df['Dissolved Oxygen (g/ml)']           = df['dissolved_oxygen']
        df['Dissolved Oxygen (g/ml)_lag1']      = df.get('dissolved_oxygen_lag1', df['dissolved_oxygen'])
        df['Dissolved Oxygen (g/ml)_lag2']      = df.get('dissolved_oxygen_lag2', df['dissolved_oxygen'])
        df['Dissolved Oxygen (g/ml)_roll_mean'] = df.get('dissolved_oxygen_roll_mean', df['dissolved_oxygen'])
        df['Dissolved Oxygen (g/ml)_roll_std']  = df.get('dissolved_oxygen_roll_std', 0)
        df['Dissolved Oxygen (g/ml)_diff1']     = df.get('dissolved_oxygen_diff1', 0)
        df['temperature(C)']                    = df['temperature']

    # Target
    if 'feed_amount' not in df.columns:
        print("⚠️  'feed_amount' column not found — synthesising from domain rules.")
        base = fw * 0.03
        temp_f = np.where((temp>=22)&(temp<=26), 1.1, np.where(temp<18, 0.4, 0.8))
        do_f   = np.where(do>=7, 1.05, np.where(do>=5, 1.0, np.where(do>=3, 0.5, 0.0)))
        ph_f   = np.where((ph>=6.8)&(ph<=8.2), 1.0, np.where(ph<6.5, 0.4, 0.7))
        df['feed_amount'] = (base * temp_f * do_f * ph_f).clip(0, 200)

    df['feed_amount'] = pd.to_numeric(df['feed_amount'], errors='coerce').fillna(df['feed_amount'].median() if 'feed_amount' in df else 15)

    return df


FEATURE_LIST = [
    'Fish_weight(g)', 'day_of_week', 'PH', 'turb_x_temp', 'env_stress_index',
    'month', 'water_quality_index', 'nitrate(g/ml)', 'day_of_week', 'month_cos',
    'ph_x_do', 'month_sin', 'Dissolved Oxygen (g/ml)_lag2', 'Dissolved Oxygen (g/ml)_lag1',
    'Dissolved Oxygen (g/ml)', 'Dissolved Oxygen (g/ml)_roll_mean', 'temperature(C)',
    'Dissolved Oxygen (g/ml)_roll_std', 'do_deficit', 'ph_acidic',
    'Dissolved Oxygen (g/ml)_diff1', 'turbidity_high', 'do_ok', 'PH_diff1',
    'thermal_stress',
]


def train(df: pd.DataFrame):
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
    from sklearn.preprocessing import RobustScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    feat_cols = [c for c in FEATURE_LIST if c in df.columns]
    missing = set(FEATURE_LIST) - set(feat_cols)
    if missing:
        print(f"  Missing features (will use 0): {missing}")
        for c in missing:
            df[c] = 0.0
        feat_cols = FEATURE_LIST

    X = df[feat_cols].fillna(0)
    y = df['feed_amount']
    valid = X.notna().all(axis=1) & y.notna()
    X, y = X[valid], y[valid]
    print(f"Training data: {X.shape}")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

    scaler = RobustScaler()
    X_tr_sc = scaler.fit_transform(X_train)
    X_te_sc = scaler.transform(X_test)

    # Try XGBoost first
    try:
        import xgboost as xgb
        print("Training XGBoost...")
        model = xgb.XGBRegressor(n_estimators=400, learning_rate=0.05, max_depth=6,
                                  subsample=0.8, colsample_bytree=0.8, random_state=42,
                                  tree_method='hist', verbosity=0)
        model.fit(X_tr_sc, y_train)
        model_name = "XGBoost"
    except ImportError:
        print("XGBoost not found, training GradientBoosting...")
        model = GradientBoostingRegressor(n_estimators=300, learning_rate=0.05,
                                           max_depth=5, random_state=42)
        model.fit(X_tr_sc, y_train)
        model_name = "GradientBoosting"

    y_pred = model.predict(X_te_sc)
    mae  = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2   = r2_score(y_test, y_pred)
    print(f"\n{'='*50}")
    print(f"  Model : {model_name}")
    print(f"  MAE   : {mae:.4f} g/fish/day")
    print(f"  RMSE  : {rmse:.4f}")
    print(f"  R²    : {r2:.4f}")
    print(f"{'='*50}")

    # Save
    with open(MODELS_DIR / "best_model.pkl", 'wb') as f: pickle.dump(model, f)
    with open(MODELS_DIR / "scaler.pkl", 'wb') as f:     pickle.dump(scaler, f)
    with open(MODELS_DIR / "features.txt", 'w') as f:    f.write('\n'.join(feat_cols))

    meta = {
        "model":            model_name,
        "task":             "regression",
        "features":         feat_cols,
        "training_samples": int(len(X_train)),
        "test_mae":         round(float(mae), 4),
        "test_rmse":        round(float(rmse), 4),
        "test_r2":          round(float(r2), 4),
    }
    with open(MODELS_DIR / "meta.json", 'w') as f: json.dump(meta, f, indent=2)
    print(f"\n✅  Saved to {MODELS_DIR}")


def main():
    parser = argparse.ArgumentParser(description="Train AquaSmart ML model")
    parser.add_argument('--data', required=True, help='Path to CSV folder or zip file')
    args = parser.parse_args()

    print(f"Loading data from: {args.data}")
    df = load_csvs(args.data)
    df = preprocess(df)
    train(df)


if __name__ == '__main__':
    main()
