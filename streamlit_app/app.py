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
    .main {
        background-color: #0e1117;
    }
    .stApp {
        background-color: #0e1117;
    }
    h1, h2, h3 {
        color: #00d4aa !important;
    }
    .stButton>button {
        background-color: #00d4aa;
        color: #000;
    }
    .stButton>button:hover {
        background-color: #00b894;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e1e2f 0%, #2d2d44 100%);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #00d4aa33;
    }
    .css-1d391kg {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌿 USA Carbon Emissions Analysis")
st.markdown("### Future Carbon Emission Horizons of the United States")

try:
    df = utils.load_raw_data()
    states, sectors, fuels, years = utils.get_unique_values()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

with st.sidebar:
    st.header("⚙️ Settings")
    selected_state = st.selectbox("Select State", ["All"] + states)
    selected_sector = st.selectbox("Select Sector", ["All"] + sectors)
    selected_fuel = st.selectbox("Select Fuel", ["All"] + fuels)
    
    st.markdown("---")
    st.markdown("**Dataset Info:**")
    st.markdown(f"- Records: {len(df):,}")
    st.markdown(f"- States: {len(states)}")
    st.markdown(f"- Years: {min(years)} - {max(years)}")
    st.markdown(f"- Sectors: {len(sectors)}")
    st.markdown(f"- Fuels: {len(fuels)}")

if selected_state != "All":
    df = df[df['state-name'] == selected_state]
if selected_sector != "All":
    df = df[df['sector-name'] == selected_sector]
if selected_fuel != "All":
    df = df[df['fuel-name'] == selected_fuel]

col1, col2, col3, col4 = st.columns(4)

total_emissions = df['value'].sum()
avg_emissions = df['value'].mean()
max_emission = df['value'].max()
min_emission = df['value'].min()

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <p style="margin:0; color:#888;">Total Emissions</p>
        <h2 style="margin:0; color:#00d4aa;">{total_emissions:,.2f}</h2>
        <p style="margin:0; color:#666;">million metric tons</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <p style="margin:0; color:#888;">Average</p>
        <h2 style="margin:0; color:#00d4aa;">{avg_emissions:.3f}</h2>
        <p style="margin:0; color:#666;">million metric tons</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <p style="margin:0; color:#888;">Maximum</p>
        <h2 style="margin:0; color:#00d4aa;">{max_emission:.3f}</h2>
        <p style="margin:0; color:#666;">million metric tons</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <p style="margin:0; color:#888;">Minimum</p>
        <h2 style="margin:0; color:#00d4aa;">{min_emission:.3f}</h2>
        <p style="margin:0; color:#666;">million metric tons</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["📈 Emissions Over Time", "🏭 By Sector", "⛽ By Fuel", "🗺️ By State"])

with tab1:
    yearly = df.groupby('period')['value'].sum().reset_index()
    fig = px.line(yearly, x='period', y='value', 
                  title='Total CO2 Emissions Over Time',
                  labels={'period': 'Year', 'value': 'Emissions (million metric tons)'})
    fig.update_traces(line_color='#00d4aa', line_width=3)
    fig.update_layout(
        paper_bgcolor='transparent',
        plot_bgcolor='transparent',
        font_color='#fff'
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    sector_data = df.groupby('sector-name')['value'].sum().reset_index()
    sector_data = sector_data.sort_values('value', ascending=True)
    fig = px.bar(sector_data, x='value', y='sector-name', orientation='h',
                 title='CO2 Emissions by Sector',
                 labels={'value': 'Emissions (million metric tons)', 'sector-name': 'Sector'})
    fig.update_traces(marker_color='#00d4aa')
    fig.update_layout(
        paper_bgcolor='transparent',
        plot_bgcolor='transparent',
        font_color='#fff'
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    fuel_data = df.groupby('fuel-name')['value'].sum().reset_index()
    fuel_data = fuel_data.sort_values('value', ascending=True)
    fig = px.bar(fuel_data, x='value', y='fuel-name', orientation='h',
                 title='CO2 Emissions by Fuel Type',
                 labels={'value': 'Emissions (million metric tons)', 'fuel-name': 'Fuel Type'})
    fig.update_traces(marker_color='#ff6b6b')
    fig.update_layout(
        paper_bgcolor='transparent',
        plot_bgcolor='transparent',
        font_color='#fff'
    )
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    state_data = df.groupby('state-name')['value'].sum().reset_index()
    state_data = state_data.sort_values('value', ascending=False).head(20)
    fig = px.bar(state_data, x='value', y='state-name', orientation='h',
                 title='Top 20 States by CO2 Emissions',
                 labels={'value': 'Emissions (million metric tons)', 'state-name': 'State'})
    fig.update_traces(marker_color='#4ecdc4')
    fig.update_layout(
        paper_bgcolor='transparent',
        plot_bgcolor='transparent',
        font_color='#fff'
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("*Data Source: U.S. Energy Information Administration (EIA) API*")