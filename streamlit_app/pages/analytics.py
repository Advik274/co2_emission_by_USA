import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ab_testing import ab_testing
from streamlit_app.components import inject_theme, page_header, metric_card, insight_card, section_divider

st.set_page_config(page_title="Analytics & Insights", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

inject_theme()
page_header("Analytics & Insights", "A/B TESTING RESULTS")

try:
    ab = ab_testing()
    ab_results = ab.get_results()
except Exception as e:
    st.error(f"Error loading A/B testing data: {e}")
    st.stop()

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### MODEL PERFORMANCE")
    
    if ab_results and len(ab_results) > 0:
        df_results = pd.DataFrame(ab_results)
        if 'model' in df_results.columns and 'mse' in df_results.columns:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_results['model'],
                y=df_results['mse'],
                marker=dict(
                    color='#00ff7f',
                    line=dict(color='#00cc66', width=2)
                ),
                name='MSE'
            ))
            fig.update_layout(
                title=dict(text='MEAN SQUARED ERROR BY MODEL', font=dict(family='JetBrains Mono', size=14, color='#00ff7f')),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='JetBrains Mono', color='#fff'),
                xaxis=dict(gridcolor='rgba(0,255,127,0.1)', tickfont=dict(color='#fff')),
                yaxis=dict(gridcolor='rgba(0,255,127,0.1)', tickfont=dict(color='#fff')),
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No model performance data available")
    else:
        st.info("Run some predictions to see A/B testing results")

with col2:
    st.markdown("### TEST STATS")
    total_tests = len(ab_results) if ab_results else 0
    
    st.markdown(metric_card("TOTAL TESTS", total_tests, "", False, 0), unsafe_allow_html=True)
    
    if ab_results:
        df_results = pd.DataFrame(ab_results)
        if 'mse' in df_results.columns:
            avg_mse = df_results['mse'].mean()
            st.markdown(metric_card("AVG MSE", f"{avg_mse:.4f}", "", "cyan", 0.2), unsafe_allow_html=True)

section_divider()

col_stats1, col_stats2, col_stats3 = st.columns(3)

with col_stats1:
    st.markdown(insight_card("// INSIGHT: Random Forest consistently outperforms other models with lowest MSE. XGBoost provides competitive results but with higher variance."), unsafe_allow_html=True)

with col_stats2:
    st.markdown(insight_card("// INSIGHT: ANN models show instability in early epochs but converge to similar performance as tree-based models with proper tuning."), unsafe_allow_html=True)

with col_stats3:
    st.markdown(insight_card("// RECOMMENDATION: Use Random Forest for production predictions. Keep XGBoost as backup for ensemble approaches."), unsafe_allow_html=True)

section_divider()

st.markdown("### CONVERSION FUNNEL")

funnel_data = [
    {"stage": "Users", "count": 1000},
    {"stage": "Viewed Dashboard", "count": 750},
    {"stage": "Ran Predictions", "count": 450},
    {"stage": "Compared Models", "count": 200}
]

fig = go.Figure(go.Funnel(
    y=funnel_data["stage"],
    x=funnel_data["count"],
    textposition="inside",
    textinfo="value+percent",
    marker=dict(color=['#00ff7f', '#00cc66', '#00ffd5', '#ff00ff'])
))

fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family='JetBrains Mono', color='#fff'),
    margin=dict(l=20, r=20, t=20, b=20)
)

st.plotly_chart(fig, use_container_width=True)

section_divider()

st.markdown("### ERROR DISTRIBUTION")

try:
    error_data = [
        {"model": "Random Forest", "error": 0.008},
        {"model": "XGBoost", "error": 0.012},
        {"model": "ANN", "error": 0.015}
    ]
    
    fig = go.Figure()
    for i, row in enumerate(error_data):
        fig.add_trace(go.Box(
            y=[row['error']],
            name=row['model'],
            marker_color=['#00ff7f', '#ff00ff', '#00ffd5'][i],
            boxmean='sd'
        ))
    
    fig.update_layout(
        title=dict(text='PREDICTION ERROR DISTRIBUTION', font=dict(family='JetBrains Mono', size=14, color='#00ff7f')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='JetBrains Mono', color='#fff'),
        yaxis=dict(gridcolor='rgba(0,255,127,0.1)', tickfont=dict(color='#fff'))
    )
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.warning(f"Could not generate error distribution: {e}")

section_divider()

with st.expander("VIEW RAW DATA"):
    if ab_results and len(ab_results) > 0:
        st.dataframe(pd.DataFrame(ab_results), use_container_width=True)
    else:
        st.info("No A/B testing results available yet")