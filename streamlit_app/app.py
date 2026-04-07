import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import utils

st.set_page_config(
    page_title="CO2 Emissions | USA",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

:root {
    --primary: #00ffd5;
    --primary-dim: #00a896;
    --secondary: #ff00aa;
    --bg-dark: #050508;
    --bg-card: rgba(15, 15, 25, 0.95);
    --glow: 0 0 30px rgba(0, 255, 213, 0.4);
    --glow-pink: 0 0 30px rgba(255, 0, 170, 0.4);
}

* { box-sizing: border-box; }

.stApp {
    background: linear-gradient(180deg, #050508 0%, #0a0a15 50%, #050508 100%) !important;
    font-family: 'Rajdhani', sans-serif !important;
    color: #ffffff !important;
}

/* Background Effects */
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

.glow-orb-1 {
    position: fixed;
    width: 600px;
    height: 600px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0, 255, 213, 0.08) 0%, transparent 70%);
    top: -200px;
    right: -200px;
    animation: orbFloat 20s ease-in-out infinite;
    z-index: -1;
}

.glow-orb-2 {
    position: fixed;
    width: 500px;
    height: 500px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255, 0, 170, 0.06) 0%, transparent 70%);
    bottom: -150px;
    left: -150px;
    animation: orbFloat 25s ease-in-out infinite reverse;
    z-index: -1;
}

@keyframes orbFloat {
    0%, 100% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(30px, 30px) scale(1.1); }
}

/* Typography */
h1, h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
}

h1 {
    background: linear-gradient(90deg, #00ffd5, #00b8a9, #00ffd5);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 3s linear infinite;
    font-size: 2.8rem !important;
}

@keyframes shimmer {
    to { background-position: 200% center; }
}

/* Cards */
.futuristic-card {
    background: linear-gradient(135deg, rgba(20, 20, 35, 0.9) 0%, rgba(10, 10, 20, 0.95) 100%) !important;
    border: 1px solid rgba(0, 255, 213, 0.2) !important;
    border-radius: 20px !important;
    padding: 25px !important;
    backdrop-filter: blur(10px);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    position: relative;
    overflow: hidden;
}

.futuristic-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00ffd5, transparent);
    opacity: 0;
    transition: opacity 0.4s;
}

.futuristic-card:hover {
    transform: translateY(-8px) !important;
    border-color: #00ffd5 !important;
    box-shadow: 0 20px 60px rgba(0, 255, 213, 0.2), 0 0 40px rgba(0, 255, 213, 0.1) !important;
}

.futuristic-card:hover::before {
    opacity: 1;
}

/* Metrics */
.metric-value {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 2.2rem !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #00ffd5, #00b8a9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: none !important;
}

.metric-label {
    color: rgba(255, 255, 255, 0.5) !important;
    font-size: 0.85rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}

/* Buttons */
.stButton > button {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    background: linear-gradient(135deg, #00ffd5 0%, #00a896 100%) !important;
    border: none !important;
    border-radius: 30px !important;
    color: #050508 !important;
    padding: 14px 32px !important;
    transition: all 0.3s ease !important;
    position: relative !important;
    overflow: hidden !important;
}

.stButton > button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent);
    transition: left 0.5s;
}

.stButton > button:hover {
    transform: scale(1.03) !important;
    box-shadow: 0 10px 40px rgba(0, 255, 213, 0.4) !important;
}

.stButton > button:hover::before {
    left: 100%;
}

/* Select Boxes */
.stSelectbox > div > div:first-child {
    background: rgba(15, 15, 25, 0.95) !important;
    border: 1px solid rgba(0, 255, 213, 0.3) !important;
    border-radius: 12px !important;
    color: #fff !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    letter-spacing: 2px !important;
    background: rgba(15, 15, 25, 0.9) !important;
    border: 1px solid rgba(0, 255, 213, 0.15) !important;
    border-radius: 12px 12px 0 0 !important;
    padding: 14px 24px !important;
    color: rgba(255,255,255,0.6) !important;
    transition: all 0.3s ease !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #00ffd5 !important;
    border-color: rgba(0, 255, 213, 0.4) !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(180deg, rgba(0, 255, 213, 0.15) 0%, rgba(15, 15, 25, 0.95) 100%) !important;
    border-color: #00ffd5 !important;
    color: #00ffd5 !important;
    box-shadow: 0 -5px 30px rgba(0, 255, 213, 0.2) !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(8, 8, 15, 0.98) !important;
    border-right: 1px solid rgba(0, 255, 213, 0.1) !important;
}

/* Divider */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(0, 255, 213, 0.5), transparent) !important;
    margin: 40px 0 !important;
}

/* Progress */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #00ffd5, #00a896, #ff00aa) !important;
    border-radius: 10px !important;
}

/* Animations */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(40px); }
    to { opacity: 1; transform: translateY(0); }
}

.fade-in {
    animation: fadeInUp 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    opacity: 0;
}

.stagger-1 { animation-delay: 0.1s; }
.stagger-2 { animation-delay: 0.2s; }
.stagger-3 { animation-delay: 0.3s; }
.stagger-4 { animation-delay: 0.4s; }

/* Spinner */
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

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #050508; }
::-webkit-scrollbar-thumb { background: rgba(0, 255, 213, 0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0, 255, 213, 0.6); }
</style>

<div class="bg-grid"></div>
<div class="glow-orb-1"></div>
<div class="glow-orb-2"></div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; padding: 40px 20px 30px;">
    <h1>USA Carbon Emissions</h1>
    <p style="color: rgba(255,255,255,0.4); font-size: 1rem; letter-spacing: 6px; margin-top: 10px;">
        FUTURE CARBON EMISSION HORIZONS
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

try:
    df = utils.load_raw_data()
    states, sectors, fuels, years = utils.get_unique_values()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0 30px;">
        <h3 style="font-size: 1rem !important; color: #00ffd5 !important;">◈ NAVIGATION</h3>
    </div>
    """, unsafe_allow_html=True)
    
    nav_options = ["Dashboard", "Predictions", "Models", "Analytics"]
    selected_nav = st.radio("Go to", nav_options, label_visibility="collapsed")
    
    if selected_nav == "Predictions":
        st.switch_page("pages/predictions.py")
    elif selected_nav == "Models":
        st.switch_page("pages/model_comparison.py")
    elif selected_nav == "Analytics":
        st.switch_page("pages/analytics.py")
    
    st.markdown("---")
    
    st.markdown("### FILTERS")
    
    selected_state = st.selectbox("State", ["All"] + states)
    selected_sector = st.selectbox("Sector", ["All"] + sectors)
    selected_fuel = st.selectbox("Fuel", ["All"] + fuels)
    
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; padding: 15px; background: rgba(0,255,213,0.05); border-radius: 12px; border: 1px solid rgba(0,255,213,0.2);">
        <p style="margin:0; color: #00ffd5; font-size: 0.75rem; letter-spacing: 2px;">DATASET INFO</p>
    </div>
    <div style="padding: 15px; font-size: 0.9rem;">
        <p style="margin: 10px 0;"><span style="color: #00ffd5;">▸</span> Records: <span style="color: #fff;">{len(df):,}</span></p>
        <p style="margin: 10px 0;"><span style="color: #00ffd5;">▸</span> States: <span style="color: #fff;">{len(states)}</span></p>
        <p style="margin: 10px 0;"><span style="color: #00ffd5;">▸</span> Years: <span style="color: #fff;">{min(years)}-{max(years)}</span></p>
    </div>
    """, unsafe_allow_html=True)

if selected_state != "All":
    df = df[df['state-name'] == selected_state]
if selected_sector != "All":
    df = df[df['sector-name'] == selected_sector]
if selected_fuel != "All":
    df = df[df['fuel-name'] == selected_fuel]

st.markdown("### KEY METRICS")

col1, col2, col3, col4 = st.columns(4)

total_emissions = df['value'].sum()
avg_emissions = df['value'].mean()
max_emission = df['value'].max()
min_emission = df['value'].min()

with col1:
    st.markdown(f"""
    <div class="futuristic-card fade-in stagger-1">
        <p class="metric-label">Total Emissions</p>
        <p class="metric-value">{total_emissions:,.2f}</p>
        <p style="color: rgba(255,255,255,0.4); font-size: 0.75rem; margin-top: 10px;">MILLION METRIC TONS</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="futuristic-card fade-in stagger-2">
        <p class="metric-label">Average</p>
        <p class="metric-value">{avg_emissions:.3f}</p>
        <p style="color: rgba(255,255,255,0.4); font-size: 0.75rem; margin-top: 10px;">MILLION METRIC TONS</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="futuristic-card fade-in stagger-3">
        <p class="metric-label">Maximum</p>
        <p class="metric-value" style="background: linear-gradient(135deg, #ff00aa, #ff6b9d); -webkit-background-clip: text;">{max_emission:.3f}</p>
        <p style="color: rgba(255,255,255,0.4); font-size: 0.75rem; margin-top: 10px;">MILLION METRIC TONS</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="futuristic-card fade-in stagger-4">
        <p class="metric-label">Minimum</p>
        <p class="metric-value" style="background: linear-gradient(135deg, #4ecdc4, #45b7aa); -webkit-background-clip: text;">{min_emission:.3f}</p>
        <p style="color: rgba(255,255,255,0.4); font-size: 0.75rem; margin-top: 10px;">MILLION METRIC TONS</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["EMISSIONS TIMELINE", "BY SECTOR", "BY FUEL", "BY STATE"])

with tab1:
    yearly = df.groupby('period')['value'].sum().reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=yearly['period'], y=yearly['value'],
        mode='lines+markers',
        line=dict(color='#00ffd5', width=3, shape='spline'),
        marker=dict(size=8, color='#00ffd5', line=dict(color='#050508', width=2)),
        fill='tozeroy',
        fillcolor='rgba(0, 255, 213, 0.1)'
    ))
    fig.update_layout(
        title=dict(text='CO2 EMISSIONS OVER TIME', font=dict(family='Orbitron', size=18, color='#00ffd5'), x=0.5),
        xaxis_title=dict(text='YEAR', font=dict(family='Rajdhani', size=14, color='#00ffd5')),
        yaxis_title=dict(text='EMISSIONS (MILLION MT)', font=dict(family='Rajdhani', size=14, color='#00ffd5')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Rajdhani', color='#fff'),
        xaxis=dict(gridcolor='rgba(0,255,213,0.1)', tickfont=dict(color='#fff'), tickformat='d'),
        yaxis=dict(gridcolor='rgba(0,255,213,0.1)', tickfont=dict(color='#fff'))
    )
    st.plotly_chart(fig, use_container_width=True)
    
    col_trend1, col_trend2, col_trend3 = st.columns(3)
    with col_trend1:
        first_year = yearly.iloc[0]['value']
        last_year = yearly.iloc[-1]['value']
        change = ((last_year - first_year) / first_year) * 100
        st.metric("Change Since 1970", f"{change:+.1f}%")
    with col_trend2:
        peak_year = yearly.loc[yearly['value'].idxmax(), 'period']
        peak_value = yearly['value'].max()
        st.metric("Peak Year", f"{int(peak_year)}", f"{peak_value:.0f}M MT")
    with col_trend3:
        avg_recent = yearly[yearly['period'] >= 2010]['value'].mean()
        st.metric("Avg (2010-2022)", f"{avg_recent:.2f}")

with tab2:
    sector_data = df.groupby('sector-name')['value'].sum().reset_index().sort_values('value', ascending=True)
    
    fig = px.bar(sector_data, x='value', y='sector-name', orientation='h',
                 title='EMISSIONS BY SECTOR',
                 labels={'value': 'EMISSIONS', 'sector-name': 'SECTOR'},
                 color='value',
                 color_continuous_scale=['#00ffd5', '#00a896', '#ff00aa'])
    fig.update_layout(
        title=dict(font=dict(family='Orbitron', size=18, color='#00ffd5'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Rajdhani', color='#fff'),
        xaxis=dict(gridcolor='rgba(0,255,213,0.1)', tickfont=dict(color='#fff')),
        yaxis=dict(tickfont=dict(color='#fff', family='Rajdhani'))
    )
    st.plotly_chart(fig, use_container_width=True)

    sector_pie = df.groupby('sector-name')['value'].sum().reset_index()
    fig_pie = go.Figure(data=[go.Pie(
        labels=sector_pie['sector-name'].str.replace(' carbon dioxide emissions', ''),
        values=sector_pie['value'],
        hole=0.5,
        marker=dict(colors=['#00ffd5', '#4ecdc4', '#ff00aa', '#ffa502', '#c0c0c0', '#6b5b95']),
        textfont=dict(family='Rajdhani', color='#fff', size=12),
        hovertemplate='%{label}<br>%{percent}<extra></extra>'
    )])
    fig_pie.update_layout(
        title=dict(text='SECTOR DISTRIBUTION', font=dict(family='Orbitron', size=18, color='#00ffd5'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Rajdhani', color='#fff')
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with tab3:
    fuel_data = df.groupby('fuel-name')['value'].sum().reset_index().sort_values('value', ascending=True)
    
    fig = px.bar(fuel_data, x='value', y='fuel-name', orientation='h',
                 title='EMISSIONS BY FUEL TYPE',
                 labels={'value': 'EMISSIONS', 'fuel-name': 'FUEL TYPE'},
                 color='value',
                 color_continuous_scale=['#ff00aa', '#ff6b6b', '#ffa502'])
    fig.update_layout(
        title=dict(font=dict(family='Orbitron', size=18, color='#ff00aa'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Rajdhani', color='#fff'),
        xaxis=dict(gridcolor='rgba(255,0,170,0.1)', tickfont=dict(color='#fff')),
        yaxis=dict(tickfont=dict(color='#fff', family='Rajdhani'))
    )
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    state_data = df.groupby('state-name')['value'].sum().reset_index().sort_values('value', ascending=False).head(20)
    
    fig = px.bar(state_data, x='value', y='state-name', orientation='h',
                 title='TOP 20 STATES BY EMISSIONS',
                 labels={'value': 'EMISSIONS', 'state-name': 'STATE'},
                 color='value',
                 color_continuous_scale='Viridis')
    fig.update_layout(
        title=dict(font=dict(family='Orbitron', size=18, color='#4ecdc4'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Rajdhani', color='#fff'),
        xaxis=dict(gridcolor='rgba(78,205,196,0.1)', tickfont=dict(color='#fff')),
        yaxis=dict(tickfont=dict(color='#fff', family='Rajdhani'))
    )
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("VIEW ALL STATES"):
        all_states = df.groupby('state-name')['value'].sum().sort_values(ascending=False)
        st.dataframe(pd.DataFrame({'STATE': all_states.index, 'EMISSIONS': all_states.values}), use_container_width=True)

st.markdown("---")

col_info1, col_info2 = st.columns(2)

with col_info1:
    st.markdown("### KEY INSIGHTS")
    st.markdown("""
    <div class="futuristic-card" style="margin-bottom: 15px;">
        <p style="margin:0;"><span style="color: #00ffd5;">▸</span> <strong>Transportation</strong> leads at ~40%</p>
    </div>
    <div class="futuristic-card" style="margin-bottom: 15px;">
        <p style="margin:0;"><span style="color: #ff00aa;">▸</span> <strong>Petroleum</strong> dominates >50%</p>
    </div>
    <div class="futuristic-card">
        <p style="margin:0;"><span style="color: #4ecdc4;">▸</span> <strong>Texas</strong> tops states</p>
    </div>
    """, unsafe_allow_html=True)

with col_info2:
    st.markdown("### DATA SUMMARY")
    st.markdown(f"""
    <div class="futuristic-card" style="margin-bottom: 15px;">
        <p style="margin:0;"><span style="color: #00ffd5;">◈</span> <strong>Source:</strong> U.S. EIA API</p>
    </div>
    <div class="futuristic-card" style="margin-bottom: 15px;">
        <p style="margin:0;"><span style="color: #00ffd5;">◈</span> <strong>Period:</strong> {min(years)} - {max(years)}</p>
    </div>
    <div class="futuristic-card">
        <p style="margin:0;"><span style="color: #00ffd5;">◈</span> <strong>Total:</strong> {len(df):,} records</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 30px; color: rgba(255,255,255,0.3); font-size: 0.8rem;">
    <p>USA CARBON EMISSIONS ANALYSIS | DATA: U.S. ENERGY INFORMATION ADMINISTRATION</p>
</div>
""", unsafe_allow_html=True)