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
    page_title="USA CO2 Emissions",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    h1, h2, h3 { color: #00d4aa !important; }
    h4 { color: #4ecdc4 !important; }
    .stButton>button {
        background-color: #00d4aa;
        color: #000;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #00b894;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e1e2f 0%, #2d2d44 100%);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #00d4aa33;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #00d4aa;
    }
    .metric-label {
        font-size: 14px;
        color: #888;
    }
    .nav-item {
        padding: 10px 15px;
        margin: 5px 0;
        border-radius: 8px;
        background: #1a1a2e;
        color: #fff;
        transition: all 0.3s;
    }
    .nav-item:hover {
        background: #2d2d44;
    }
    .nav-item.active {
        background: #00d4aa;
        color: #000;
    }
    .css-1d391kg { padding-top: 1rem; }
    .stSelectbox label { color: #00d4aa !important; }
    .stRadio label { color: #00d4aa !important; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        background-color: #1a1a2e;
        border-radius: 4px 4px 0px 0px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00d4aa;
        color: #000;
    }
    div[data-testid="stMetricValue"] {
        color: #00d4aa !important;
    }
    .insight-card {
        background: linear-gradient(135deg, #1e1e2f 0%, #2d2d44 100%);
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #00d4aa;
    }
    .sidebar-section {
        background: #1a1a2e;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌿 USA Carbon Emissions Analysis")
st.markdown("### Future Carbon Emission Horizons of the United States")
st.markdown("---")

try:
    df = utils.load_raw_data()
    states, sectors, fuels, years = utils.get_unique_values()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

with st.sidebar:
    st.markdown("### 🧭 Navigation")
    
    nav_options = ["📊 Dashboard", "🔮 Predictions", "📈 Model Comparison", "📉 Analytics"]
    selected_nav = st.radio("Go to", nav_options, label_visibility="collapsed")
    
    if selected_nav == "🔮 Predictions":
        st.switch_page("pages/predictions.py")
    elif selected_nav == "📈 Model Comparison":
        st.switch_page("pages/model_comparison.py")
    elif selected_nav == "📉 Analytics":
        st.switch_page("pages/analytics.py")
    
    st.markdown("---")
    
    st.markdown("### ⚙️ Filters")
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    selected_state = st.selectbox("🌍 State", ["All"] + states)
    selected_sector = st.selectbox("🏭 Sector", ["All"] + sectors)
    selected_fuel = st.selectbox("⛽ Fuel", ["All"] + fuels)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 📚 Dataset Info")
    st.markdown(f"""
    <div class="sidebar-section">
        <p style="margin:5px 0;"><strong>Records:</strong> {len(df):,}</p>
        <p style="margin:5px 0;"><strong>States:</strong> {len(states)}</p>
        <p style="margin:5px 0;"><strong>Years:</strong> {min(years)} - {max(years)}</p>
        <p style="margin:5px 0;"><strong>Sectors:</strong> {len(sectors)}</p>
        <p style="margin:5px 0;"><strong>Fuels:</strong> {len(fuels)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 Quick Stats")
    if selected_state == "All" and selected_sector == "All" and selected_fuel == "All":
        top_state = df.groupby('state-name')['value'].sum().idxmax()
        top_sector = df.groupby('sector-name')['value'].sum().idxmax()
        top_fuel = df.groupby('fuel-name')['value'].sum().idxmax()
        
        st.markdown(f"""
        <div class="insight-card">
            <p style="margin:0; color:#888; font-size:12px;">Highest Emitter</p>
            <p style="margin:0; color:#00d4aa; font-size:14px;">{top_state}</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        st.markdown(f"""
        <div class="insight-card">
            <p style="margin:0; color:#888; font-size:12px;">Top Sector</p>
            <p style="margin:0; color:#00d4aa; font-size:14px;">{top_sector.split()[0]}</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        st.markdown(f"""
        <div class="insight-card">
            <p style="margin:0; color:#888; font-size:12px;">Primary Fuel</p>
            <p style="margin:0; color:#00d4aa; font-size:14px;">{top_fuel}</p>
        </div>
        """, unsafe_allow_html=True)

if selected_state != "All":
    df = df[df['state-name'] == selected_state]
if selected_sector != "All":
    df = df[df['sector-name'] == selected_sector]
if selected_fuel != "All":
    df = df[df['fuel-name'] == selected_fuel]

st.markdown("### 📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

total_emissions = df['value'].sum()
avg_emissions = df['value'].mean()
max_emission = df['value'].max()
min_emission = df['value'].min()

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-label">Total Emissions</p>
        <p class="metric-value">{total_emissions:,.2f}</p>
        <p style="color:#666; font-size:12px;">million metric tons</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-label">Average</p>
        <p class="metric-value">{avg_emissions:.3f}</p>
        <p style="color:#666; font-size:12px;">million metric tons</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-label">Maximum</p>
        <p class="metric-value">{max_emission:.3f}</p>
        <p style="color:#666; font-size:12px;">million metric tons</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-label">Minimum</p>
        <p class="metric-value">{min_emission:.3f}</p>
        <p style="color:#666; font-size:12px;">million metric tons</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["📈 Emissions Over Time", "🏭 By Sector", "⛽ By Fuel", "🗺️ By State"])

with tab1:
    yearly = df.groupby('period')['value'].sum().reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=yearly['period'], 
        y=yearly['value'],
        mode='lines+markers',
        line=dict(color='#00d4aa', width=3),
        marker=dict(size=8, color='#00d4aa')
    ))
    fig.add_trace(go.Scatter(
        x=yearly['period'],
        y=yearly['value'],
        mode='lines',
        fill='tozeroy',
        fillcolor='rgba(0, 212, 170, 0.2)',
        line=dict(color='rgba(0,0,0,0)')
    ))
    fig.update_layout(
        title='Total CO2 Emissions Over Time',
        xaxis_title='Year',
        yaxis_title='Emissions (million metric tons)',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#fff'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    col_trend1, col_trend2 = st.columns(2)
    with col_trend1:
        first_year = yearly.iloc[0]['value']
        last_year = yearly.iloc[-1]['value']
        change = ((last_year - first_year) / first_year) * 100
        st.metric("Change Since 1970", f"{change:.1f}%", 
                 "↓" if change < 0 else "↑")
    with col_trend2:
        peak_year = yearly.loc[yearly['value'].idxmax(), 'period']
        peak_value = yearly['value'].max()
        st.metric("Peak Year", f"{int(peak_year)}", f"{peak_value:.0f}M MT")

with tab2:
    sector_data = df.groupby('sector-name')['value'].sum().reset_index()
    sector_data = sector_data.sort_values('value', ascending=True)
    
    fig = px.bar(sector_data, x='value', y='sector-name', orientation='h',
                 title='CO2 Emissions by Sector',
                 labels={'value': 'Emissions (million metric tons)', 'sector-name': 'Sector'},
                 color='value',
                 color_continuous_scale='Teal')
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#fff'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    sector_pie = df.groupby('sector-name')['value'].sum().reset_index()
    fig_pie = go.Figure(data=[go.Pie(
        labels=sector_pie['sector-name'].str.replace(' carbon dioxide emissions', ''),
        values=sector_pie['value'],
        hole=0.4,
        marker=dict(colors=['#00d4aa', '#4ecdc4', '#ff6b6b', '#ffa502', '#c0c0c0', '#6b5b95'])
    )])
    fig_pie.update_layout(
        title='Sector Distribution',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#fff'
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with tab3:
    fuel_data = df.groupby('fuel-name')['value'].sum().reset_index()
    fuel_data = fuel_data.sort_values('value', ascending=True)
    
    fig = px.bar(fuel_data, x='value', y='fuel-name', orientation='h',
                 title='CO2 Emissions by Fuel Type',
                 labels={'value': 'Emissions (million metric tons)', 'fuel-name': 'Fuel Type'},
                 color='value',
                 color_continuous_scale='Reds')
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#fff'
    )
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    state_data = df.groupby('state-name')['value'].sum().reset_index()
    state_data = state_data.sort_values('value', ascending=False).head(20)
    
    fig = px.bar(state_data, x='value', y='state-name', orientation='h',
                 title='Top 20 States by CO2 Emissions',
                 labels={'value': 'Emissions (million metric tons)', 'state-name': 'State'},
                 color='value',
                 color_continuous_scale='Viridis')
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#fff'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("View All States"):
        all_states = df.groupby('state-name')['value'].sum().sort_values(ascending=False)
        st.dataframe(pd.DataFrame({'State': all_states.index, 'Emissions': all_states.values}), use_container_width=True)

st.markdown("---")

col_info1, col_info2 = st.columns(2)

with col_info1:
    st.markdown("### 🔍 Key Insights")
    st.markdown("""
    <div class="insight-card">
        <p style="margin:0;"><strong>Transportation Sector</strong> is the largest emitter, contributing to nearly 40% of total CO2 emissions.</p>
    </div>
    <div class="insight-card">
        <p style="margin:0;"><strong>Petroleum</strong> remains the dominant fuel source, accounting for over 50% of emissions.</p>
    </div>
    <div class="insight-card">
        <p style="margin:0;"><strong>Texas</strong> leads all states in emissions, followed by California and Pennsylvania.</p>
    </div>
    """, unsafe_allow_html=True)

with col_info2:
    st.markdown("### 📋 Data Summary")
    st.markdown(f"""
    <div class="insight-card">
        <p style="margin:0;"><strong>Data Source:</strong> U.S. EIA API</p>
    </div>
    <div class="insight-card">
        <p style="margin:0;"><strong>Time Period:</strong> {min(years)} - {max(years)}</p>
    </div>
    <div class="insight-card">
        <p style="margin:0;"><strong>Total Records:</strong> {len(df):,}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("🌿 USA Carbon Emissions Analysis | Data: U.S. Energy Information Administration")