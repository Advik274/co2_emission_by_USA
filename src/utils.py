import pandas as pd
import numpy as np
import joblib
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_raw_data():
    """Load the raw CO2 emission data."""
    data_path = os.path.join(BASE_DIR, 'data', 'raw', 'Co2 emmision dataset fetched by API.csv')
    return pd.read_csv(data_path)

def load_processed_data():
    """Load processed train/test data."""
    data_dir = os.path.join(BASE_DIR, 'data', 'processed')
    X_train = pd.read_csv(os.path.join(data_dir, 'X_train.csv'))
    X_test = pd.read_csv(os.path.join(data_dir, 'X_test.csv'))
    y_train = pd.read_csv(os.path.join(data_dir, 'y_train.csv'))
    y_test = pd.read_csv(os.path.join(data_dir, 'y_test.csv'))
    return X_train, X_test, y_train, y_test

def get_unique_values():
    """Extract unique values for state, sector, fuel from raw data."""
    df = load_raw_data()
    states = sorted(df['state-name'].unique().tolist())
    sectors = sorted(df['sector-name'].unique().tolist())
    fuels = sorted(df['fuel-name'].unique().tolist())
    years = sorted(df['period'].unique().tolist())
    return states, sectors, fuels, years

def load_xgboost_model():
    """Load the trained XGBoost model."""
    model_path = os.path.join(BASE_DIR, 'models', 'xgboost', 'xgboost_regressor_model.joblib')
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None

def load_ann_model(model_name='simple_ann'):
    """Load an ANN model by name."""
    model_path = os.path.join(BASE_DIR, 'models', 'ann', f'{model_name}.keras')
    if os.path.exists(model_path):
        import tensorflow as tf
        return tf.keras.models.load_model(model_path)
    return None

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
    state_data['value_log_transformed_roll_mean3'] = state_data['value_log_transformed'].rolling(3, min_periods=1).mean().shift(1).fillna(0)
    
    if year <= state_data['period'].max():
        row = state_data[state_data['period'] == year]
        if len(row) > 0:
            return row.iloc[0][['value_log_transformed_lag1', 'value_log_transformed_roll_mean3']].values
    
    last_year = state_data['period'].max()
    last_log_value = state_data.iloc[-1]['value_log_transformed']
    roll_mean = state_data['value_log_transformed'].tail(3).mean()
    
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
    fuel_cols = get_feature_columns()[7:]
    
    sector_features = [1.0 if sector == s.replace('sector-name_', '').replace(' carbon dioxide emissions', '') else 0.0 
                      for s in sector_cols]
    fuel_features = [1.0 if fuel == f.replace('fuel-name_', '') else 0.0 
                    for f in fuel_cols]
    
    features = np.array([projected_log_value, roll_mean] + sector_features + fuel_features)
    return features

def inverse_log_transform(value):
    """Convert log-transformed prediction back to original scale."""
    return np.expm1(value)

def get_model_metrics():
    """Return known model performance metrics from research."""
    return {
        'Random Forest': {'MSE': 367.5128, 'R2': 0.9917, 'MSE_log': 0.0424, 'R2_log': 0.9831},
        'XGBoost': {'MSE': 857.6206, 'R2': 0.9806, 'MSE_log': 0.0427, 'R2_log': 0.9830},
        'ANN (Simple)': {'MSE': None, 'R2': None, 'note': 'Available for inference'}
    }

def get_ann_model_info():
    """Return information about available ANN models."""
    model_dir = os.path.join(BASE_DIR, 'models', 'ann')
    ann_models = [f.replace('.keras', '') for f in os.listdir(model_dir) if f.endswith('.keras')]
    return ann_models