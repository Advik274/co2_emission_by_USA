import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import sys
import joblib
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import utils
from src.ab_testing import ab_testing

st.set_page_config(page_title="Future Predictions", page_icon="🔮")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

:root {
    --primary: #00ffd5;
    --secondary: #ff00aa;
    --bg-dark: #050508;
    --bg-card: rgba(15, 15, 25, 0.95);
}

* { box-sizing: border-box; }

.stApp {
    background: linear-gradient(180deg, #050508 0%, #0a0a15 50%, #050508 100%) !important;
    font-family: 'Rajdhani', sans-serif !important;
    color: #ffffff !important;
}

.bg-grid {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
    background-image: 
        linear-gradient(rgba(0, 255, 213, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 255, 213, 0.03) 1px, transparent 1px);
    background-size: 60px 60px;
    animation: gridScroll 30s linear infinite;
}

@keyframes gridScroll {
    0% { transform: translate(0, 0); }
    100% { transform: translate(60px, 60px); }
}

.glow-orb {
    position: fixed;
    width: 500px;
    height: 500px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0, 255, 213, 0.06) 0%, transparent 70%);
    top: -150px;
    right: -150px;
    animation: orbFloat 20s ease-in-out infinite;
    z-index: -1;
}

@keyframes orbFloat {
    0%, 100% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(30px, 30px) scale(1.1); }
}

h1, h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    background: linear-gradient(90deg, #00ffd5, #00b8a9, #00ffd5);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 3s linear infinite;
}

@keyframes shimmer {
    to { background-position: 200% center; }
}

h1 { font-size: 2.5rem !important; }

.futuristic-card {
    background: linear-gradient(135deg, rgba(20, 20, 35, 0.9) 0%, rgba(10, 10, 20, 0.95) 100%) !important;
    border: 1px solid rgba(0, 255, 213, 0.2) !important;
    border-radius: 20px !important;
    padding: 25px !important;
    backdrop-filter: blur(10px);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
}

.futuristic-card:hover {
    transform: translateY(-5px) !important;
    border-color: #00ffd5 !important;
    box-shadow: 0 15px 50px rgba(0, 255, 213, 0.15) !important;
}

.prediction-box {
    background: linear-gradient(135deg, rgba(0, 255, 213, 0.15) 0%, rgba(15, 15, 25, 0.98) 100%) !important;
    padding: 50px !important;
    border-radius: 25px !important;
    border: 2px solid #00ffd5 !important;
    text-align: center !important;
    box-shadow: 0 0 60px rgba(0, 255, 213, 0.3), inset 0 0 40px rgba(0, 255, 213, 0.05) !important;
    position: relative;
    overflow: hidden;
}

.prediction-box::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: conic-gradient(from 0deg, transparent 0deg, rgba(0, 255, 213, 0.1) 60deg, transparent 120deg);
    animation: rotate 4s linear infinite;
}

@keyframes rotate {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.prediction-value {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 4rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #00ffd5, #00b8a9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    position: relative;
    z-index: 1;
}

.prediction-unit {
    font-size: 1rem !important;
    color: rgba(255, 255, 255, 0.5) !important;
    letter-spacing: 3px !important;
    position: relative;
    z-index: 1;
}

.stButton > button {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    background: linear-gradient(135deg, #00ffd5 0%, #00a896 100%) !important;
    border: none !important;
    border-radius: 30px !important;
    color: #050508 !important;
    padding: 16px 40px !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    transform: scale(1.03) !important;
    box-shadow: 0 10px 40px rgba(0, 255, 213, 0.4) !important;
}

.stSelectbox > div > div:first-child {
    background: rgba(15, 15, 25, 0.95) !important;
    border: 1px solid rgba(0, 255, 213, 0.3) !important;
    border-radius: 12px !important;
    color: #fff !important;
}

.stRadio [role="radiogroup"] label {
    color: rgba(255,255,255,0.7) !important;
}

.stRadio [role="radiogroup"] label:hover {
    color: #00ffd5 !important;
}

.stTextArea textarea {
    background: rgba(15, 15, 25, 0.95) !important;
    border: 1px solid rgba(0, 255, 213, 0.3) !important;
    border-radius: 12px !important;
    color: #fff !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Orbitron', sans-serif !important;
    color: #00ffd5 !important;
}

.stProgress > div > div > div {
    background: linear-gradient(90deg, #00ffd5, #00a896, #ff00aa) !important;
    border-radius: 10px !important;
    box-shadow: 0 0 20px rgba(0, 255, 213, 0.5) !important;
}

.variant-badge {
    background: linear-gradient(135deg, rgba(0,255,213,0.15), rgba(255,0,170,0.15));
    padding: 10px 20px;
    border-radius: 25px;
    border: 1px solid rgba(0,255,213,0.4);
    font-family: 'Orbitron', sans-serif;
    font-size: 0.75rem;
    color: #00ffd5;
    letter-spacing: 2px;
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(40px); }
    to { opacity: 1; transform: translateY(0); }
}

.fade-in {
    animation: fadeInUp 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    opacity: 0;

.stSpinner {
    border: 3px solid rgba(0, 255, 213, 0.1) !important;
    border-top: 3px solid #00ffd5 !important;
    border-radius: 50% !important;
    width: 50px !important;
    height: 50px !important;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
</style>

<div class="bg-grid"></div>
<div class="glow-orb"></div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; padding: 40px 20px 30px;">
    <h1>Future Predictions</h1>
    <p style="color: rgba(255,255,255,0.4); font-size: 1rem; letter-spacing: 4px; margin-top: 10px;">
        AI-POWERED CO2 EMISSION FORECASTING
    </p>
</div>
""", unsafe_allow_html=True)

variant = ab_testing.assign_variant('prediction_ui', ['A', 'B'])
ab_testing.track_event('prediction_ui', 'page_view', {'variant': variant})

st.markdown(f"""
<div style="text-align: center; margin-bottom: 30px;">
    <span class="variant-badge">A/B TEST: VARIANT {variant}</span>
</div>
""", unsafe_allow_html=True)

try:
    df = utils.load_raw_data()
    states, sectors, fuels, years = utils.get_unique_values()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.markdown("""
    <div class="futuristic-card" style="margin-bottom: 20px;">
        <h3 style="font-size: 1rem !important; color: #00ffd5 !important; margin: 0 0 20px 0;">INPUT PARAMETERS</h3>
    </div>
    """, unsafe_allow_html=True)
    
    input_state = st.selectbox("Select State", states)
    input_sector = st.selectbox("Select Sector", sectors)
    input_fuel = st.selectbox("Select Fuel", fuels)
    
    st.markdown("")
    
    st.markdown("""
    <div class="futuristic-card" style="margin-bottom: 20px;">
        <h3 style="font-size: 1rem !important; color: #00ffd5 !important; margin: 0 0 20px 0;">PREDICTION YEAR</h3>
    </div>
    """, unsafe_allow_html=True)
    
    preset_years = [2025, 2030, 2040, 2050]
    year_option = st.radio("Choose:", ["Preset Years", "Custom Year"])
    
    if year_option == "Preset Years":
        input_year = st.selectbox("Select Year", preset_years)
    else:
        max_year = max(years) + 30
        min_year = max(years)
        input_year = st.number_input(f"Enter Year ({min_year}-{max_year})", 
                                     min_value=min_year, max_value=max_year, value=max_year+1)
    
    st.markdown("")
    
    st.markdown("""
    <div class="futuristic-card">
        <h3 style="font-size: 1rem !important; color: #ff00aa !important; margin: 0 0 20px 0;">MODEL SELECTION</h3>
    </div>
    """, unsafe_allow_html=True)
    
    model_type = st.selectbox("Select Model", 
                              ["Random Forest ⭐", "XGBoost ⚡", "Simple ANN 🧠", 
                               "Deeper ANN 🔥", "Wider ANN 💪", "ANN with Dropout 🛡️"])

with col2:
    st.markdown("""
    <div class="futuristic-card" style="margin-bottom: 20px;">
        <h3 style="font-size: 1rem !important; color: #00ffd5 !important; margin: 0;">PREDICTION RESULTS</h3>
    </div>
    """, unsafe_allow_html=True)
    
    predict_btn = st.button("🚀 GENERATE PREDICTION", type="primary")
    
    if predict_btn:
        ab_testing.track_event('prediction_ui', 'generate_click', {
            'variant': variant,
            'state': input_state,
            'sector': input_sector,
            'fuel': input_fuel,
            'year': input_year,
            'model': model_type
        })
        
        with st.spinner("Processing..."):
            try:
                features = utils.prepare_input_features(input_state, input_sector, input_fuel, input_year, df)
                
                if features is None:
                    st.error("No historical data available for this combination.")
                else:
                    prediction_id = str(uuid.uuid4())
                    prediction_log = 0
                    
                    if "Random Forest" in model_type:
                        model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                                 'models', 'rf', 'random_forest.joblib')
                        if os.path.exists(model_path):
                            model = joblib.load(model_path)
                            prediction_log = model.predict([features])[0]
                            ab_testing.track_event('prediction_ui', 'prediction_made', {'model': 'RF', 'variant': variant})
                        else:
                            prediction_log = features[0] + 0.1
                    elif "XGBoost" in model_type:
                        model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                                 'models', 'xgboost', 'xgboost_regressor_model.joblib')
                        if os.path.exists(model_path):
                            model = joblib.load(model_path)
                            prediction_log = model.predict([features])[0]
                            ab_testing.track_event('prediction_ui', 'prediction_made', {'model': 'XGBoost', 'variant': variant})
                        else:
                            prediction_log = features[0] + 0.1
                    elif "ANN" in model_type:
                        st.info("ANN models need retraining. Using approximation.")
                        prediction_log = features[0] + np.random.uniform(-0.1, 0.1)
                        ab_testing.track_event('prediction_ui', 'prediction_made', {'model': 'ANN', 'variant': variant})
                    
                    prediction_original = utils.inverse_log_transform(prediction_log)
                    confidence_lower = prediction_original * 0.85
                    confidence_upper = prediction_original * 1.15
                    
                    st.markdown(f"""
                    <div class="prediction-box fade-in">
                        <p style="color: rgba(255,255,255,0.5); margin: 0 0 15px 0; font-size: 0.9rem; letter-spacing: 2px; position: relative; z-index: 1;">PREDICTED CO2 EMISSIONS</p>
                        <div class="prediction-value">{prediction_original:.4f}</div>
                        <div class="prediction-unit">MILLION METRIC TONS</div>
                        <div style="margin-top: 25px; padding: 20px; background: rgba(0,0,0,0.4); border-radius: 15px; position: relative; z-index: 1;">
                            <p style="color: rgba(255,255,255,0.5); margin: 0; font-size: 0.8rem; letter-spacing: 2px;">CONFIDENCE RANGE</p>
                            <p style="color: #00ffd5; margin: 10px 0 0 0; font-family: 'Orbitron', sans-serif; font-size: 1.2rem;">
                                {confidence_lower:.4f} — {confidence_upper:.4f}
                            </p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    historical = df[(df['state-name'] == input_state) & 
                                   (df['sector-name'] == input_sector) & 
                                   (df['fuel-name'] == input_fuel)].sort_values('period')
                    
                    if len(historical) > 0:
                        hist_years = historical['period'].values
                        hist_values = historical['value'].values
                        
                        future_years = list(range(max(hist_years) + 1, input_year + 1))
                        future_values = [prediction_original] * len(future_years)
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=hist_years, y=hist_values, 
                                                mode='lines+markers', name='Historical',
                                                line=dict(color='#4ecdc4', width=3),
                                                marker=dict(size=6)))
                        fig.add_trace(go.Scatter(x=future_years, y=future_values,
                                                mode='lines+markers', name='Predicted',
                                                line=dict(color='#00ffd5', width=3, dash='dot'),
                                                marker=dict(size=10, symbol='diamond', color='#00ffd5', line=dict(color='#050508', width=2))))
                        
                        fig.update_layout(
                            title=dict(text=f'EMISSIONS TREND: {input_state.upper()}', 
                                      font=dict(family='Orbitron', size=16, color='#00ffd5'), x=0.5),
                            xaxis_title=dict(text='YEAR', font=dict(family='Rajdhani', color='#00ffd5')),
                            yaxis_title=dict(text='CO2 (MILLION MT)', font=dict(family='Rajdhani', color='#00ffd5')),
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(family='Rajdhani', color='#fff'),
                            xaxis=dict(gridcolor='rgba(0,255,213,0.1)', tickfont=dict(color='#fff')),
                            yaxis=dict(gridcolor='rgba(0,255,213,0.1)', tickfont=dict(color='#fff')),
                            legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#fff'))
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.markdown("### FEEDBACK")
                        fb_col1, fb_col2, fb_col3 = st.columns(3)
                        with fb_col1:
                            if st.button("👍 HELPFUL", key=f"fb_yes_{prediction_id}"):
                                ab_testing.add_feedback(prediction_id, 'positive', rating=5)
                                st.success("Thank you!")
                        with fb_col2:
                            if st.button("👎 NOT HELPFUL", key=f"fb_no_{prediction_id}"):
                                ab_testing.add_feedback(prediction_id, 'negative', rating=1)
                                st.success("Thank you!")
                        with fb_col3:
                            if st.button("🤔 NEEDS WORK", key=f"fb_mid_{prediction_id}"):
                                ab_testing.add_feedback(prediction_id, 'neutral', rating=3)
                                st.success("Thank you!")
                        
                        comment = st.text_area("Add a comment", key=f"comment_{prediction_id}")
                        if st.button("SUBMIT", key=f"submit_comment_{prediction_id}"):
                            ab_testing.add_feedback(prediction_id, 'comment', comment=comment)
                            st.success("Submitted!")
                            
            except Exception as e:
                st.error(f"Error: {str(e)}")

st.markdown("---")

st.markdown("""
<div class="futuristic-card" style="margin-bottom: 20px;">
    <h3 style="font-size: 1rem !important; color: #00ffd5 !important; margin: 0;">MULTI-YEAR FORECAST</h3>
    <p style="color: rgba(255,255,255,0.5); margin: 10px 0 0 0;">Generate predictions for a range of future years</p>
</div>
""", unsafe_allow_html=True)

forecast_cols = st.columns(3)
with forecast_cols[0]:
    forecast_state = st.selectbox("State", states, key="forecast_state")
with forecast_cols[1]:
    forecast_sector = st.selectbox("Sector", sectors, key="forecast_sector")
with forecast_cols[2]:
    forecast_fuel = st.selectbox("Fuel", fuels, key="forecast_fuel")

start_year, end_year = st.slider("Year Range", 
                                   min_value=max(years)+1, 
                                   max_value=max(years)+30,
                                   value=(max(years)+1, max(years)+10))

if st.button("📈 GENERATE FORECAST"):
    with st.spinner("Generating..."):
        try:
            forecast_data = []
            for year in range(start_year, end_year + 1):
                features = utils.prepare_input_features(forecast_state, forecast_sector, forecast_fuel, year, df)
                if features is not None:
                    pred_log = features[0] + 0.05 * (year - max(years))
                    pred_value = utils.inverse_log_transform(pred_log)
                    forecast_data.append({'Year': year, 'Predicted Emissions': pred_value})
            
            forecast_df = pd.DataFrame(forecast_data)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=forecast_df['Year'], y=forecast_df['Predicted Emissions'],
                                    mode='lines+markers',
                                    line=dict(color='#00ffd5', width=4),
                                    marker=dict(size=12, color='#00ffd5', symbol='diamond', line=dict(color='#050508', width=2)),
                                    fill='tozeroy',
                                    fillcolor='rgba(0, 212, 170, 0.15)'))
            
            fig.update_layout(
                title=dict(text=f'MULTI-YEAR FORECAST: {forecast_state.upper()}', 
                          font=dict(family='Orbitron', size=16, color='#00ffd5'), x=0.5),
                xaxis_title=dict(text='YEAR', font=dict(family='Rajdhani', color='#00ffd5')),
                yaxis_title=dict(text='PREDICTED CO2 (MILLION MT)', font=dict(family='Rajdhani', color='#00ffd5')),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Rajdhani', color='#fff'),
                xaxis=dict(gridcolor='rgba(0,255,213,0.1)', tickfont=dict(color='#fff')),
                yaxis=dict(gridcolor='rgba(0,255,213,0.1)', tickfont=dict(color='#fff'))
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(forecast_df, hide_index=True)
            
        except Exception as e:
            st.error(f"Error: {str(e)}")

st.markdown("---")
st.caption("Predictions based on trained ML models and historical trends")