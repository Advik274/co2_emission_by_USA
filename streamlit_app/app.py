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

with open(os.path.join(os.path.dirname(__file__), "styles.css"), "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<div class="scanline-overlay"></div>
<div class="bg-grid"></div>
<div class="glow-orb-1"></div>
<div class="glow-orb-2"></div>
<div class="glow-orb-3"></div>
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
    
    selected_states = st.multiselect("States", states, default=[states[0]] if states else [])
    selected_sectors = st.multiselect("Sectors", sectors, default=[sectors[0]] if sectors else [])
    selected_fuels = st.multiselect("Fuels", fuels, default=[fuels[0]] if fuels else [])
    
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

filtered_df = df.copy()
if selected_states:
    filtered_df = filtered_df[filtered_df['state-name'].isin(selected_states)]
if selected_sectors:
    filtered_df = filtered_df[filtered_df['sector-name'].isin(selected_sectors)]
if selected_fuels:
    filtered_df = filtered_df[filtered_df['fuel-name'].isin(selected_fuels)]

st.markdown("### KEY METRICS")

col1, col2, col3, col4 = st.columns(4)

total_emissions = filtered_df['value'].sum()
avg_emissions = filtered_df['value'].mean()
max_emission = filtered_df['value'].max()
min_emission = filtered_df['value'].min()

with col1:
    st.markdown(f"""
    <div class="futuristic-card fade-in stagger-1">
        <p class="metric-label">TOTAL EMISSIONS</p>
        <p class="metric-value">{total_emissions:,.2f}</p>
        <p class="metric-label">MILLION METRIC TONS</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="futuristic-card fade-in stagger-2">
        <p class="metric-label">AVERAGE</p>
        <p class="metric-value">{avg_emissions:.3f}</p>
        <p class="metric-label">MILLION METRIC TONS</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="futuristic-card fade-in stagger-3">
        <p class="metric-label">MAXIMUM</p>
        <p class="metric-value" style="color: #ff00ff !important; text-shadow: 0 0 20px rgba(255,0,255,0.5) !important;">{max_emission:.3f}</p>
        <p class="metric-label">MILLION METRIC TONS</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="futuristic-card fade-in stagger-4">
        <p class="metric-label">MINIMUM</p>
        <p class="metric-value" style="color: #00ffd5 !important; text-shadow: 0 0 20px rgba(0,255,213,0.5) !important;">{min_emission:.3f}</p>
        <p class="metric-label">MILLION METRIC TONS</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["EMISSIONS TIMELINE", "BY SECTOR", "BY FUEL", "BY STATE"])

with tab1:
    st.markdown("""
    <div class="futuristic-card" style="margin-bottom: 20px;">
        <p style="color: #888; font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; margin: 0;">
            // The story: A half-century of American emissions reveals a nation's energy evolution. 
            From the industrial boom of the 1970s to the clean energy push of today, 
            this timeline captures the ebbs and flows of our carbon footprint.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    yearly = filtered_df.groupby('period')['value'].sum().reset_index().sort_values('period')
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=yearly['period'], y=yearly['value'],
        mode='lines+markers',
        line=dict(color='#00ff7f', width=2.5),
        marker=dict(
            size=10, 
            color='#00ff7f', 
            line=dict(color='#050508', width=1.5),
            symbol='circle'
        ),
        hovertemplate='<b>%{x}</b><br>Emissions: %{y:,.2f} M MT<extra></extra>'
    ))
    
    if len(yearly) > 2:
        peak_idx = yearly['value'].idxmax()
        peak_year = yearly.loc[peak_idx, 'period']
        peak_val = yearly.loc[peak_idx, 'value']
        fig.add_annotation(
            x=peak_year, y=peak_val,
            text=f"Peak<br>{peak_year}<br>{peak_val:,.0f}",
            showarrow=True,
            arrowhead=2,
            arrowcolor='#ff00ff',
            font=dict(family='JetBrains Mono', size=10, color='#ff00ff'),
            bgcolor='rgba(10,10,20,0.8)',
            bordercolor='#ff00ff'
        )
        
        if 2020 in yearly['period'].values:
            covid_val = yearly[yearly['period']==2020]['value'].values[0]
            fig.add_annotation(
                x=2020, y=covid_val,
                text=f"COVID<br>2020<br>{covid_val:,.0f}",
                showarrow=True,
                arrowhead=2,
                arrowcolor='#00ffd5',
                font=dict(family='JetBrains Mono', size=10, color='#00ffd5'),
                bgcolor='rgba(10,10,20,0.8)',
                bordercolor='#00ffd5'
            )
    
    fig.update_layout(
        title=dict(text='CO2 EMISSIONS OVER TIME', font=dict(family='JetBrains Mono', size=16, color='#00ff7f'), x=0.5),
        xaxis_title=dict(text='YEAR', font=dict(family='JetBrains Mono', size=12, color='#00ff7f')),
        yaxis_title=dict(text='EMISSIONS (MILLION MT)', font=dict(family='JetBrains Mono', size=12, color='#00ff7f')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(family='JetBrains Mono', color='#fff'),
        xaxis=dict(
            gridcolor='rgba(0,255,127,0.1)', 
            tickfont=dict(color='#fff'), 
            tickformat='d',
            dtick=2,
            range=[yearly['period'].min()-1, yearly['period'].max()+1]
        ),
        yaxis=dict(
            gridcolor='rgba(0,255,127,0.1)', 
            tickfont=dict(color='#fff'),
        ),
        hovermode='x unified',
        dragmode='zoom'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    col_trend1, col_trend2, col_trend3 = st.columns(3)
    with col_trend1:
        first_year = yearly.iloc[0]['value'] if len(yearly) > 0 else 0
        last_year = yearly.iloc[-1]['value'] if len(yearly) > 0 else 0
        change = ((last_year - first_year) / first_year) * 100 if first_year > 0 else 0
        st.metric("Change Since 1970", f"{change:+.1f}%")
    with col_trend2:
        if len(yearly) > 0:
            peak_year = yearly.loc[yearly['value'].idxmax(), 'period']
            peak_value = yearly['value'].max()
            st.metric("Peak Year", f"{int(peak_year)}", f"{peak_value:.0f}M MT")
    with col_trend3:
        avg_recent = yearly[yearly['period'] >= 2010]['value'].mean() if len(yearly[yearly['period'] >= 2010]) > 0 else 0
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
    <div class="futuristic-card" style="margin-bottom: 20px;">
        <p style="color: #888; font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; margin: 0;">
            // The story: America's carbon story is written in its sectors. Transportation fuels our economy 
            but also feeds our emissions. The battle between progress and preservation plays out in these numbers.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    sector_data = filtered_df.groupby('sector-name')['value'].sum().reset_index().sort_values('value', ascending=True)
    
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

with tab3:
    st.markdown("""
    <div class="futuristic-card" style="margin-bottom: 20px;">
        <p style="color: #888; font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; margin: 0;">
            // The story: Coal, gas, and oil—each fuel tells a different part of America's energy journey. 
            Watch how we've shifted over decades, moving from the dirty past toward a cleaner horizon.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    fuel_data = filtered_df.groupby('fuel-name')['value'].sum().reset_index().sort_values('value', ascending=False)
    
    fig = px.pie(fuel_data, values='value', names='fuel-name',
                 title='EMISSIONS BY FUEL',
                 color_discrete_sequence=['#00ff7f', '#ff00ff', '#00ffd5', '#00cc66'])
    fig.update_layout(
        title=dict(font=dict(family='JetBrains Mono', size=16, color='#00ff7f'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='JetBrains Mono', color='#fff')
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.markdown("""
    <div class="futuristic-card" style="margin-bottom: 20px;">
        <p style="color: #888; font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; margin: 0;">
            // The story: Every state tells its own emission story. Texas leads the pack as an energy giant, 
            while smaller states punch above their weight in the national carbon conversation.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    state_data = filtered_df.groupby('state-name')['value'].sum().reset_index().sort_values('value', ascending=False).head(20)
    
    fig = px.bar(state_data, x='value', y='state-name', orientation='h',
               title='TOP 20 STATES BY EMISSIONS',
               labels={'value': 'EMISSIONS', 'state-name': 'STATE'},
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