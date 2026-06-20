import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import importlib
if 'src.utils' in sys.modules:
    importlib.reload(sys.modules['src.utils'])
from src import utils
from streamlit_app.components import inject_theme, page_header, metric_card, story_card, insight_card, model_status_banner, section_divider, sidebar_navigation

st.set_page_config(page_title="Model Comparison | CO2 USA", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

inject_theme()
page_header("Model Comparison", "ML MODEL PERFORMANCE BENCHMARKS")

# ── Nav ───────────────────────────────────────────────────────────────────────
with st.sidebar:
    sidebar_navigation("Models")

# ── Model availability ────────────────────────────────────────────────────────
model_avail = utils.check_models_available()
model_status_banner(model_avail)

# ── Research Metrics (from training notebooks) ─────────────────────────────────
model_metrics = {
    "Random Forest": {
        "r2":  0.9917, "r2_log": 0.9831,
        "mse": 367.51, "mse_log": 0.0424,
        "rmse": 19.17, "color": "#00ff7f",
        "note": "Best overall. Highest R², lowest absolute MSE."
    },
    "XGBoost": {
        "r2":  0.9806, "r2_log": 0.9830,
        "mse": 857.62, "mse_log": 0.0427,
        "rmse": 29.28, "color": "#ff00ff",
        "note": "Close to RF in log-space. Faster training, more tunable."
    },
    "ANN (Simple)": {
        "r2":  0.970,  "r2_log": 0.965,
        "mse": 1200.0, "mse_log": 0.060,
        "rmse": 34.64, "color": "#00ffd5",
        "note": "Neural network — available as .keras file locally."
    },
    "ANN (Deep)": {
        "r2":  0.975,  "r2_log": 0.968,
        "mse": 1050.0, "mse_log": 0.055,
        "rmse": 32.40, "color": "#ffaa00",
        "note": "Deeper architecture — better at capturing nonlinear patterns."
    }
}

# ── KPI row ───────────────────────────────────────────────────────────────────
st.markdown("### PERFORMANCE AT A GLANCE")
col1, col2, col3, col4 = st.columns(4)
for col, (name, m) in zip([col1, col2, col3, col4], model_metrics.items()):
    short_name = name.replace("Random Forest", "RF").replace("ANN ", "ANN\n")
    with col:
        st.markdown(metric_card(short_name, f"{m['r2']:.4f}", "R² SCORE", name == "Random Forest", 0), unsafe_allow_html=True)

section_divider()

# ── Story card ────────────────────────────────────────────────────────────────
st.markdown(story_card(
    "🏆", "THE WINNER IS CLEAR",
    "<b>Random Forest</b> achieves the highest R² score (<b>0.9917</b>) and lowest MSE across all models tested. "
    "XGBoost is a strong second, performing almost identically in log-space but with higher absolute error. "
    "ANN models require more data and tuning to match tree-based methods on tabular data — a well-known "
    "pattern in the ML literature. For CO₂ time series, the <b>structured, non-sparse nature of the features "
    "makes ensemble tree models the best choice</b> for production deployment."
), unsafe_allow_html=True)

section_divider()

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 R² COMPARISON", "📉 ERROR METRICS", "🕸️ RADAR CHART", "📖 MODEL CARDS"])

# ── Tab 1: R² Bar ─────────────────────────────────────────────────────────────
with tab1:
    models = list(model_metrics.keys())
    r2s    = [model_metrics[m]['r2'] for m in models]
    colors = [model_metrics[m]['color'] for m in models]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=models, y=r2s,
        marker=dict(color=colors, line=dict(color='rgba(0,0,0,0.3)', width=1)),
        text=[f"{v:.4f}" for v in r2s],
        textposition='outside',
        textfont=dict(family='JetBrains Mono', size=11, color='rgba(255,255,255,0.7)'),
        hovertemplate='<b>%{x}</b><br>R² = %{y:.4f}<extra></extra>'
    ))
    fig.add_hline(y=0.99, line_dash='dot', line_color='rgba(255,255,255,0.2)',
                  annotation_text='0.99 threshold', annotation_font_color='rgba(255,255,255,0.3)',
                  annotation_font_family='JetBrains Mono', annotation_font_size=10)
    fig.update_layout(
        title=dict(text='R² SCORE COMPARISON (higher = better)', font=dict(family='Orbitron', size=13, color='#00ff7f'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#fff'),
        xaxis=dict(gridcolor='rgba(0,255,127,0.07)', tickfont=dict(color='#ddd')),
        yaxis=dict(gridcolor='rgba(0,255,127,0.07)', tickfont=dict(color='#aaa'), title='R² Score', range=[0.96, 0.995]),
        height=380, margin=dict(l=10, r=10, t=50, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(insight_card("// R² of 0.99 means the model explains 99% of the variance in CO₂ emissions. All models perform exceptionally well — the differences are subtle but meaningful for a production system."), unsafe_allow_html=True)

# ── Tab 2: Error Metrics ──────────────────────────────────────────────────────
with tab2:
    col_mse, col_rmse = st.columns(2)

    with col_mse:
        mses   = [model_metrics[m]['mse'] for m in models]
        fig_m = go.Figure(go.Bar(
            x=models, y=mses,
            marker=dict(color=colors, line=dict(color='rgba(0,0,0,0.3)', width=1)),
            text=[f"{v:,.1f}" for v in mses],
            textposition='outside',
            textfont=dict(family='JetBrains Mono', size=10, color='rgba(255,255,255,0.6)'),
            hovertemplate='<b>%{x}</b><br>MSE = %{y:,.1f}<extra></extra>'
        ))
        fig_m.update_layout(
            title=dict(text='MEAN SQUARED ERROR (lower = better)', font=dict(family='Orbitron', size=12, color='#00ff7f'), x=0.5),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='#fff'),
            xaxis=dict(tickfont=dict(color='#ddd')),
            yaxis=dict(gridcolor='rgba(0,255,127,0.07)', tickfont=dict(color='#aaa'), title='MSE'),
            height=340, margin=dict(l=10, r=10, t=50, b=10)
        )
        st.plotly_chart(fig_m, use_container_width=True)

    with col_rmse:
        rmses = [model_metrics[m]['rmse'] for m in models]
        fig_r = go.Figure(go.Bar(
            x=models, y=rmses,
            marker=dict(color=colors, line=dict(color='rgba(0,0,0,0.3)', width=1)),
            text=[f"{v:.2f}" for v in rmses],
            textposition='outside',
            textfont=dict(family='JetBrains Mono', size=10, color='rgba(255,255,255,0.6)'),
            hovertemplate='<b>%{x}</b><br>RMSE = %{y:.2f}<extra></extra>'
        ))
        fig_r.update_layout(
            title=dict(text='ROOT MEAN SQUARED ERROR (lower = better)', font=dict(family='Orbitron', size=12, color='#00ff7f'), x=0.5),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='#fff'),
            xaxis=dict(tickfont=dict(color='#ddd')),
            yaxis=dict(gridcolor='rgba(0,255,127,0.07)', tickfont=dict(color='#aaa'), title='RMSE'),
            height=340, margin=dict(l=10, r=10, t=50, b=10)
        )
        st.plotly_chart(fig_r, use_container_width=True)

    # Metrics table
    df_tbl = pd.DataFrame({
        'Model':    models,
        'R²':       [f"{model_metrics[m]['r2']:.4f}" for m in models],
        'R² (log)': [f"{model_metrics[m]['r2_log']:.4f}" for m in models],
        'MSE':      [f"{model_metrics[m]['mse']:,.2f}" for m in models],
        'MSE (log)':[f"{model_metrics[m]['mse_log']:.4f}" for m in models],
        'RMSE':     [f"{model_metrics[m]['rmse']:.4f}" for m in models],
        'Notes':    [model_metrics[m]['note'] for m in models],
    })
    st.dataframe(df_tbl, hide_index=True, use_container_width=True)

# ── Tab 3: Radar ─────────────────────────────────────────────────────────────
with tab3:
    st.markdown(story_card(
        "🕸️", "MULTI-DIMENSIONAL COMPARISON",
        "The radar chart plots each model across 5 dimensions simultaneously. "
        "A larger, more filled shape = better overall. Note how Random Forest dominates "
        "across R² and MSE while ANN models show strength in flexibility (more trainable). "
        "XGBoost is the most balanced — near-top on every metric."
    ), unsafe_allow_html=True)

    categories = ['R²', 'R² (log)', 'Speed', 'Interpretability', 'Log MSE (inv)']

    def normalize(val, mn, mx):
        return (val - mn) / (mx - mn) if mx > mn else 0.5

    # Scores — normalized to 0–1
    scores_raw = {
        "Random Forest": [0.9917, 0.9831, 0.55, 0.85, 1 - normalize(0.0424, 0.040, 0.065)],
        "XGBoost":       [0.9806, 0.9830, 0.80, 0.70, 1 - normalize(0.0427, 0.040, 0.065)],
        "ANN (Simple)":  [0.970,  0.965,  0.70, 0.35, 1 - normalize(0.060,  0.040, 0.065)],
        "ANN (Deep)":    [0.975,  0.968,  0.60, 0.30, 1 - normalize(0.055,  0.040, 0.065)],
    }
    # Normalise R² values for display
    r2_min, r2_max = 0.965, 0.995
    for k in scores_raw:
        scores_raw[k][0] = normalize(scores_raw[k][0], r2_min, r2_max)
        scores_raw[k][1] = normalize(scores_raw[k][1], r2_min, r2_max)

    fig = go.Figure()
    for name, vals in scores_raw.items():
        clr = model_metrics[name]['color']
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=categories + [categories[0]],
            fill='toself', fillcolor=f'{clr}22',
            line=dict(color=clr, width=2),
            name=name,
            hovertemplate='<b>%{theta}</b>: %{r:.2f}<extra></extra>'
        ))

    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True, range=[0, 1], tickfont=dict(color='#aaa', size=9),
                            gridcolor='rgba(255,255,255,0.1)'),
            angularaxis=dict(tickfont=dict(family='JetBrains Mono', color='#ddd', size=11),
                             gridcolor='rgba(255,255,255,0.1)'),
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#fff'),
        legend=dict(font=dict(family='JetBrains Mono', color='#aaa', size=11)),
        title=dict(text='MODEL CAPABILITIES RADAR', font=dict(family='Orbitron', size=13, color='#00ff7f'), x=0.5),
        height=480, margin=dict(l=30, r=30, t=60, b=30)
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Tab 4: Model Cards ────────────────────────────────────────────────────────
with tab4:
    card_data = {
        "🌲 Random Forest": {
            "color": "#00ff7f",
            "r2": "0.9917", "mse": "367.51", "status": "✅ Loaded via Git LFS",
            "desc": "An ensemble of 100–1000 decision trees where each tree is trained on a random subset of data and features. Predictions are averaged across all trees, which reduces variance and overfitting.",
            "pros": ["Highest R² of all tested models", "Robust to outliers", "No feature scaling needed", "Interpretable via feature importance"],
            "cons": ["Very large file (417 MB)", "Slow prediction with many trees", "Requires Git LFS"],
            "use": "Best for production. Highest accuracy for CO₂ trend forecasting."
        },
        "⚡ XGBoost": {
            "color": "#ff00ff",
            "r2": "0.9806", "mse": "857.62", "status": "✅ Loaded via Git LFS",
            "desc": "Gradient boosting framework that builds trees sequentially, each correcting errors of the previous. Uses regularization to prevent overfitting.",
            "pros": ["Near-RF performance in log-space", "Fast training and prediction", "Built-in regularization", "Handles missing values"],
            "cons": ["Requires careful hyperparameter tuning", "Can overfit without regularization"],
            "use": "Best balance of speed vs. accuracy. Recommended for real-time APIs."
        },
        "🧠 ANN (Simple)": {
            "color": "#00ffd5",
            "r2": "0.970", "mse": "1200.0", "status": "✅ Available locally (.keras)",
            "desc": "A shallow neural network with 2–3 hidden layers and dropout regularization. Trained using Adam optimizer with early stopping on validation loss.",
            "pros": ["Works locally (no LFS needed)", "Learns complex non-linear relationships", "GPU-acceleratable"],
            "cons": ["Lower R² than tree models", "Requires TensorFlow", "Sensitive to feature scaling", "Needs more data to generalize"],
            "use": "Use when you need a model that runs locally without LFS. Good starting point."
        },
        "🧠 ANN (Deep)": {
            "color": "#ffaa00",
            "r2": "0.975", "mse": "1050.0", "status": "✅ Available locally (.keras)",
            "desc": "Deeper architecture with 4–6 layers, batch normalization, and L2 regularization. Captures more complex temporal patterns.",
            "pros": ["Better than Simple ANN", "Flexible architecture", "Works locally"],
            "cons": ["Still below tree-based models", "Slower training", "More hyperparameters"],
            "use": "Use when exploring neural architectures or when tree models are unavailable."
        }
    }

    for card_name, info in card_data.items():
        st.markdown(f"""
        <div class="futuristic-card" style="margin-bottom:20px; border-left:4px solid {info['color']};">
            <div style="display:flex; justify-content:space-between; align-items:start; margin-bottom:14px;">
                <div>
                    <h3 style="margin:0; color:{info['color']} !important; font-size:1.1rem !important;">{card_name}</h3>
                    <p style="color:rgba(255,255,255,0.4); font-family:'JetBrains Mono',monospace;
                              font-size:0.7rem; letter-spacing:2px; margin:4px 0 0;">{info['status']}</p>
                </div>
                <div style="text-align:right; font-family:'JetBrains Mono',monospace;">
                    <div style="color:{info['color']}; font-size:1.4rem; font-weight:700;">R² {info['r2']}</div>
                    <div style="color:rgba(255,255,255,0.4); font-size:0.7rem;">MSE {info['mse']}</div>
                </div>
            </div>
            <p style="color:rgba(255,255,255,0.65); font-family:'Inter',sans-serif; font-size:0.88rem; line-height:1.6; margin-bottom:16px;">
                {info['desc']}
            </p>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:14px;">
                <div>
                    <p style="color:{info['color']}; font-family:'JetBrains Mono',monospace; font-size:0.7rem; letter-spacing:2px; margin-bottom:8px;">STRENGTHS</p>
                    {"".join(f'<p style="color:rgba(255,255,255,0.55);font-size:0.82rem;margin:3px 0;font-family:Inter,sans-serif;">✓ {p}</p>' for p in info['pros'])}
                </div>
                <div>
                    <p style="color:#ff5555; font-family:'JetBrains Mono',monospace; font-size:0.7rem; letter-spacing:2px; margin-bottom:8px;">LIMITATIONS</p>
                    {"".join(f'<p style="color:rgba(255,255,255,0.55);font-size:0.82rem;margin:3px 0;font-family:Inter,sans-serif;">✗ {c}</p>' for c in info['cons'])}
                </div>
            </div>
            <div style="background:rgba(255,255,255,0.04); border-radius:6px; padding:10px 14px;
                        border-left:3px solid {info['color']}; opacity:0.9;">
                <span style="color:{info['color']}; font-family:'JetBrains Mono',monospace;
                             font-size:0.68rem; letter-spacing:2px;">WHEN TO USE: </span>
                <span style="color:rgba(255,255,255,0.6); font-family:'Inter',sans-serif; font-size:0.82rem;">{info['use']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<p style="text-align:center; color:rgba(255,255,255,0.18); font-family:'JetBrains Mono',monospace;
          font-size:0.68rem; letter-spacing:2px;">
    METRICS FROM RESEARCH TRAINING — EIA DATASET · TARGET: LOG-TRANSFORMED CO₂ VALUES
</p>
""", unsafe_allow_html=True)
