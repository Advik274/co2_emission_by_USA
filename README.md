# USA CO2 Emissions Dashboard and Forecasting

An interactive Streamlit application for exploring state-level carbon dioxide emissions in the United States and forecasting future emissions by state, sector, fuel type, and year.

The project uses historical emissions data from the U.S. Energy Information Administration (EIA), research notebooks for preprocessing and model training, and a Streamlit UI for dashboard analytics, forecasts, model comparison, and usage telemetry.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![Plotly](https://img.shields.io/badge/Plotly-5.15%2B-green)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.13%2B-orange)

## What This App Does

- Shows historical CO2 emissions trends for selected U.S. states.
- Filters analysis by state, sector, fuel type, and year.
- Excludes national aggregate rows from state-level charts so the dashboard does not double count the whole United States as a state.
- Removes aggregate sector/fuel rows from detail charts where they would distort statewise totals.
- Forecasts future emissions for a selected state, sector, fuel, and year.
- Falls back to a trend-based forecast when large Git LFS model files are unavailable locally.
- Compares Random Forest, XGBoost, and ANN model performance.
- Tracks simple prediction UI telemetry for the Analytics page.

## Pages

### Dashboard

The main dashboard provides statewise emissions analysis through:

- Timeline chart
- Sector breakdown
- Fuel breakdown
- U.S. choropleth map
- Top state rankings
- KPI cards for total emissions, average per record, peak year, and trend

### Predictions

The forecasting page lets users select:

- State
- Emission sector
- Fuel type
- Forecast year
- Model type

The prediction result is for the selected state/sector/fuel slice, not total statewide emissions unless the chosen inputs represent a broad total category. If trained Random Forest or XGBoost files are missing, the app uses a trend-based estimate from historical data.

### Model Comparison

The model comparison page summarizes model metrics and tradeoffs for:

- Random Forest
- XGBoost
- Simple ANN
- Deep ANN

### Analytics

The analytics page displays local telemetry from prediction page usage, including:

- Page views
- Generate clicks
- Completed forecasts
- Variant conversion summary
- Funnel visualization

## Tech Stack

- Streamlit for the web app
- Pandas and NumPy for data handling
- Plotly for interactive charts
- Scikit-learn and Joblib for tree-based models
- XGBoost for gradient boosted forecasting
- TensorFlow/Keras for ANN models
- Git LFS expected for large model artifacts

## Project Structure

```text
.
├── data/
│   ├── raw/
│   │   └── Co2 emmision dataset fetched by API.csv
│   ├── processed/
│   │   ├── X_train.csv
│   │   ├── X_test.csv
│   │   ├── y_train.csv
│   │   └── y_test.csv
│   └── ab_test_experiments.json
├── models/
│   ├── ann/
│   │   ├── simple_ann.keras
│   │   ├── deeper_ann.keras
│   │   └── ...
│   ├── rf/
│   │   └── random_forest.joblib
│   └── xgboost/
│       └── xgboost_regressor_model.joblib
├── notebooks/
│   ├── CO2_EDA_Initial_Cleaning.ipynb
│   ├── CO2_Preprocessing_Feature_Engineering.ipynb
│   ├── CO2_Model_Training_XGBoost.ipynb
│   ├── CO2_Model_Evaluation_Analysis.ipynb
│   └── CO2_Conclusion.ipynb
├── src/
│   ├── ab_testing.py
│   └── utils.py
├── streamlit_app/
│   ├── app.py
│   ├── components.py
│   ├── styles.css
│   └── pages/
│       ├── predictions.py
│       ├── model_comparison.py
│       └── analytics.py
├── .streamlit/
│   └── config.toml
├── requirements.txt
└── README.md
```

## Setup

### 1. Clone The Repository

```bash
git clone https://github.com/Advik274/co2_emission_by_USA_project.git
cd co2_emission_by_USA_project
```

If you cloned into a different folder name, run the remaining commands from the repository root.

### 2. Create A Virtual Environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Fetch Large Model Files If Needed

Some trained model files may be stored through Git LFS. If Random Forest or XGBoost shows as unavailable in the app, run:

```bash
git lfs install
git lfs pull
```

The app still works without those files because it falls back to trend-based estimates.

### 5. Run The Streamlit App

From the repository root:

```bash
python -m streamlit run streamlit_app/app.py
```

The app will usually open at:

```text
http://localhost:8501
```

If that port is busy, Streamlit will suggest another local URL.

## Model Notes

The project includes model training and evaluation notebooks. The Streamlit app can use:

| Model | Purpose | Availability |
| --- | --- | --- |
| Random Forest | Highest accuracy tree-based model | May require Git LFS |
| XGBoost | Fast boosted-tree alternative | May require Git LFS |
| Simple ANN | Local neural-network inference | `.keras` file |
| Deep ANN | Larger ANN architecture | `.keras` file |
| Trend estimate | Always-available fallback | Computed from historical data |

Known benchmark values used in the app:

| Model | R2 | MSE |
| --- | ---: | ---: |
| Random Forest | 0.9917 | 367.51 |
| XGBoost | 0.9806 | 857.62 |
| ANN (Simple) | 0.9700 | 1200.00 |
| ANN (Deep) | 0.9750 | 1050.00 |

## Data Notes

- Source: U.S. Energy Information Administration (EIA)
- Units: million metric tons of CO2
- Granularity: state, sector, fuel type, and year
- The app filters out `United States` national aggregate rows for statewise views.
- The app filters out aggregate sector/fuel rows in detail charts to avoid double counting.

## Development Checks

Useful sanity checks before committing changes:

```bash
python -m py_compile src/utils.py src/ab_testing.py streamlit_app/app.py streamlit_app/components.py streamlit_app/pages/predictions.py streamlit_app/pages/analytics.py streamlit_app/pages/model_comparison.py
git diff --check
```

On some systems, Python may need a writable bytecode cache directory:

```bash
set PYTHONPYCACHEPREFIX=.pycache_tmp
python -m py_compile src\utils.py src\ab_testing.py streamlit_app\app.py streamlit_app\components.py streamlit_app\pages\predictions.py streamlit_app\pages\analytics.py streamlit_app\pages\model_comparison.py
```

## Deployment Notes

For Streamlit Cloud:

1. Push the repository to GitHub.
2. Create a new Streamlit app from the GitHub repository.
3. Set the main file path to:

```text
streamlit_app/app.py
```

4. Ensure large model files are available through Git LFS or rely on the trend-based fallback.

## Current Limitations

- Forecasts are only as strong as the historical state/sector/fuel series selected.
- Very small categories, such as a state-sector-fuel combination already near zero, can produce near-zero forecasts.
- Random Forest and XGBoost may not load unless the real model artifacts are present instead of Git LFS pointer files.
- The telemetry file is local JSON and is not intended to be a production analytics database.

## License

This project is intended for educational and research use.

## Acknowledgments

- U.S. Energy Information Administration for emissions data
- Streamlit, Plotly, Scikit-learn, XGBoost, and TensorFlow/Keras for the project tooling
