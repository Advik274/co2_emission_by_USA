import pandas as pd
import numpy as np
import joblib
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NATIONAL_AGGREGATE_STATES = {'United States'}
AGGREGATE_SECTORS = {'Total carbon dioxide emissions from all sectors'}
AGGREGATE_FUELS = {'All Fuels'}

# ──────────────────────────────────────────────────────────────────────────────
# Data Loading
# ──────────────────────────────────────────────────────────────────────────────

def load_raw_data():
    """Load the raw CO2 emission data."""
    data_path = os.path.join(BASE_DIR, 'data', 'raw', 'Co2 emmision dataset fetched by API.csv')
    return pd.read_csv(data_path)

def filter_state_level_data(df):
    """Return only state-level rows, excluding national aggregate records."""
    if 'state-name' not in df.columns:
        return df.copy()
    return df[~df['state-name'].isin(NATIONAL_AGGREGATE_STATES)].copy()

def filter_detail_rows(df, exclude_sector_totals=True, exclude_fuel_totals=True):
    """Remove aggregate sector/fuel rows before category breakdowns."""
    detail_df = df.copy()
    if exclude_sector_totals and 'sector-name' in detail_df.columns:
        detail_df = detail_df[~detail_df['sector-name'].isin(AGGREGATE_SECTORS)]
    if exclude_fuel_totals and 'fuel-name' in detail_df.columns:
        detail_df = detail_df[~detail_df['fuel-name'].isin(AGGREGATE_FUELS)]
    return detail_df

def load_processed_data():
    """Load processed train/test data."""
    data_dir = os.path.join(BASE_DIR, 'data', 'processed')
    X_train = pd.read_csv(os.path.join(data_dir, 'X_train.csv'))
    X_test  = pd.read_csv(os.path.join(data_dir, 'X_test.csv'))
    y_train = pd.read_csv(os.path.join(data_dir, 'y_train.csv'))
    y_test  = pd.read_csv(os.path.join(data_dir, 'y_test.csv'))
    return X_train, X_test, y_train, y_test

def get_unique_values():
    """Extract unique values for state, sector, fuel from raw data."""
    df = filter_state_level_data(load_raw_data())
    states  = sorted(df['state-name'].unique().tolist())
    sectors = sorted(
        s for s in df['sector-name'].unique().tolist()
        if s not in AGGREGATE_SECTORS
    )
    fuels = sorted(
        f for f in df['fuel-name'].unique().tolist()
        if f not in AGGREGATE_FUELS
    )
    years   = sorted(df['period'].unique().tolist())
    return states, sectors, fuels, years

# ──────────────────────────────────────────────────────────────────────────────
# Model Loading (safe — never crashes)
# ──────────────────────────────────────────────────────────────────────────────

_LFS_MARKER = b'version https://git-lfs.github.com/spec/v1'

def _is_lfs_pointer(path):
    """Return True if the file is a Git LFS pointer (not the real model)."""
    try:
        with open(path, 'rb') as f:
            header = f.read(64)
        return _LFS_MARKER in header
    except Exception:
        return False

def load_model_safe(model_type: str):
    """
    Safely load a model. Returns (model, status_message).
    status_message is None on success, a human-readable string on failure.
    """
    if 'Random Forest' in model_type or model_type == 'RF':
        path = os.path.join(BASE_DIR, 'models', 'rf', 'random_forest.joblib')
    elif 'XGBoost' in model_type:
        path = os.path.join(BASE_DIR, 'models', 'xgboost', 'xgboost_regressor_model.joblib')
    else:
        return None, f"Unknown model type: {model_type}"

    if not os.path.exists(path):
        return None, f"Model file not found: {os.path.basename(path)}"

    if _is_lfs_pointer(path):
        return None, (
            "Model file is a Git LFS pointer — the actual model wasn't downloaded. "
            "Run `git lfs pull` to fetch the real model files. "
            "Using trend-based estimate instead."
        )

    try:
        model = joblib.load(path)
        return model, None
    except Exception as e:
        return None, f"Failed to load model ({e}). Using trend-based estimate instead."

def load_ann_model_safe(model_name: str = 'simple_ann'):
    """
    Safely load an ANN .keras model. Returns (model, status_message).
    """
    path = os.path.join(BASE_DIR, 'models', 'ann', f'{model_name}.keras')
    if not os.path.exists(path):
        return None, f"ANN model file not found: {model_name}.keras"
    try:
        import tensorflow as tf
        model = tf.keras.models.load_model(path)
        return model, None
    except ImportError:
        return None, "TensorFlow not installed. Run: pip install tensorflow"
    except Exception as e:
        return None, f"Failed to load ANN model ({e})"

# ──────────────────────────────────────────────────────────────────────────────
# Feature Engineering
# ──────────────────────────────────────────────────────────────────────────────

def get_feature_columns():
    """Return the feature column names used in training."""
    return [
        'value_log_transformed_lag1',
        'value_log_transformed_roll_mean3',
        'sector-name_Electric Power carbon dioxide emissions',
        'sector-name_Industrial carbon dioxide emissions',
        'sector-name_Residential carbon dioxide emissions',
        'sector-name_Total carbon dioxide emissions from all sectors',
        'sector-name_Transportation carbon dioxide emissions',
        'fuel-name_Coal',
        'fuel-name_Natural Gas',
        'fuel-name_Petroleum'
    ]

def prepare_input_features(state, sector, fuel, year, historical_data):
    """Prepare features for prediction based on user inputs."""
    state_data = historical_data[
        (historical_data['state-name'] == state) &
        (historical_data['sector-name'] == sector) &
        (historical_data['fuel-name'] == fuel)
    ].sort_values('period')

    if len(state_data) == 0:
        return None

    state_data = state_data.copy()
    state_data['value_log_transformed'] = np.log1p(state_data['value'])
    state_data['value_log_transformed_lag1'] = state_data['value_log_transformed'].shift(1).fillna(0)
    state_data['value_log_transformed_roll_mean3'] = (
        state_data['value_log_transformed'].rolling(3, min_periods=1).mean().shift(1).fillna(0)
    )

    if year <= state_data['period'].max():
        row = state_data[state_data['period'] == year]
        if len(row) > 0:
            return row.iloc[0][['value_log_transformed_lag1', 'value_log_transformed_roll_mean3']].values

    last_year      = state_data['period'].max()
    last_log_value = state_data.iloc[-1]['value_log_transformed']
    roll_mean      = state_data['value_log_transformed'].tail(3).mean()

    years_ahead = year - last_year
    if years_ahead > 0:
        recent_values = state_data['value_log_transformed'].tail(10)
        if len(recent_values) >= 2:
            trend = (recent_values.iloc[-1] - recent_values.iloc[0]) / len(recent_values)
        else:
            trend = -0.02
        projected_log_value = last_log_value + (trend * years_ahead * 0.8)
        projected_log_value = max(projected_log_value, last_log_value * 0.5)
    else:
        projected_log_value = last_log_value

    sector_cols = get_feature_columns()[2:7]
    fuel_cols   = get_feature_columns()[7:]

    sector_features = [
        1.0 if sector == s.replace('sector-name_', '') else 0.0
        for s in sector_cols
    ]
    fuel_features = [
        1.0 if fuel == f.replace('fuel-name_', '') else 0.0
        for f in fuel_cols
    ]

    features = np.array([projected_log_value, roll_mean] + sector_features + fuel_features)
    return features

# ──────────────────────────────────────────────────────────────────────────────
# Trend-Based Prediction (always works — no model needed)
# ──────────────────────────────────────────────────────────────────────────────

def trend_predict(state, sector, fuel, year, df):
    """
    Pure trend-based prediction. Uses historical data to compute a linear trend
    and project forward. Always returns a (value, confidence_low, confidence_high) tuple.
    """
    hist = df[
        (df['state-name'] == state) &
        (df['sector-name'] == sector) &
        (df['fuel-name'] == fuel)
    ].sort_values('period')

    if len(hist) == 0:
        return None, None, None

    last_val = float(hist.iloc[-1]['value'])
    last_yr  = int(hist['period'].max())
    yrs_diff = int(year) - last_yr

    if yrs_diff <= 0:
        # Historical year — look it up directly
        row = hist[hist['period'] == year]
        if len(row) > 0:
            v = float(row.iloc[0]['value'])
            return v, v * 0.9, v * 1.1
        return last_val, last_val * 0.9, last_val * 1.1

    # Compute recent trend (last decade)
    recent = hist[hist['period'] >= max(hist['period'].max() - 10, hist['period'].min())]
    if len(recent) >= 2:
        vals  = recent['value'].astype(float).values
        span  = len(vals) - 1
        annual_change = (vals[-1] - vals[0]) / span if span > 0 else 0
        # Cap change rate at ±5% per year
        max_change = last_val * 0.05
        annual_change = max(-max_change, min(max_change, annual_change))
    else:
        annual_change = -last_val * 0.01  # default 1% annual decline

    pred = last_val + annual_change * yrs_diff
    pred = max(pred, 0.001)

    # Widen confidence interval with years ahead
    spread = 0.10 + 0.01 * yrs_diff
    return pred, pred * (1 - spread), pred * (1 + spread)

# ──────────────────────────────────────────────────────────────────────────────
# Transforms & Metrics
# ──────────────────────────────────────────────────────────────────────────────

def inverse_log_transform(value):
    """Convert log-transformed prediction back to original scale."""
    return float(np.expm1(value))

def get_model_metrics():
    """Return known model performance metrics from research."""
    return {
        'Random Forest': {'MSE': 367.5128, 'R2': 0.9917, 'MSE_log': 0.0424, 'R2_log': 0.9831},
        'XGBoost':       {'MSE': 857.6206, 'R2': 0.9806, 'MSE_log': 0.0427, 'R2_log': 0.9830},
        'ANN (Simple)':  {'MSE': None,     'R2': None,   'note': 'Available for inference'}
    }

def get_ann_model_info():
    """Return information about available ANN models."""
    model_dir = os.path.join(BASE_DIR, 'models', 'ann')
    if not os.path.exists(model_dir):
        return []
    return [f.replace('.keras', '') for f in os.listdir(model_dir) if f.endswith('.keras')]

def check_models_available():
    """
    Return a dict of model availability status.
    {'RF': True/False, 'XGBoost': True/False, 'ANN': ['simple_ann', ...]}
    """
    rf_path  = os.path.join(BASE_DIR, 'models', 'rf', 'random_forest.joblib')
    xgb_path = os.path.join(BASE_DIR, 'models', 'xgboost', 'xgboost_regressor_model.joblib')
    ann_models = get_ann_model_info()

    return {
        'RF':      os.path.exists(rf_path) and not _is_lfs_pointer(rf_path),
        'XGBoost': os.path.exists(xgb_path) and not _is_lfs_pointer(xgb_path),
        'ANN':     ann_models,
    }
