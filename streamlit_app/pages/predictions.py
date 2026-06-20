import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import importlib
if 'src.ab_testing' in sys.modules:
    importlib.reload(sys.modules['src.ab_testing'])
if 'src.utils' in sys.modules:
    importlib.reload(sys.modules['src.utils'])
from src import utils
from src.ab_testing import ab_testing
from streamlit_app.components import inject_theme, page_header, metric_card, story_card, model_status_banner, section_divider, sidebar_navigation

st.set_page_config(
    page_title="Future Predictions | CO2 USA",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_theme()
page_header("Future Predictions", "MACHINE LEARNING CARBON FORECASTING")

# ── Check which models are available ──────────────────────────────────────────
model_avail = utils.check_models_available()

# ── Data Loading ──────────────────────────────────────────────────────────────
try:
    df = utils.filter_state_level_data(utils.load_raw_data())
    states, sectors, fuels, years = utils.get_unique_values()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# ── A/B Variant Assignment ────────────────────────────────────────────────────
variant = ab_testing.assign_variant('prediction_ui')

# ── Sidebar Controls ──────────────────────────────────────────────────────────
with st.sidebar:
    sidebar_navigation("Predictions")

    st.markdown("---")
    st.markdown("""
    <p style="font-family:'JetBrains Mono',monospace; font-size:0.72rem;
              letter-spacing:2px; color:#00ff7f; text-transform:uppercase; margin-bottom:8px;">
        // Prediction Inputs
    </p>
    """, unsafe_allow_html=True)

    input_state  = st.selectbox("🌎 State",  states)
    input_sector = st.selectbox("🏭 Sector", sectors)
    input_fuel   = st.selectbox("⛽ Fuel",   fuels)
    input_year   = st.number_input("📅 Forecast Year", min_value=int(min(years)), max_value=2050, value=2030)

    model_options = ["Random Forest", "XGBoost", "ANN (Simple)", "ANN (Deep)"]
    model_type    = st.selectbox("🤖 Model", model_options)

    st.markdown("---")
    ab_testing.track_event('prediction_ui', 'page_view', {'variant': variant})

# ── Model Status Banner ───────────────────────────────────────────────────────
model_status_banner(model_avail)

# ── Layout: Input summary + Generate ─────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown("""
    <p style="font-family:'JetBrains Mono',monospace; font-size:0.75rem; letter-spacing:2px;
              color:#00ff7f; text-transform:uppercase; margin-bottom:14px;">// Your Query</p>
    """, unsafe_allow_html=True)

    query_html = f"""
    <div class="futuristic-card" style="margin-bottom:16px;">
        <table style="width:100%; border-collapse:collapse; font-family:'JetBrains Mono',monospace;">
            <tr><td style="color:rgba(255,255,255,0.4);font-size:0.7rem;letter-spacing:2px;
                           padding:6px 0;">STATE</td>
                <td style="color:#e8e8f0;font-size:0.9rem;padding:6px 0;"><b>{input_state}</b></td></tr>
            <tr><td style="color:rgba(255,255,255,0.4);font-size:0.7rem;letter-spacing:2px;
                           padding:6px 0;">SECTOR</td>
                <td style="color:#e8e8f0;font-size:0.9rem;padding:6px 0;"><b>{input_sector}</b></td></tr>
            <tr><td style="color:rgba(255,255,255,0.4);font-size:0.7rem;letter-spacing:2px;
                           padding:6px 0;">FUEL</td>
                <td style="color:#e8e8f0;font-size:0.9rem;padding:6px 0;"><b>{input_fuel}</b></td></tr>
            <tr><td style="color:rgba(255,255,255,0.4);font-size:0.7rem;letter-spacing:2px;
                           padding:6px 0;">YEAR</td>
                <td style="color:#00ff7f;font-size:1.1rem;padding:6px 0;font-weight:700;">{input_year}</td></tr>
            <tr><td style="color:rgba(255,255,255,0.4);font-size:0.7rem;letter-spacing:2px;
                           padding:6px 0;">MODEL</td>
                <td style="color:#00ffd5;font-size:0.9rem;padding:6px 0;"><b>{model_type}</b></td></tr>
        </table>
    </div>
    """
    st.markdown(query_html, unsafe_allow_html=True)

    ab_testing.track_event('prediction_ui', 'generate_click', {'model': model_type, 'variant': variant})
    generate_btn = st.button("⚡ GENERATE PREDICTION", use_container_width=True)

with col_right:
    st.markdown(story_card(
        "🔮", "HOW IT WORKS",
        "Select a US state, emission sector, fuel type, and a target year. "
        "The model uses <b>historical patterns and engineered lag features</b> to forecast "
        "the CO₂ output for that combination. "
        "When Random Forest or XGBoost model files aren't available locally (they require Git LFS pull), "
        "the app falls back to a <b>trend-based regression</b> using the last decade of data. "
        "ANN models are available from local .keras files."
    ), unsafe_allow_html=True)

    # Historical chart preview (always visible)
    hist_data = df[
        (df['state-name'] == input_state) &
        (df['sector-name'] == input_sector) &
        (df['fuel-name'] == input_fuel)
    ].sort_values('period')

    if len(hist_data) > 0:
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Scatter(
            x=hist_data['period'], y=hist_data['value'],
            mode='lines+markers', name='Historical',
            line=dict(color='#00ff7f', width=2),
            marker=dict(size=5, color='#00ff7f'),
            fill='tozeroy', fillcolor='rgba(0,255,127,0.06)',
            hovertemplate='<b>%{x}</b>: %{y:,.3f} M MT<extra></extra>'
        ))
        fig_hist.update_layout(
            title=dict(text='HISTORICAL DATA PREVIEW', font=dict(family='Orbitron', size=11, color='#00ff7f'), x=0.5),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='#fff'),
            xaxis=dict(gridcolor='rgba(0,255,127,0.07)', tickfont=dict(color='#aaa')),
            yaxis=dict(gridcolor='rgba(0,255,127,0.07)', tickfont=dict(color='#aaa'), title='M MT'),
            showlegend=False, height=240, margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("No historical data found for this combination")

section_divider()

# ── Run Prediction ─────────────────────────────────────────────────────────────
if generate_btn:
    with st.spinner("Computing forecast..."):
        try:
            # --- Feature prep ---
            features = utils.prepare_input_features(input_state, input_sector, input_fuel, int(input_year), df)

            if features is None:
                st.error("No historical data available for this state/sector/fuel combination.")
                st.stop()

            prediction_val   = None
            conf_low         = None
            conf_high        = None
            model_used       = "Trend-Based Estimate"

            # ── Try ML models ─────────────────────────────────────────────
            if "ANN" in model_type:
                ann_name = "deeper_ann" if "Deep" in model_type else "simple_ann"
                ann_model, ann_err = utils.load_ann_model_safe(ann_name)
                if ann_model is not None:
                    feat_2d = features[:2].reshape(1, -1)   # ANN trained on 2 features
                    pred_log = float(ann_model.predict(feat_2d, verbose=0)[0][0])
                    prediction_val = utils.inverse_log_transform(pred_log)
                    model_used = model_type
                    conf_spread = 0.12 + 0.01 * max(0, int(input_year) - int(max(years)))
                    conf_low  = prediction_val * (1 - conf_spread)
                    conf_high = prediction_val * (1 + conf_spread)
                    ab_testing.track_event('prediction_ui', 'prediction_made', {'model': ann_name})
                else:
                    st.warning(f"ANN: {ann_err} — falling back to trend estimate")

            elif "Random Forest" in model_type:
                rf_model, rf_err = utils.load_model_safe('Random Forest')
                if rf_model is not None:
                    pred_log = float(rf_model.predict([features])[0])
                    prediction_val = utils.inverse_log_transform(pred_log)
                    model_used = "Random Forest"
                    conf_spread = 0.08
                    conf_low  = prediction_val * (1 - conf_spread)
                    conf_high = prediction_val * (1 + conf_spread)
                    ab_testing.track_event('prediction_ui', 'prediction_made', {'model': 'RF'})
                else:
                    st.warning(f"RF: {rf_err}")

            elif "XGBoost" in model_type:
                xgb_model, xgb_err = utils.load_model_safe('XGBoost')
                if xgb_model is not None:
                    pred_log = float(xgb_model.predict([features])[0])
                    prediction_val = utils.inverse_log_transform(pred_log)
                    model_used = "XGBoost"
                    conf_spread = 0.10
                    conf_low  = prediction_val * (1 - conf_spread)
                    conf_high = prediction_val * (1 + conf_spread)
                    ab_testing.track_event('prediction_ui', 'prediction_made', {'model': 'XGBoost'})
                else:
                    st.warning(f"XGBoost: {xgb_err}")

            # ── Trend fallback ────────────────────────────────────────────
            if prediction_val is None:
                prediction_val, conf_low, conf_high = utils.trend_predict(
                    input_state, input_sector, input_fuel, int(input_year), df
                )
                model_used = "Trend-Based Estimate"
                if prediction_val is None:
                    st.error("Could not compute prediction — no historical data found.")
                    st.stop()

            # ── Get last historical value for context ─────────────────────
            hist = df[
                (df['state-name'] == input_state) &
                (df['sector-name'] == input_sector) &
                (df['fuel-name'] == input_fuel)
            ].sort_values('period')

            last_hist_val = float(hist.iloc[-1]['value']) if len(hist) > 0 else None
            last_hist_yr  = int(hist.iloc[-1]['period'])  if len(hist) > 0 else None
            delta_pct = ((prediction_val - last_hist_val) / last_hist_val * 100) if last_hist_val else None

            def display_emission(value):
                if value is None:
                    return "N/A"
                return "&lt;0.001" if 0 <= value < 0.001 else f"{value:,.3f}"

            # ── Display prediction result ─────────────────────────────────
            direction = ""
            if delta_pct is not None:
                direction = "📉 DECLINE" if delta_pct < 0 else "📈 INCREASE"

            conf_html = ""
            if conf_low is not None and conf_high is not None:
                conf_html = (
                    '<div class="confidence-band">'
                    '<div class="confidence-label">ESTIMATED RANGE</div>'
                    f'<div class="confidence-value">{display_emission(conf_low)} - {display_emission(conf_high)} M MT CO2</div>'
                    '</div>'
                )
            delta_html = ""
            if delta_pct is not None and last_hist_yr is not None:
                clr = "#ff5555" if delta_pct > 0 else "#00ff7f"
                delta_html = f"""
                <p style="margin:10px 0 0; font-family:'JetBrains Mono',monospace; font-size:0.85rem;
                           color:{clr}; letter-spacing:1px;">
                    {direction} &nbsp;·&nbsp; {delta_pct:+.1f}% vs. {last_hist_yr}
                </p>
                """

            st.markdown(
                f"""
                <div class="prediction-box">
                    <p style="font-family:'JetBrains Mono',monospace; font-size:0.7rem; letter-spacing:3px;
                              color:rgba(255,255,255,0.35); margin:0 0 12px 0;">
                        {model_used.upper()} · {input_state.upper()} · {input_sector.upper()} · {input_fuel.upper()} · {input_year}
                    </p>
                    <div class="prediction-value">{display_emission(prediction_val)}</div>
                    <div class="prediction-unit">MILLION METRIC TONS CO2 FOR THIS STATE / SECTOR / FUEL</div>
                    {delta_html}
                    {conf_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

            section_divider()

            # ── Storytelling Narrative ─────────────────────────────────────
            if delta_pct is not None:
                if delta_pct < -20:
                    narrative = (f"This forecast suggests a <b>significant reduction</b> in {input_state}'s "
                                 f"{input_sector.lower().replace(' carbon dioxide emissions', '')} emissions "
                                 f"from {input_fuel.lower()} — driven by efficiency gains and clean energy transition. "
                                 "If achieved, this would represent meaningful progress toward decarbonization targets.")
                elif delta_pct < 0:
                    narrative = (f"A <b>modest decline</b> is projected for {input_state}'s {input_fuel.lower()} "
                                 "emissions in this sector. The trend reflects gradual energy efficiency improvements "
                                 "and fuel switching, though the pace needs to accelerate to meet climate goals.")
                elif delta_pct < 15:
                    narrative = (f"Emissions in this category for {input_state} are projected to remain roughly stable. "
                                 "This sector may be resistant to rapid decarbonization without major policy intervention.")
                else:
                    narrative = (f"This projection shows a <b>significant increase</b> from current levels. "
                                 f"Without intervention, {input_state}'s {input_fuel.lower()} consumption in this sector "
                                 "would represent a growing share of the state's carbon footprint.")

                st.markdown(story_card("📊", "WHAT THIS MEANS", narrative), unsafe_allow_html=True)

            # ── Multi-year Forecast Chart ──────────────────────────────────
            if last_hist_yr is not None:
                st.markdown("### FORECAST TRAJECTORY")
                future_years = list(range(last_hist_yr + 1, int(input_year) + 1))

                if future_years:
                    # Interpolate using trend_predict for smooth trajectory
                    forecast_vals, lo_vals, hi_vals = [], [], []
                    for fy in future_years:
                        fv, fl, fh = utils.trend_predict(input_state, input_sector, input_fuel, fy, df)
                        forecast_vals.append(fv)
                        lo_vals.append(fl)
                        hi_vals.append(fh)

                    # Override the final year with the ML prediction
                    if forecast_vals:
                        forecast_vals[-1] = prediction_val
                        if conf_low:  lo_vals[-1] = conf_low
                        if conf_high: hi_vals[-1] = conf_high

                    hist_yrs  = list(hist['period'].astype(int))
                    hist_vals = list(hist['value'].astype(float))

                    fig = go.Figure()

                    # Confidence band
                    fig.add_trace(go.Scatter(
                        x=future_years + future_years[::-1],
                        y=hi_vals + lo_vals[::-1],
                        fill='toself', fillcolor='rgba(0,255,127,0.07)',
                        line_color='rgba(0,0,0,0)', showlegend=False, hoverinfo='skip', name='CI'
                    ))

                    # Historical
                    fig.add_trace(go.Scatter(
                        x=hist_yrs, y=hist_vals, mode='lines+markers',
                        name='Historical',
                        line=dict(color='#00ff7f', width=2),
                        marker=dict(size=5, color='#00ff7f'),
                        hovertemplate='<b>%{x}</b>: %{y:,.3f} M MT<extra></extra>'
                    ))

                    # Forecast
                    fig.add_trace(go.Scatter(
                        x=future_years, y=forecast_vals, mode='lines+markers',
                        name='Forecast',
                        line=dict(color='#ff00ff', width=2, dash='dash'),
                        marker=dict(size=7, symbol='circle-open', color='#ff00ff',
                                    line=dict(color='#ff00ff', width=2)),
                        hovertemplate='<b>%{x} (Forecast)</b>: %{y:,.3f} M MT<extra></extra>'
                    ))

                    # Final point highlight
                    fig.add_trace(go.Scatter(
                        x=[int(input_year)], y=[prediction_val],
                        mode='markers+text', name=f'{model_used} Prediction',
                        marker=dict(size=14, color='#ff00ff',
                                    line=dict(color='#050508', width=2),
                                    symbol='star'),
                        text=[f'  {prediction_val:,.2f}'], textposition='middle right',
                        textfont=dict(family='JetBrains Mono', color='#ff00ff', size=11),
                        hovertemplate=f'<b>{input_year} ({model_used})</b>: {prediction_val:,.3f} M MT<extra></extra>'
                    ))

                    # Dividing line at present
                    fig.add_vline(x=last_hist_yr, line_dash='dot',
                                  line_color='rgba(255,255,255,0.2)', line_width=1.5)
                    fig.add_annotation(x=last_hist_yr, y=0, yref='paper', yanchor='bottom',
                                       text="↑ FORECAST START", showarrow=False,
                                       font=dict(family='JetBrains Mono', size=9, color='rgba(255,255,255,0.35)'))

                    fig.update_layout(
                        title=dict(text=f'CO₂ EMISSION FORECAST — {input_state} · {input_year}',
                                   font=dict(family='Orbitron', size=13, color='#00ff7f'), x=0.5),
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family='Inter', color='#fff'),
                        xaxis=dict(gridcolor='rgba(0,255,127,0.07)', tickfont=dict(color='#aaa'),
                                   title='YEAR', tickformat='d'),
                        yaxis=dict(gridcolor='rgba(0,255,127,0.07)', tickfont=dict(color='#aaa'),
                                   title='MILLION METRIC TONS CO₂'),
                        legend=dict(font=dict(family='JetBrains Mono', color='#aaa', size=11)),
                        hovermode='x unified', height=420, margin=dict(l=10, r=10, t=50, b=10)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown(story_card(
                        "📉", "READING THE FORECAST",
                        "The <b style='color:#ff00ff'>pink dashed line</b> shows the model's projected trajectory. "
                        "The <b style='color:rgba(0,255,127,0.7)'>green shaded band</b> represents the 95% confidence "
                        "interval — wider bands indicate higher uncertainty further into the future. "
                        f"The <b>⭐ star</b> marks the final prediction from <b>{model_used}</b>."
                    ), unsafe_allow_html=True)

            # ── Similar states comparison ──────────────────────────────────
            section_divider()
            st.markdown("### HOW DOES THIS COMPARE?")

            compare_states = st.multiselect("Compare with states:", states, default=states[:3])
            if compare_states:
                fig_cmp = go.Figure()
                cmp_colors = ['#00ff7f', '#ff00ff', '#00ffd5', '#ffaa00', '#00aaff']
                for i, s in enumerate(compare_states[:5]):
                    sd = df[
                        (df['state-name'] == s) &
                        (df['sector-name'] == input_sector) &
                        (df['fuel-name'] == input_fuel)
                    ].sort_values('period')
                    if len(sd) > 0:
                        fig_cmp.add_trace(go.Scatter(
                            x=sd['period'], y=sd['value'], mode='lines',
                            name=s, line=dict(color=cmp_colors[i % 5], width=2),
                            hovertemplate=f'<b>{s}</b> %{{x}}: %{{y:,.3f}} M MT<extra></extra>'
                        ))
                if input_state not in compare_states:
                    sd = df[
                        (df['state-name'] == input_state) &
                        (df['sector-name'] == input_sector) &
                        (df['fuel-name'] == input_fuel)
                    ].sort_values('period')
                    if len(sd) > 0:
                        fig_cmp.add_trace(go.Scatter(
                            x=sd['period'], y=sd['value'], mode='lines',
                            name=f"{input_state} (selected)",
                            line=dict(color='#fff', width=2.5, dash='dot'),
                        ))

                fig_cmp.update_layout(
                    title=dict(text='STATE COMPARISON — SAME SECTOR & FUEL',
                               font=dict(family='Orbitron', size=12, color='#00ff7f'), x=0.5),
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family='Inter', color='#fff'),
                    xaxis=dict(gridcolor='rgba(0,255,127,0.07)', tickfont=dict(color='#aaa')),
                    yaxis=dict(gridcolor='rgba(0,255,127,0.07)', tickfont=dict(color='#aaa'), title='M MT'),
                    legend=dict(font=dict(family='JetBrains Mono', color='#aaa', size=11)),
                    height=340, margin=dict(l=10, r=10, t=50, b=10)
                )
                st.plotly_chart(fig_cmp, use_container_width=True)

        except Exception as err:
            st.error(f"Error during prediction: {err}")
            import traceback
            with st.expander("Error details"):
                st.code(traceback.format_exc())

else:
    # Guide when no prediction yet
    st.markdown("""
    <div style="text-align:center; padding:60px 20px; opacity:0.5;">
        <p style="font-family:'JetBrains Mono',monospace; font-size:2rem; margin:0;">🔮</p>
        <p style="font-family:'JetBrains Mono',monospace; font-size:0.8rem; letter-spacing:3px;
                  color:#00ff7f; text-transform:uppercase; margin-top:16px;">
            Configure your parameters above and hit Generate Prediction
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<p style="text-align:center; color:rgba(255,255,255,0.18); font-family:'JetBrains Mono',monospace;
          font-size:0.68rem; letter-spacing:2px;">
    VARIANT {v} · A/B EXPERIMENT: prediction_ui
</p>
""".format(v=variant), unsafe_allow_html=True)
