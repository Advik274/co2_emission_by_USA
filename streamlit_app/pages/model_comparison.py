import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import utils

st.set_page_config(page_title="Model Comparison", page_icon="📊")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

:root {
    --primary: #00ffd5;
    --secondary: #ff00aa;
    --bg-dark: #050508;
}

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
    width: 400px;
    height: 400px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255, 0, 170, 0.06) 0%, transparent 70%);
    bottom: -100px;
    left: -100px;
    animation: orbFloat 25s ease-in-out infinite reverse;
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

h1 { font-size: 2.2rem !important; }

.futuristic-card {
    background: linear-gradient(135deg, rgba(20, 20, 35, 0.9) 0%, rgba(10, 10, 20, 0.95) 100%) !important;
    border: 1px solid rgba(0, 255, 213, 0.2) !important;
    border-radius: 20px !important;
    padding: 30px !important;
    transition: all 0.4s ease !important;
}

.futuristic-card:hover {
    transform: translateY(-5px) !important;
    border-color: #00ffd5 !important;
    box-shadow: 0 15px 50px rgba(0, 255, 213, 0.15) !important;
}

.best-model {
    border: 2px solid #00ffd5 !important;
    box-shadow: 0 0 50px rgba(0, 255, 213, 0.3), inset 0 0 30px rgba(0, 255, 213, 0.05) !important;
}

.metric-badge {
    display: inline-block;
    padding: 10px 18px;
    border-radius: 12px;
    background: rgba(0, 255, 213, 0.15);
    border: 1px solid rgba(0, 255, 213, 0.4);
    font-family: 'Orbitron', sans-serif;
    font-size: 0.8rem;
    color: #00ffd5;
    margin: 5px;
}

.stSelectbox > div > div:first-child {
    background: rgba(15, 15, 25, 0.95) !important;
    border: 1px solid rgba(0, 255, 213, 0.3) !important;
    border-radius: 12px !important;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(15, 15, 25, 0.9) !important;
    border: 1px solid rgba(0, 255, 213, 0.15) !important;
    border-radius: 12px 12px 0 0 !important;
    color: rgba(255,255,255,0.6) !important;
    font-family: 'Orbitron', sans-serif !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(180deg, rgba(0, 255, 213, 0.15) 0%, rgba(15, 15, 25, 0.95) 100%) !important;
    border-color: #00ffd5 !important;
    color: #00ffd5 !important;
}
</style>

<div class="bg-grid"></div>
<div class="glow-orb"></div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; padding: 40px 20px 30px;">
    <h1>Model Performance</h1>
    <p style="color: rgba(255,255,255,0.4); font-size: 1rem; letter-spacing: 4px; margin-top: 10px;">
        TRAINED ML MODELS COMPARISON
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

metrics = utils.get_model_metrics()
ann_models = utils.get_ann_model_info()

st.markdown("### PERFORMANCE METRICS")

selected_model = st.selectbox("SELECT MODEL", 
                             list(metrics.keys()) + ann_models)

if selected_model in metrics:
    model_data = metrics[selected_model]
    is_best = model_data.get('R2', 0) > 0.98
    
    st.markdown(f"""
    <div class="futuristic-card {'best-model' if is_best else ''}" style="margin: 20px 0;">
        <h3 style="color: #00ffd5 !important; margin: 0 0 20px 0; font-size: 1.2rem !important;">
            {selected_model} {'🏆 BEST' if is_best else ''}
        </h3>
        <div style="display: flex; flex-wrap: wrap; gap: 10px; margin: 20px 0;">
            <span class="metric-badge">MSE: {model_data.get('MSE', 'N/A')}</span>
            <span class="metric-badge">R²: {model_data.get('R2', 'N/A')}</span>
            <span class="metric-badge">MSE (Log): {model_data.get('MSE_log', 'N/A')}</span>
            <span class="metric-badge">R² (Log): {model_data.get('R2_log', 'N/A')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="futuristic-card" style="margin: 20px 0;">
        <h3 style="color: #ff00aa !important; margin: 0 0 15px 0;">{selected_model}</h3>
        <p style="color: #888;">Neural network for predictions</p>
        <p style="color: #00ffd5; margin-top: 10px;">Architecture: Deep Learning (TensorFlow)</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.markdown("### COMPARISON CHARTS")

comparison_data = []
for model_name, data in metrics.items():
    comparison_data.append({
        'Model': model_name,
        'MSE (Original)': data.get('MSE'),
        'R² (Original)': data.get('R2'),
        'MSE (Log)': data.get('MSE_log'),
        'R² (Log)': data.get('R2_log')
    })

comparison_df = pd.DataFrame(comparison_data)

tab1, tab2 = st.tabs(["R² SCORE COMPARISON", "MSE COMPARISON"])

with tab1:
    colors = ['#00ffd5' if r2 > 0.98 else '#4ecdc4' for r2 in comparison_df['R² (Original)']]
    fig_r2 = go.Figure()
    fig_r2.add_trace(go.Bar(
        name='R² (Original Scale)',
        x=comparison_df['Model'],
        y=comparison_df['R² (Original)'],
        marker_color=colors,
        text=[f"{r:.4f}" for r in comparison_df['R² (Original)']],
        textposition='auto'
    ))
    fig_r2.add_trace(go.Bar(
        name='R² (Log Scale)',
        x=comparison_df['Model'],
        y=comparison_df['R² (Log)'],
        marker_color='#ff00aa'
    ))
    fig_r2.update_layout(
        title=dict(text='R² SCORE (HIGHER = BETTER)', font=dict(family='Orbitron', size=16, color='#00ffd5'), x=0.5),
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Rajdhani', color='#fff'),
        xaxis=dict(gridcolor='rgba(0,255,213,0.1)', tickfont=dict(color='#fff')),
        yaxis=dict(gridcolor='rgba(0,255,213,0.1)', tickfont=dict(color='#fff'), range=[0, 1.1]),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#fff'))
    )
    st.plotly_chart(fig_r2, use_container_width=True)

with tab2:
    fig_mse = go.Figure()
    fig_mse.add_trace(go.Bar(
        name='MSE (Original)',
        x=comparison_df['Model'],
        y=comparison_df['MSE (Original)'],
        marker_color='#ff00aa'
    ))
    fig_mse.add_trace(go.Bar(
        name='MSE (Log)',
        x=comparison_df['Model'],
        y=comparison_df['MSE (Log)'],
        marker_color='#ffa502'
    ))
    fig_mse.update_layout(
        title=dict(text='MSE (LOWER = BETTER)', font=dict(family='Orbitron', size=16, color='#ff00aa'), x=0.5),
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Rajdhani', color='#fff'),
        xaxis=dict(gridcolor='rgba(0,255,213,0.1)', tickfont=dict(color='#fff')),
        yaxis=dict(gridcolor='rgba(0,255,213,0.1)', tickfont=dict(color='#fff')),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#fff'))
    )
    st.plotly_chart(fig_mse, use_container_width=True)

st.markdown("---")

st.markdown("### RECOMMENDATIONS")

col_rec1, col_rec2 = st.columns(2)

with col_rec1:
    st.markdown("""
    <div class="futuristic-card">
        <h4 style="color: #00ffd5 !important; margin: 0 0 15px 0;">BEST BY METRIC</h4>
        <table style="width: 100%; color: #fff; font-family: 'Rajdhani', sans-serif;">
            <tr><td style="padding: 10px;">🥇 R² (Original)</td><td style="padding: 10px; color: #00ffd5;">Random Forest: 0.9917</td></tr>
            <tr><td style="padding: 10px;">🥇 MSE (Original)</td><td style="padding: 10px; color: #00ffd5;">Random Forest: 367.51</td></tr>
            <tr><td style="padding: 10px;">🥇 R² (Log)</td><td style="padding: 10px; color: #00ffd5;">Random Forest: 0.9831</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

with col_rec2:
    st.markdown("""
    <div class="futuristic-card">
        <h4 style="color: #ff00aa !important; margin: 0 0 15px 0;">USE CASE</h4>
        <table style="width: 100%; color: #fff; font-family: 'Rajdhani', sans-serif;">
            <tr><td style="padding: 10px;">Production</td><td style="padding: 10px; color: #00ffd5;">Random Forest</td><td style="padding: 10px; color: #888;">Best accuracy</td></tr>
            <tr><td style="padding: 10px;">Speed</td><td style="padding: 10px; color: #00ffd5;">XGBoost</td><td style="padding: 10px; color: #888;">Fast inference</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.markdown("### FEATURE COMPARISON")

feature_df = pd.DataFrame({
    'Model': ['Random Forest', 'XGBoost', 'ANN'],
    'Type': ['Ensemble', 'Boosting', 'Neural Net'],
    'Speed': ['Fast', 'Fast', 'Medium'],
    'Accuracy': ['Highest', 'High', 'High'],
    'Interpretability': ['High', 'Medium', 'Low']
})
st.dataframe(feature_df, hide_index=True, use_container_width=True)

st.markdown("---")
st.caption("Metrics based on research paper evaluation")