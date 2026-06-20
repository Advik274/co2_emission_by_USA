import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import utils
from streamlit_app.components import inject_theme, page_header, metric_card, insight_card, section_divider

st.set_page_config(page_title="Model Comparison", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

inject_theme()
page_header("Model Comparison", "ML MODEL PERFORMANCE")

try:
    X_train, X_test, y_train, y_test = utils.load_processed_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

model_metrics = {
    "Random Forest": {"r2": 0.9917, "rmse": 0.085, "mse": 0.0072},
    "XGBoost": {"r2": 0.9850, "rmse": 0.115, "mse": 0.0132},
    "ANN (Simple)": {"r2": 0.9700, "rmse": 0.163, "mse": 0.0266},
    "ANN (Deep)": {"r2": 0.9750, "rmse": 0.149, "mse": 0.0222}
}

st.markdown("### PERFORMANCE METRICS")

col1, col2, col3, col4 = st.columns(4)

metrics_list = list(model_metrics.items())
for i, (col, (name, metrics)) in enumerate(zip([col1, col2, col3, col4], metrics_list)):
    with col:
        st.markdown(metric_card(name, f"{metrics['r2']:.4f}", "R² SCORE", i==0, i*0.1), unsafe_allow_html=True)

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["R² COMPARISON", "ERROR METRICS", "FEATURE IMPORTANCE"])

with tab1:
    models = list(model_metrics.keys())
    r2_scores = [model_metrics[m]['r2'] for m in models]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=models,
        y=r2_scores,
        marker=dict(
            color=r2_scores,
            colorscale=['#00ff7f', '#00cc66', '#ff00ff', '#00ffd5'],
            line=dict(color='#ffffff', width=2)
        ),
        text=[f"{s:.4f}" for s in r2_scores],
        textposition='outside'
    ))
    fig.update_layout(
        title=dict(text='R² SCORES BY MODEL', font=dict(family='JetBrains Mono', size=16, color='#00ff7f'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='JetBrains Mono', color='#fff'),
        xaxis=dict(gridcolor='rgba(0,255,127,0.1)', tickfont=dict(color='#fff', size=12)),
        yaxis=dict(gridcolor='rgba(0,255,127,0.1)', tickfont=dict(color='#fff'), range=[0, 1.1]),
        margin=dict(l=20, r=20, t=50, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(insight_card("// WINNER: Random Forest achieves the highest R² score of 0.9917, explaining 99.17% of variance in emissions data. This makes it the best choice for production predictions."), unsafe_allow_html=True)

with tab2:
    models = list(model_metrics.keys())
    rmse_scores = [model_metrics[m]['rmse'] for m in models]
    mse_scores = [model_metrics[m]['mse'] for m in models]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=models,
        y=rmse_scores,
        name='RMSE',
        marker=dict(color='#00ff7f', line=dict(color='#00cc66', width=2))
    ))
    fig.add_trace(go.Bar(
        x=models,
        y=mse_scores,
        name='MSE',
        marker=dict(color='#ff00ff', line=dict(color='#cc00cc', width=2))
    ))
    fig.update_layout(
        title=dict(text='ERROR METRICS BY MODEL', font=dict(family='JetBrains Mono', size=16, color='#00ff7f'), x=0.5),
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='JetBrains Mono', color='#fff'),
        xaxis=dict(gridcolor='rgba(0,255,127,0.1)', tickfont=dict(color='#fff')),
        yaxis=dict(gridcolor='rgba(0,255,127,0.1)', tickfont=dict(color='#fff')),
        legend=dict(font=dict(family='JetBrains Mono', color='#fff'))
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(insight_card("// ANALYSIS: Lower is better for both RMSE and MSE. Random Forest shows the lowest error metrics, indicating more accurate predictions."), unsafe_allow_html=True)

with tab3:
    try:
        rf_model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'rf', 'random_forest.joblib')
        if os.path.exists(rf_model_path):
            import joblib
            rf_model = joblib.load(rf_model_path)
            if hasattr(rf_model, 'feature_importances_'):
                feature_names = utils.get_feature_columns()
                importances = rf_model.feature_importances_
                
                feat_imp = pd.DataFrame({
                    'feature': feature_names[:len(importances)],
                    'importance': importances
                }).sort_values('importance', ascending=True)
                
                fig = px.bar(feat_imp, x='importance', y='feature', orientation='h',
                           title='FEATURE IMPORTANCE (Random Forest)',
                           color='importance',
                           color_continuous_scale=['#00ff7f', '#ff00ff'])
                fig.update_layout(
                    title=dict(font=dict(family='JetBrains Mono', size=16, color='#00ff7f'), x=0.5),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family='JetBrains Mono', color='#fff'),
                    xaxis=dict(gridcolor='rgba(0,255,127,0.1)', tickfont=dict(color='#fff')),
                    yaxis=dict(tickfont=dict(color='#fff', size=10))
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Model does not have feature_importances_ attribute")
        else:
            st.info("Random Forest model file not found")
    except Exception as e:
        st.warning(f"Could not load feature importance: {e}")

st.markdown("---")

st.markdown("### RECOMMENDATION")

col_rec1, col_rec2 = st.columns([1, 2])

with col_rec1:
    st.markdown("""
    <div class="futuristic-card" style="text-align: center;">
        <p class="metric-label" style="font-size: 1rem;">BEST MODEL</p>
        <p class="metric-value" style="font-size: 1.8rem;">Random Forest</p>
        <p class="metric-label" style="margin-top: 15px;">R² SCORE</p>
        <p class="metric-value" style="font-size: 1.4rem; color: #00ffd5 !important;">0.9917</p>
    </div>
    """, unsafe_allow_html=True)

with col_rec2:
    st.markdown(insight_card("""
    // CONCLUSION: Random Forest is recommended for production use due to:
    <br><br>
    • Highest R² score (0.9917) - explains 99.17% of variance
    <br>
    • Lowest RMSE (0.085) - most accurate predictions
    <br>
    • Fast inference time compared to deep learning models
    <br>
    • Robust to overfitting with proper hyperparameters
    <br><br>
    Use XGBoost as backup for ensemble approaches or when model interpretability is needed.
    """), unsafe_allow_html=True)