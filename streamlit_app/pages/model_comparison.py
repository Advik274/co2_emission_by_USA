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
    .stApp { background-color: #0e1117; }
    h1, h2, h3 { color: #00d4aa !important; }
    .model-card {
        background: linear-gradient(135deg, #1e1e2f 0%, #2d2d44 100%);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #00d4aa33;
    }
    .best-model {
        border: 2px solid #00d4aa;
        box-shadow: 0 0 20px rgba(0, 212, 170, 0.3);
    }
    .metric-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 5px;
        background: #00d4aa;
        color: #000;
        font-weight: bold;
        margin: 2px;
    }
    .rank-1 { background: #ffd700 !important; }
    .rank-2 { background: #c0c0c0 !important; }
    .rank-3 { background: #cd7f32 !important; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Model Performance Comparison")
st.markdown("Compare the performance of different trained machine learning models")

metrics = utils.get_model_metrics()
ann_models = utils.get_ann_model_info()

st.markdown("### 🎯 Performance Metrics")

selected_model = st.selectbox("Select Model to View Details", 
                             list(metrics.keys()) + ann_models,
                             key='model_select_compare')

if selected_model in metrics:
    model_data = metrics[selected_model]
    is_best = model_data.get('R2', 0) > 0.98
    st.markdown(f"""
    <div class="model-card {'best-model' if is_best else ''}">
        <h3>{selected_model} {'🏆 Best' if is_best else ''}</h3>
        <p><strong>MSE (Original Scale):</strong> {model_data.get('MSE', 'N/A')}</p>
        <p><strong>R² (Original Scale):</strong> {model_data.get('R2', 'N/A')}</p>
        <p><strong>MSE (Log Scale):</strong> {model_data.get('MSE_log', 'N/A')}</p>
        <p><strong>R² (Log Scale):</strong> {model_data.get('R2_log', 'N/A')}</p>
        {f"<p><em>{model_data.get('note', '')}</em></p>" if 'note' in model_data else ""}
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="model-card">
        <h3>{selected_model}</h3>
        <p><em>Neural network model available for predictions</em></p>
        <p>Architecture: Deep Learning (TensorFlow/Keras)</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.markdown("### 📈 Model Comparison Charts")

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

tab1, tab2 = st.tabs(["R² Score Comparison", "MSE Comparison"])

with tab1:
    fig_r2 = go.Figure()
    colors = ['#00d4aa' if r2 > 0.98 else '#4ecdc4' for r2 in comparison_df['R² (Original)']]
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
        marker_color='#ff6b6b',
        text=[f"{r:.4f}" for r in comparison_df['R² (Log)']],
        textposition='auto'
    ))

    fig_r2.update_layout(
        title='R² Score Comparison (Higher is Better)',
        xaxis_title='Model',
        yaxis_title='R² Score',
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#fff',
        legend=dict(bgcolor='rgba(0,0,0,0)'),
        yaxis=dict(range=[0, 1.1])
    )
    st.plotly_chart(fig_r2, use_container_width=True)

with tab2:
    fig_mse = go.Figure()
    fig_mse.add_trace(go.Bar(
        name='MSE (Original Scale)',
        x=comparison_df['Model'],
        y=comparison_df['MSE (Original)'],
        marker_color='#ff6b6b',
        text=[f"{m:.1f}" for m in comparison_df['MSE (Original)']],
        textposition='auto'
    ))
    fig_mse.add_trace(go.Bar(
        name='MSE (Log Scale)',
        x=comparison_df['Model'],
        y=comparison_df['MSE (Log)'],
        marker_color='#ffa502',
        text=[f"{m:.4f}" for m in comparison_df['MSE (Log)']],
        textposition='auto'
    ))

    fig_mse.update_layout(
        title='MSE Comparison (Lower is Better)',
        xaxis_title='Model',
        yaxis_title='Mean Squared Error',
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#fff',
        legend=dict(bgcolor='rgba(0,0,0,0)')
    )
    st.plotly_chart(fig_mse, use_container_width=True)

st.markdown("---")

st.markdown("### 🏆 Model Recommendations")

col_rec1, col_rec2 = st.columns(2)

with col_rec1:
    st.markdown("#### Best By Metric")
    st.markdown("""
    | Metric | Best Model | Score |
    |--------|------------|-------|
    | R² (Original) | Random Forest | 0.9917 |
    | MSE (Original) | Random Forest | 367.51 |
    | R² (Log) | Random Forest | 0.9831 |
    | MSE (Log) | Random Forest | 0.0424 |
    """)

with col_rec2:
    st.markdown("#### Use Case Recommendations")
    st.markdown("""
    | Use Case | Model | Reason |
    |----------|-------|--------|
    | Production | Random Forest | Best accuracy |
    | Fast inference | XGBoost | Good speed |
    | Deep learning | Simple ANN | Lightweight |
    | Complex patterns | Deeper ANN | More capacity |
    """)

st.markdown("---")

st.markdown("### 📊 Model Feature Comparison")

feature_data = {
    'Model': ['Random Forest', 'XGBoost', 'ANN Variants'],
    'Type': ['Ensemble (Tree)', 'Gradient Boosting', 'Neural Network'],
    'Training Time': ['Fast', 'Medium', 'Slow'],
    'Inference Speed': ['Fast', 'Fast', 'Medium'],
    'Memory': ['Medium', 'Medium', 'High'],
    'Interpretability': ['High', 'Medium', 'Low']
}

feature_df = pd.DataFrame(feature_data)
st.dataframe(feature_df, hide_index=True, use_container_width=True)

st.markdown("---")
st.markdown("*Metrics based on research paper evaluation results*")

with st.expander("📈 Model Performance Over Time"):
    st.markdown("### Training Metrics")
    
    model_names = list(metrics.keys())
    metric_options = st.selectbox("Select Metric", ['MSE', 'R²'])
    
    if metric_options == 'R²':
        fig_perf = go.Figure()
        for i, (name, data) in enumerate(metrics.items()):
            r2_log = data.get('R2_log', 0)
            r2_orig = data.get('R2', 0)
            fig_perf.add_trace(go.Scatter(
                x=['Log Scale', 'Original Scale'],
                y=[r2_log, r2_orig],
                mode='lines+markers',
                name=name,
                line=dict(width=3)
            ))
        
        fig_perf.update_layout(
            title='R² Performance Comparison',
            xaxis_title='Scale',
            yaxis_title='R² Score',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#fff'
        )
        st.plotly_chart(fig_perf, use_container_width=True)
    else:
        fig_perf = go.Figure()
        for i, (name, data) in enumerate(metrics.items()):
            mse_log = data.get('MSE_log', 0)
            mse_orig = data.get('MSE', 0)
            fig_perf.add_trace(go.Scatter(
                x=['Log Scale', 'Original Scale'],
                y=[mse_log, mse_orig],
                mode='lines+markers',
                name=name,
                line=dict(width=3)
            ))
        
        fig_perf.update_layout(
            title='MSE Performance Comparison',
            xaxis_title='Scale',
            yaxis_title='MSE',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#fff'
        )
        st.plotly_chart(fig_perf, use_container_width=True)