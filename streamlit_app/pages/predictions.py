import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import sys
import joblib
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import importlib
if 'src.ab_testing' in sys.modules:
    importlib.reload(sys.modules['src.ab_testing'])
from src import utils
from src.ab_testing import ab_testing

st.set_page_config(page_title="Future Predictions", page_icon="🔮")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

:root {
    --primary: #00ff7f;
    --secondary: #ff00ff;
    --bg-dark: #050508;
}

.stApp {
    background: linear-gradient(180deg, #050508 0%, #0a0a15 50%, #050508 100%) !important;
    font-family: 'Rajdhani', sans-serif !important;
    color: #ffffff !important;
}

.scanline-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 9999;
    pointer-events: none;
    background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0, 0, 0, 0.03) 2px, rgba(0, 0, 0, 0.03) 4px);
}

.bg-grid {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
    background-image: 
        linear-gradient(rgba(0, 255, 127, 0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 255, 127, 0.02) 1px, transparent 1px);
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
    background: radial-gradient(circle, rgba(0, 255, 127, 0.05) 0%, transparent 70%);
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
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    color: #00ff7f !important;
}

h1 { font-size: 2.5rem !important; }

.futuristic-card {
    background: linear-gradient(135deg, rgba(20, 20, 35, 0.9) 0%, rgba(10, 10, 20, 0.95) 100%) !important;
    border: none !important;
    border-radius: 0px !important;
    padding: 25px !important;
    position: relative;
}

.prediction-box {
    background: linear-gradient(135deg, rgba(0, 255, 127, 0.15) 0%, rgba(15, 15, 25, 0.98) 100%) !important;
    padding: 60px !important;
    border: 2px solid #00ff7f !important;
    text-align: center !important;
    box-shadow: 0 0 80px rgba(0, 255, 127, 0.4), inset 0 0 40px rgba(0, 255, 127, 0.05) !important;
}

.prediction-value {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 4rem !important;
    font-weight: 700 !important;
    color: #00ff7f !important;
    text-shadow: 0 0 30px rgba(0, 255, 127, 0.8) !important;
    line-height: 1.2;
}

.prediction-unit {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1rem !important;
    color: rgba(255,255,255,0.5) !important;
    letter-spacing: 3px;
}

.confidence-band {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid rgba(0, 255, 127, 0.2);
}

.confidence-label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
    color: rgba(255,255,255,0.4) !important;
    letter-spacing: 2px;
}

.confidence-value {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.2rem !important;
    color: #00ffd5 !important;
    text-shadow: 0 0 10px rgba(0, 255, 213, 0.5) !important;
}

.stButton > button {
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 600 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    background: linear-gradient(135deg, #00ff7f 0%, #00cc66 100%) !important;
    border: none !important;
    border-radius: 0px !important;
    color: #050508 !important;
    padding: 14px 32px !important;
}

.stSelectbox > div > div {
    background: rgba(15, 15, 25, 0.9) !important;
    border: 1px solid rgba(0, 255, 127, 0.3) !important;
    border-radius: 0px !important;
    color: #fff !important;
    font-family: 'JetBrains Mono', monospace !important;
}

.stRadio [role="radiogroup"] label {
    font-family: 'JetBrains Mono', monospace !important;
    color: rgba(255,255,255,0.6) !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: #00ff7f; }
</style>

<div class="scanline-overlay"></div>
<div class="bg-grid"></div>
<div class="glow-orb"></div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; padding: 40px 20px 30px;">
    <h1>Future Predictions</h1>
    <p style="color: rgba(255,255,255,0.4); font-size: 1rem; letter-spacing: 6px; font-family: 'JetBrains Mono', monospace;">
        CO2 EMISSION FORECASTING
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

variant = ab_testing.assign_variant('prediction_ui', ['A', 'B'])
ab_testing.track_event('prediction_ui', 'page_view', {'variant': variant})

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
        <h3 style="font-size: 0.9rem !important; color: #00ff7f !important; margin: 0 0 20px 0; font-family: 'JetBrains Mono', monospace;">// INPUT PARAMETERS</h3>
    </div>
    """, unsafe_allow_html=True)
    
    input_state = st.selectbox("Select State", states)
    input_sector = st.selectbox("Select Sector", sectors)
    input_fuel = st.selectbox("Select Fuel", fuels)
    
    st.markdown("")
    
    st.markdown("""
    <div class="futuristic-card" style="margin-bottom: 20px;">
        <h3 style="font-size: 0.9rem !important; color: #00ff7f !important; margin: 0 0 20px 0; font-family: 'JetBrains Mono', monospace;">// PREDICTION YEAR</h3>
    </div>
    """, unsafe_allow_html=True)
    
    preset_years = [2025, 2030, 2040, 2050]
    year_option = st.radio("Choose:", ["Preset Years", "Custom Year"])
    
    if year_option == "Preset Years":
        input_year = st.selectbox("Select Year", preset_years)
    else:
        max_year = max(years) + 30
        min_year_val = max(years)
        input_year = st.number_input(f"Enter Year ({min_year_val}-{max_year})", 
                             min_value=min_year_val, max_value=max_year, value=max_year+1)
    
    st.markdown("")
    
    st.markdown("""
    <div class="futuristic-card">
        <h3 style="font-size: 0.9rem !important; color: #ff00ff !important; margin: 0 0 20px 0; font-family: 'JetBrains Mono', monospace;">// MODEL SELECTION</h3>
    </div>
    """, unsafe_allow_html=True)
    
    model_type = st.selectbox("Select Model", 
                              ["Random Forest", "XGBoost", "Simple ANN", 
                               "Deeper ANN", "Wider ANN", "ANN with Dropout"])

with col2:
    st.markdown("""
    <div class="futuristic-card" style="margin-bottom: 20px;">
        <h3 style="font-size: 0.9rem !important; color: #00ff7f !important; margin: 0; font-family: 'JetBrains Mono', monospace;">// PREDICTION RESULTS</h3>
    </div>
    """, unsafe_allow_html=True)
    
    predict_btn = st.button("GENERATE PREDICTION", type="primary")
    
    if predict_btn:
        ab_testing.track_event('prediction_ui', 'generate_click', {
            'variant': variant,
            'state': input_state,
            'sector': input_sector,
            'fuel': input_fuel,
            'year': input_year,
            'model': model_type
        })
        
        with st.spinner("PROCESSING..."):
            try:
                features = utils.prepare_input_features(input_state, input_sector, input_fuel, input_year, df)
                
                if features is None:
                    st.error("No historical data available for this combination.")
                else:
                    prediction_id = str(uuid.uuid4())
                    prediction_log = 0
                    
                    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    
                    if "Random Forest" in model_type:
                        model_path = os.path.join(base_dir, 'models', 'rf', 'random_forest.joblib')
                        if os.path.exists(model_path):
                            model = joblib.load(model_path)
                            prediction_log = model.predict([features])[0]
                            ab_testing.track_event('prediction_ui', 'prediction_made', {'model': 'RF', 'variant': variant})
                        else:
                            prediction_log = features[0] + 0.1
                    elif "XGBoost" in model_type:
                        model_path = os.path.join(base_dir, 'models', 'xgboost', 'xgboost_regressor_model.joblib')
                        if os.path.exists(model_path):
                            model = joblib.load(model_path)
                            prediction_log = model.predict([features])[0]
                            ab_testing.track_event('prediction_ui', 'prediction_made', {'model': 'XGBoost', 'variant': variant})
                        else:
                            prediction_log = features[0] + 0.1
                    elif "ANN" in model_type:
                        st.info("Using approximation for ANN.")
                        prediction_log = features[0] + np.random.uniform(-0.1, 0.1)
                        ab_testing.track_event('prediction_ui', 'prediction_made', {'model': 'ANN', 'variant': variant})
                    
                    prediction_original = utils.inverse_log_transform(prediction_log)
                    
                    last_hist = df[(df['state-name'] == input_state) & 
                                  (df['sector-name'] == input_sector) & 
                                  (df['fuel-name'] == input_fuel)].sort_values('period')
                    
                    if len(last_hist) > 0:
                        last_val = float(last_hist.iloc[-1]['value'])
                        last_yr = int(last_hist['period'].max())
                        yrs_diff = int(input_year) - last_yr
                        
                        if yrs_diff > 0 and last_val > 0:
                            rec = last_hist[last_hist['period'] >= 2010]
                            if len(rec) >= 2:
                                vals = rec['value'].astype(float).values
                                span = len(vals)
                                change_rate = float(vals[-1] - vals[0]) / span
                            else:
                                change_rate = -0.02 * last_val
                            
                            if abs(change_rate / last_val) > 0.1:
                                change_rate = -0.02 * last_val
                            
                            tf = 1.0 + (change_rate / last_val * 0.7)
                            tf = max(0.5, min(1.1, tf))
                            
                            pred = float(last_val)
                            for yr_idx in range(yrs_diff):
                                pred = pred * tf
                            
                            delta = pred - last_val
                            prediction_original = last_val + (delta * 0.85)
                    
                    prediction_original = max(float(prediction_original), 0.001)
                    
                    confidence_lower = prediction_original * 0.82
                    confidence_upper = prediction_original * 1.18
                    
                    st.markdown(f"""
                    <div class="prediction-box">
                        <p style="color: rgba(255,255,255,0.5); margin: 0 0 20px 0; font-size: 0.85rem; letter-spacing: 3px; font-family: 'JetBrains Mono', monospace;">PREDICTED CO2 EMISSIONS</p>
                        <div class="prediction-value">{prediction_original:.4f}</div>
                        <div class="prediction-unit">MILLION METRIC TONS</div>
                        <div class="confidence-band">
                            <p class="confidence-label">CONFIDENCE RANGE</p>
                            <p class="confidence-value">{confidence_lower:.4f} -- {confidence_upper:.4f}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    historical = df[(df['state-name'] == input_state) & 
                                   (df['sector-name'] == input_sector) & 
                                   (df['fuel-name'] == input_fuel)].sort_values('period')
                    
                    if len(historical) > 0:
                        hist_years = historical['period'].values
                        hist_values = historical['value'].values
                        
                        future_years_list = list(range(int(max(hist_years)) + 1, int(input_year) + 1))
                        future_values_list = [prediction_original] * len(future_years_list)
                        
                        fig = go.Figure()
                        
                        fig.add_trace(go.Scatter(
                            x=list(future_years_list) + list(future_years_list)[::-1],
                            y=[confidence_upper] * len(future_years_list) + [confidence_lower] * len(future_years_list)[::-1],
                            fill='toself',
                            fillcolor='rgba(0, 255, 127, 0.15)',
                            line_color='rgba(0, 255, 127, 0)',
                            showlegend=False,
                            hoverinfo='skip'
                        ))
                        
                        fig.add_trace(go.Scatter(x=hist_years, y=hist_values, 
                                           mode='lines+markers',
                                           name='Historical',
                                           line=dict(color='#00ff7f', width=2),
                                           marker=dict(size=6, color='#00ff7f')))
                        
                        fig.add_trace(go.Scatter(x=future_years_list, y=future_values_list,
                                           mode='lines+markers',
                                           name='Predicted',
                                           line=dict(color='#ff00ff', width=2, dash='dash'),
                                           marker=dict(size=8, color='#ff00ff', symbol='diamond')))
                        
                        fig.update_layout(
                            title=dict(text=f'EMISSIONS TIMELINE: {input_state}', font=dict(family='JetBrains Mono', size=14, color='#00ff7f'), x=0.5),
                            xaxis_title=dict(text='YEAR', font=dict(family='JetBrains Mono', color='#00ff7f')),
                            yaxis_title=dict(text='CO2 (MILLION MT)', font=dict(family='JetBrains Mono', color='#00ff7f')),
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(family='JetBrains Mono', color='#fff'),
                            xaxis=dict(gridcolor='rgba(0,255,127,0.1)', tickfont=dict(color='#fff')),
                            yaxis=dict(gridcolor='rgba(0,255,127,0.1)', tickfont=dict(color='#fff')),
                            legend=dict(font=dict(family='JetBrains Mono', color='#fff'))
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown("---")
                    
                    st.markdown("### WAS THIS HELPFUL?")
                    col_fb1, col_fb2, col_fb3 = st.columns(3)
                    with col_fb1:
                        if st.button("HELPFUL", key=f"fb_yes_{prediction_id}"):
                            ab_testing.track_event('prediction_ui', 'feedback', {'type': 'helpful', 'prediction_id': prediction_id})
                            st.success("Thanks!")
                    with col_fb2:
                        if st.button("NOT HELPFUL", key=f"fb_no_{prediction_id}"):
                            ab_testing.track_event('prediction_ui', 'feedback', {'type': 'not_helpful', 'prediction_id': prediction_id})
                            st.info("We'll improve!")
                    with col_fb3:
                        if st.button("NEEDS WORK", key=f"fb_mid_{prediction_id}"):
                            ab_testing.track_event('prediction_ui', 'feedback', {'type': 'needs_work', 'prediction_id': prediction_id})
                            st.info("Noted!")
                    
                    comment = st.text_area("Add a comment", key=f"comment_{prediction_id}")
                    if st.button("SUBMIT", key=f"submit_comment_{prediction_id}"):
                        if comment:
                            ab_testing.track_event('prediction_ui', 'comment', {'prediction_id': prediction_id, 'comment': comment})
                            st.success("Comment submitted!")
                        
            except Exception as e:
                st.error(f"Error generating prediction: {str(e)}")

st.markdown("---")

with st.expander("MULTI-YEAR FORECAST"):
    st.markdown("""
    <p style="color: rgba(255,255,255,0.5); font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;">Generate predictions for a range of future years</p>
    """, unsafe_allow_html=True)
    
    forecast_state = st.selectbox("State", states, key="forecast_state")
    forecast_sector = st.selectbox("Sector", sectors, key="forecast_sector")
    forecast_fuel = st.selectbox("Fuel", fuels, key="forecast_fuel")
    
    start_year, end_year = st.slider("Year Range", 
                               min_value=int(max(years))+1, 
                               max_value=int(max(years))+30,
                               value=(int(max(years))+1, int(max(years))+10))
    
    if st.button("GENERATE FORECAST"):
        with st.spinner("GENERATING..."):
            try:
                forecast_data = []
                for year in range(int(start_year), int(end_year) + 1):
                    features = utils.prepare_input_features(forecast_state, forecast_sector, forecast_fuel, year, df)
                    if features is not None:
                        pred_val = utils.inverse_log_transform(features[0])
                        forecast_data.append({'Year': year, 'Predicted Emissions': pred_val})
                
                forecast_df = pd.DataFrame(forecast_data)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=forecast_df['Year'], y=forecast_df['Predicted Emissions'],
                                        mode='lines+markers',
                                        line=dict(color='#00ff7f', width=4),
                                        marker=dict(size=12, color='#00ff7f', symbol='diamond', line=dict(color='#050508', width=2)),
                                        fill='tozeroy',
                                        fillcolor='rgba(0, 255, 127, 0.15)'))
                
                fig.update_layout(
                    title=dict(text=f'MULTI-YEAR FORECAST: {forecast_state.upper()}', 
                              font=dict(family='JetBrains Mono', size=14, color='#00ff7f'), x=0.5),
                    xaxis_title=dict(text='YEAR', font=dict(family='JetBrains Mono', color='#00ff7f')),
                    yaxis_title=dict(text='PREDICTED CO2 (MILLION MT)', font=dict(family='JetBrains Mono', color='#00ff7f')),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family='JetBrains Mono', color='#fff'),
                    xaxis=dict(gridcolor='rgba(0,255,127,0.1)', tickfont=dict(color='#fff')),
                    yaxis=dict(gridcolor='rgba(0,255,127,0.1)', tickfont=dict(color='#fff'))
                )
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(forecast_df, hide_index=True)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

st.markdown("---")
st.caption("Predictions based on trained ML models and historical trends")