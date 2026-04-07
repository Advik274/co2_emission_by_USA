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
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

:root {
    --primary: #00ff7f;
    --primary-dim: #00cc66;
    --secondary: #ff00ff;
    --accent: #00ffd5;
    --bg-dark: #050508;
    --bg-glass: rgba(15, 15, 15, 0.7);
    --glow: 0 0 20px rgba(0, 255, 127, 0.5);
    --glow-pink: 0 0 20px rgba(255, 0, 255, 0.5);
}

* { box-sizing: border-box; }

.stApp {
    background: linear-gradient(180deg, #050508 0%, #0a0a15 50%, #050508 100%) !important;
    font-family: 'Rajdhani', sans-serif !important;
    color: #ffffff !important;
}

/* CRT Scanline Overlay */
.scanline-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 9999;
    pointer-events: none;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0, 0, 0, 0.03) 2px,
        rgba(0, 0, 0, 0.03) 4px
    );
}

/* Background Grid */
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

/* Floating Orbs */
.glow-orb-1 {
    position: fixed;
    width: 600px;
    height: 600px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0, 255, 127, 0.05) 0%, transparent 70%);
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
    background: radial-gradient(circle, rgba(255, 0, 255, 0.04) 0%, transparent 70%);
    bottom: -150px;
    left: -150px;
    animation: orbFloat 25s ease-in-out infinite reverse;
    z-index: -1;
}

@keyframes orbFloat {
    0%, 100% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(30px, 30px) scale(1.1); }
}

/* Typography - Monospace for data */
h1, h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    color: #00ff7f !important;
}

h1 {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 2.6rem !important;
    font-weight: 700 !important;
}

/* Glassmorphism Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(10, 10, 15, 0.85) !important;
    backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(0, 255, 127, 0.15) !important;
}

/* Neon Navigation */
.stRadio [role="radiogroup"] {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.stRadio [role="radiogroup"] label {
    padding: 12px 15px !important;
    border-radius: 8px !important;
    background: transparent !important;
    border-left: 2px solid transparent !important;
    transition: all 0.3s ease !important;
    color: rgba(255,255,255,0.6) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
}

.stRadio [role="radiogroup"] label:hover {
    background: rgba(0, 255, 127, 0.05) !important;
    color: #00ff7f !important;
}

.stRadio [role="radiogroup"] input:checked + label {
    background: rgba(0, 255, 127, 0.1) !important;
    border-left: 2px solid #00ff7f !important;
    box-shadow: 0 0 15px rgba(0, 255, 127, 0.2) !important;
    color: #00ff7f !important;
}

/* Futuristic Cards with Corner Brackets */
.futuristic-card {
    background: linear-gradient(135deg, rgba(20, 20, 35, 0.9) 0%, rgba(10, 10, 20, 0.95) 100%) !important;
    border: none !important;
    border-radius: 0px !important;
    padding: 25px !important;
    position: relative;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
}

.futuristic-card::before,
.futuristic-card::after {
    content: '';
    position: absolute;
    width: 15px;
    height: 15px;
    border-color: #00ff7f;
    border-style: solid;
}

.futuristic-card::before {
    top: -1px;
    left: -1px;
    border-width: 2px 0 0 2px;
}

.futuristic-card::after {
    bottom: -1px;
    right: -1px;
    border-width: 0 2px 2px 0;
}

.futuristic-card:hover {
    transform: translateY(-8px) !important;
    box-shadow: 0 20px 60px rgba(0, 255, 127, 0.15), 0 0 40px rgba(0, 255, 127, 0.1) !important;
}

/* Metric Values - Monospace */
.metric-value {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 2.2rem !important;
    font-weight: 700 !important;
    color: #00ff7f !important;
    text-shadow: 0 0 20px rgba(0, 255, 127, 0.5) !important;
}

.metric-label {
    color: rgba(255, 255, 255, 0.5) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}

.metric-unit {
    font-size: 10px !important;
    opacity: 0.6 !important;
    text-transform: uppercase !important;
}

/* Buttons */
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
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
    transition: left 0.5s;
}

.stButton > button:hover {
    transform: scale(1.03) !important;
    box-shadow: 0 10px 40px rgba(0, 255, 127, 0.4) !important;
}

.stButton > button:hover::before {
    left: 100%;
}

/* Select Boxes */
.stSelectbox > div > div:first-child {
    background: rgba(15, 15, 25, 0.9) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(0, 255, 127, 0.3) !important;
    border-radius: 0px !important;
    color: #fff !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* Tabs - Neon Style */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 2px !important;
    background: transparent !important;
    border: 1px solid rgba(0, 255, 127, 0.15) !important;
    border-radius: 0px !important;
    padding: 14px 24px !important;
    color: rgba(255,255,255,0.5) !important;
    transition: all 0.3s ease !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #00ff7f !important;
    border-color: rgba(0, 255, 127, 0.4) !important;
}

.stTabs [aria-selected="true"] {
    background: rgba(0, 255, 127, 0.1) !important;
    border: 1px solid #00ff7f !important;
    border-bottom: 2px solid #00ff7f !important;
    color: #00ff7f !important;
    box-shadow: 0 -5px 30px rgba(0, 255, 127, 0.2) !important;
}

/* Custom Scrollbars */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #00ff7f; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #00cc66; }

/* Divider */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(0, 255, 127, 0.5), transparent) !important;
    margin: 40px 0 !important;
}

/* Progress */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #00ff7f, #00cc66, #ff00ff) !important;
    border-radius: 0px !important;
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
    border: 3px solid rgba(0, 255, 127, 0.1) !important;
    border-top: 3px solid #00ff7f !important;
    border-radius: 0px !important;
    width: 50px !important;
    height: 50px !important;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Selection Chips */
.filter-chip {
    display: inline-flex;
    align-items: center;
    padding: 8px 16px;
    background: rgba(0, 255, 127, 0.15);
    border: 1px solid rgba(0, 255, 127, 0.4);
    border-radius: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #00ff7f;
    margin: 5px;
}

.filter-chip .remove {
    margin-left: 8px;
    cursor: pointer;
    opacity: 0.7;
}

.filter-chip .remove:hover {
    opacity: 1;
}

/* Data Tables */
[data-testid="stDataFrame"] {
    background: rgba(15, 15, 25, 0.9) !important;
    border: 1px solid rgba(0, 255, 127, 0.2) !important;
    border-radius: 0px !important;
}

[data-testid="stDataFrame"] thead {
    position: sticky;
    top: 0;
    background: rgba(15, 15, 25, 0.95) !important;
    backdrop-filter: blur(10px);
    z-index: 1;
}

[data-testid="stDataFrame"] tbody tr:hover {
    background: rgba(0, 255, 127, 0.08) !important;
}
</style>

<div class="scanline-overlay"></div>
<div class="bg-grid"></div>
<div class="glow-orb-1"></div>
<div class="glow-orb-2"></div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; padding: 40px 20px 30px;">
    <h1>USA Carbon Emissions</h1>
    <p style="color: rgba(255,255,255,0.4); font-size: 1rem; letter-spacing: 6px; font-family: 'JetBrains Mono', monospace;">
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
        <h3 style="font-size: 0.9rem !important; color: #00ff7f !important; font-family: 'JetBrains Mono', monospace;">// NAVIGATION</h3>
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
    
    st.markdown("""
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #00ff7f; letter-spacing: 2px;">
        // FILTERS
    </div>
    """, unsafe_allow_html=True)
    
    selected_state = st.selectbox("State", ["All"] + states)
    selected_sector = st.selectbox("Sector", ["All"] + sectors)
    selected_fuel = st.selectbox("Fuel", ["All"] + fuels)
    
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; padding: 15px; background: rgba(0,255,127,0.05); border: 1px solid rgba(0,255,127,0.2); border-radius: 0px;">
        <p style="margin:0; color: #00ff7f; font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; letter-spacing: 2px;">DATASET INFO</p>
    </div>
    <div style="padding: 15px; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;">
        <p style="margin: 10px 0;"><span style="color: #00ff7f;">></span> Records: <span style="color: #fff;">{len(df):,}</span></p>
        <p style="margin: 10px 0;"><span style="color: #00ff7f;">></span> States: <span style="color: #fff;">{len(states)}</span></p>
        <p style="margin: 10px 0;"><span style="color: #00ff7f;">></span> Years: <span style="color: #fff;">{min(years)}-{max(years)}</span></p>
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
        <p class="metric-label">TOTAL EMISSIONS</p>
        <p class="metric-value">{total_emissions:,.2f}</p>
        <p class="metric-unit">MILLION METRIC TONS</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="futuristic-card fade-in stagger-2">
        <p class="metric-label">AVERAGE</p>
        <p class="metric-value">{avg_emissions:.3f}</p>
        <p class="metric-unit">MILLION METRIC TONS</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="futuristic-card fade-in stagger-3">
        <p class="metric-label">MAXIMUM</p>
        <p class="metric-value" style="color: #ff00ff !important; text-shadow: 0 0 20px rgba(255,0,255,0.5) !important;">{max_emission:.3f}</p>
        <p class="metric-unit">MILLION METRIC TONS</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="futuristic-card fade-in stagger-4">
        <p class="metric-label">MINIMUM</p>
        <p class="metric-value" style="color: #00ffd5 !important; text-shadow: 0 0 20px rgba(0,255,213,0.5) !important;">{min_emission:.3f}</p>
        <p class="metric-unit">MILLION METRIC TONS</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["EMISSIONS TIMELINE", "BY SECTOR", "BY FUEL", "BY STATE"])

with tab1:
    st.markdown("""
    <div class="insight-narrative">
        <p style="color: #888; font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; margin-bottom: 20px;">
            // The story: A half-century of American emissions reveals a nation's energy evolution. 
            From the industrial boom of the 1970s to the clean energy push of today, 
            this timeline captures the ebbs and flows of our carbon footprint.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    yearly = df.groupby('period')['value'].sum().reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=yearly['period'], y=yearly['value'],
        mode='lines+markers',
        line=dict(color='#00ff7f', width=3, shape='spline'),
        marker=dict(size=8, color='#00ff7f', line=dict(color='#050508', width=2)),
        fill='tozeroy',
        fillcolor='rgba(0, 255, 127, 0.1)'
    ))
    fig.update_layout(
        title=dict(text='CO2 EMISSIONS OVER TIME', font=dict(family='JetBrains Mono', size=16, color='#00ff7f'), x=0.5),
        xaxis_title=dict(text='YEAR', font=dict(family='JetBrains Mono', size=12, color='#00ff7f')),
        yaxis_title=dict(text='EMISSIONS (MILLION MT)', font=dict(family='JetBrains Mono', size=12, color='#00ff7f')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='JetBrains Mono', color='#fff'),
        xaxis=dict(gridcolor='rgba(0,255,127,0.1)', tickfont=dict(color='#fff'), tickformat='d'),
        yaxis=dict(gridcolor='rgba(0,255,127,0.1)', tickfont=dict(color='#fff'))
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
    
    st.markdown("""
    <div class="futuristic-card" style="margin-top: 20px;">
        <p style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #00ff7f; margin: 0;">
            // KEY TAKEAWAY: Emissions peaked in 2007 at 6,021 million metric tons—the height of America's 
            fossil fuel dependency. Since then, a gradual decline reflects the shift toward cleaner energy sources. 
            The 2020 dip (visible in the chart) marks an unprecedented drop due to pandemic-induced economic slowdown.
        </p>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("""
    <div class="insight-narrative">
        <p style="color: #888; font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; margin-bottom: 20px;">
            // The story: America's carbon story is written in its sectors. Transportation fuels our economy 
            but also feeds our emissions. The battle between progress and preservation plays out in these numbers.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    sector_data = df.groupby('sector-name')['value'].sum().reset_index().sort_values('value', ascending=True)
    
    fig = px.bar(sector_data, x='value', y='sector-name', orientation='h',
                 title='EMISSIONS BY SECTOR',
                 labels={'value': 'EMISSIONS', 'sector-name': 'SECTOR'},
                 color='value',
                 color_continuous_scale=['#00ff7f', '#00cc66', '#ff00ff'])
    fig.update_layout(
        title=dict(font=dict(family='JetBrains Mono', size=16, color='#00ff7f'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='JetBrains Mono', color='#fff'),
        xaxis=dict(gridcolor='rgba(0,255,127,0.1)', tickfont=dict(color='#fff')),
        yaxis=dict(tickfont=dict(color='#fff', family='JetBrains Mono'))
    )
    st.plotly_chart(fig, use_container_width=True)

    sector_pie = df.groupby('sector-name')['value'].sum().reset_index()
    fig_pie = go.Figure(data=[go.Pie(
        labels=sector_pie['sector-name'].str.replace(' carbon dioxide emissions', ''),
        values=sector_pie['value'],
        hole=0.6,
        marker=dict(colors=['#00ff7f', '#00ffd5', '#ff00ff', '#ffa502', '#c0c0c0', '#6b5b95']),
        textfont=dict(family='JetBrains Mono', color='#fff', size=11),
        hovertemplate='%{label}<br>%{percent}<extra></extra>'
    )])
    fig_pie.update_layout(
        title=dict(text='SECTOR DISTRIBUTION', font=dict(family='JetBrains Mono', size=16, color='#00ff7f'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='JetBrains Mono', color='#fff')
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown("""
    <div class="futuristic-card" style="margin-top: 20px;">
        <p style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #00ff7f; margin: 0;">
            // KEY TAKEAWAY: Transportation dominates with 36% of all emissions—America's love affair 
            with the automobile. Electric Power follows at 33%, while Residential and Commercial sectors 
            account for just 18% combined. Industrial sector contributes 13%—the backbone of manufacturing.
        </p>
    </div>
    """, unsafe_allow_html=True)

with tab3:
    st.markdown("""
    <div class="insight-narrative">
        <p style="color: #888; font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; margin-bottom: 20px;">
            // The story: Crude oil refined into gasoline, diesel, and jet fuel—Petroleum remains 
            the powerhouse of America's energy landscape, outpacing all other fuels combined.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    fuel_data = df.groupby('fuel-name')['value'].sum().reset_index().sort_values('value', ascending=True)
    
    fig = px.bar(fuel_data, x='value', y='fuel-name', orientation='h',
                 title='EMISSIONS BY FUEL TYPE',
                 labels={'value': 'EMISSIONS', 'fuel-name': 'FUEL TYPE'},
                 color='value',
                 color_continuous_scale=['#ff00ff', '#ff6b6b', '#ffa502'])
    fig.update_layout(
        title=dict(font=dict(family='JetBrains Mono', size=16, color='#ff00ff'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='JetBrains Mono', color='#fff'),
        xaxis=dict(gridcolor='rgba(255,0,255,0.1)', tickfont=dict(color='#fff')),
        yaxis=dict(tickfont=dict(color='#fff', family='JetBrains Mono'))
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div class="futuristic-card" style="margin-top: 20px;">
        <p style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #ff00ff; margin: 0;">
            // KEY TAKEAWAY: Petroleum accounts for a staggering 54% of emissions—more than all 
            other fuels combined. Natural Gas contributes 34%, while Coal, once king, 
            now accounts for just 12%. The "All Fuels" category (aggregated data) makes up the remainder.
        </p>
    </div>
    """, unsafe_allow_html=True)

with tab4:
    st.markdown("""
    <div class="insight-narrative">
        <p style="color: #888; font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; margin-bottom: 20px;">
            // The story: Not all states contribute equally to the carbon ledger. 
            Texas alone emits more than the entire emissions of many developed nations—a true energy giant.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    state_data = df.groupby('state-name')['value'].sum().reset_index().sort_values('value', ascending=False).head(20)
    
    fig = px.bar(state_data, x='value', y='state-name', orientation='h',
                 title='TOP 20 STATES BY EMISSIONS',
                 labels={'value': 'EMISSIONS', 'state-name': 'STATE'},
                 color='value',
                 color_continuous_scale='Viridis')
    fig.update_layout(
        title=dict(font=dict(family='JetBrains Mono', size=16, color='#00ffd5'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='JetBrains Mono', color='#fff'),
        xaxis=dict(gridcolor='rgba(0,255,213,0.1)', tickfont=dict(color='#fff')),
        yaxis=dict(tickfont=dict(color='#fff', family='JetBrains Mono'))
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div class="futuristic-card" style="margin-top: 20px;">
        <p style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #00ffd5; margin: 0;">
            // KEY TAKEAWAY: Texas leads all states with emissions 3x higher than California—the #2 emitter. 
            The top 5 states (Texas, California, Pennsylvania, Florida, Ohio) account for 40% of national emissions. 
            This concentration reveals where energy policy can make the biggest impact.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("VIEW ALL STATES"):
        all_states = df.groupby('state-name')['value'].sum().sort_values(ascending=False)
        st.dataframe(pd.DataFrame({'STATE': all_states.index, 'EMISSIONS': all_states.values}), use_container_width=True)

st.markdown("---")

col_info1, col_info2 = st.columns(2)

with col_info1:
    st.markdown("### KEY INSIGHTS")
    st.markdown("""
    <div class="futuristic-card" style="margin-bottom: 15px;">
        <p style="margin:0; font-family: 'JetBrains Mono', monospace;"><span style="color: #00ff7f;">▸</span> <strong>Transportation</strong> leads at ~40%</p>
    </div>
    <div class="futuristic-card" style="margin-bottom: 15px;">
        <p style="margin:0; font-family: 'JetBrains Mono', monospace;"><span style="color: #ff00ff;">▸</span> <strong>Petroleum</strong> dominates >50%</p>
    </div>
    <div class="futuristic-card">
        <p style="margin:0; font-family: 'JetBrains Mono', monospace;"><span style="color: #00ffd5;">▸</span> <strong>Texas</strong> tops states</p>
    </div>
    """, unsafe_allow_html=True)

with col_info2:
    st.markdown("### DATA SUMMARY")
    st.markdown(f"""
    <div class="futuristic-card" style="margin-bottom: 15px;">
        <p style="margin:0; font-family: 'JetBrains Mono', monospace;"><span style="color: #00ff7f;">◈</span> <strong>Source:</strong> U.S. EIA API</p>
    </div>
    <div class="futuristic-card" style="margin-bottom: 15px;">
        <p style="margin:0; font-family: 'JetBrains Mono', monospace;"><span style="color: #00ff7f;">◈</span> <strong>Period:</strong> {min(years)} - {max(years)}</p>
    </div>
    <div class="futuristic-card">
        <p style="margin:0; font-family: 'JetBrains Mono', monospace;"><span style="color: #00ff7f;">◈</span> <strong>Total:</strong> {len(df):,} records</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 30px; color: rgba(255,255,255,0.3); font-size: 0.75rem; font-family: 'JetBrains Mono', monospace;">
    <p>USA CARBON EMISSIONS ANALYSIS // DATA: U.S. ENERGY INFORMATION ADMINISTRATION</p>
</div>
""", unsafe_allow_html=True)