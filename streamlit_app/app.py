import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import importlib
if 'src.utils' in sys.modules:
    importlib.reload(sys.modules['src.utils'])
from src import utils
from streamlit_app.components import inject_theme, page_header, metric_card, kpi_tile, story_card, section_divider, sidebar_navigation

st.set_page_config(
    page_title="USA CO2 Emissions",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_theme()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding:40px 20px 28px;">
    <h1>USA Carbon Emissions</h1>
    <p style="color:rgba(255,255,255,0.35); font-size:0.85rem; letter-spacing:5px;
              font-family:'JetBrains Mono',monospace; margin:0;">
        HALF A CENTURY OF AMERICAN EMISSIONS DATA
    </p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ── Data Loading ───────────────────────────────────────────────────────────────
try:
    df = utils.filter_state_level_data(utils.load_raw_data())
    states, sectors, fuels, years = utils.get_unique_values()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# ── Sidebar Filters ────────────────────────────────────────────────────────────
with st.sidebar:
    sidebar_navigation("Dashboard")

    st.markdown("---")
    st.markdown("""
    <p style="font-family:'JetBrains Mono',monospace; font-size:0.72rem;
              letter-spacing:2px; color:#00ff7f; text-transform:uppercase;">
        // Filters
    </p>
    """, unsafe_allow_html=True)

    selected_states  = st.multiselect("States",  states,  default=states[:3])
    selected_sectors = st.multiselect("Sectors", sectors, default=[sectors[0]])
    selected_fuels   = st.multiselect("Fuels",   fuels,   default=[fuels[0]])

    st.markdown("---")
    total_recs = len(df)
    yr_min, yr_max = int(min(years)), int(max(years))
    st.markdown(f"""
    <div style="padding:14px; background:rgba(0,255,127,0.05);
                border:1px solid rgba(0,255,127,0.15); border-radius:8px; text-align:center;">
        <p style="margin:0; color:#00ff7f; font-family:'JetBrains Mono',monospace;
                  font-size:0.65rem; letter-spacing:2px; text-transform:uppercase;">Dataset</p>
        <p style="margin:8px 0 0; color:#fff; font-family:'JetBrains Mono',monospace;
                  font-size:0.82rem;">
            {total_recs:,} records<br>
            {len(states)} states · {yr_min}–{yr_max}
        </p>
    </div>
    """, unsafe_allow_html=True)

# ── Filter Data ────────────────────────────────────────────────────────────────
filtered_df = df.copy()
if selected_states:
    filtered_df = filtered_df[filtered_df['state-name'].isin(selected_states)]
if selected_sectors:
    filtered_df = filtered_df[filtered_df['sector-name'].isin(selected_sectors)]
if selected_fuels:
    filtered_df = filtered_df[filtered_df['fuel-name'].isin(selected_fuels)]
analysis_df = utils.filter_detail_rows(filtered_df)

if analysis_df.empty:
    st.warning("No state-level detail records match the selected filters.")
    st.stop()

# ── KPI Row ────────────────────────────────────────────────────────────────────
full_yearly = df.groupby('period')['value'].sum().reset_index().sort_values('period')
total_all   = df['value'].sum()
total_filt  = analysis_df['value'].sum()
avg_filt    = analysis_df['value'].mean() if len(analysis_df) > 0 else 0
yearly_filt = analysis_df.groupby('period')['value'].sum().reset_index().sort_values('period')
peak_source = yearly_filt if len(yearly_filt) > 0 else full_yearly
if len(peak_source) > 0:
    peak_yr_row = peak_source.loc[peak_source['value'].idxmax()]
    peak_yr, peak_val = int(peak_yr_row['period']), float(peak_yr_row['value'])
else:
    peak_yr, peak_val = yr_min, 0.0

# Trend: compare last 5 years avg to first 5 years avg (filtered)
if len(yearly_filt) >= 10:
    trend_pct = ((yearly_filt['value'].iloc[-5:].mean() - yearly_filt['value'].iloc[:5].mean())
                 / yearly_filt['value'].iloc[:5].mean() * 100)
    trend_str = f"{trend_pct:+.1f}%"
    trend_pos = trend_pct < 0  # declining = good = green
else:
    trend_str, trend_pos = "N/A", None

col1, col2, col3, col4 = st.columns(4)
tiles = [
    ("TOTAL EMISSIONS", f"{total_filt:,.0f}", "M MT", None, None, 0.0),
    ("AVG PER RECORD", f"{avg_filt:.2f}", "M MT", None, None, 0.08),
    ("PEAK YEAR", str(peak_yr), f"{peak_val:,.0f} M MT", None, None, 0.16),
    ("LONG-TERM TREND", trend_str, "vs. baseline", trend_str != "N/A" and not trend_pos, trend_pos if trend_str != "N/A" else None, 0.24),
]
for col, (lbl, val, unit, _, dpos, delay) in zip([col1, col2, col3, col4], tiles):
    with col:
        st.markdown(metric_card(lbl, val, unit, False, delay), unsafe_allow_html=True)

section_divider()

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 TIMELINE", "🏭 BY SECTOR", "⛽ BY FUEL", "🗺️ USA MAP", "🏆 TOP STATES"
])

# ── TAB 1: Timeline ─────────────────────────────────────────────────────────
with tab1:
    yearly_filt = analysis_df.groupby('period')['value'].sum().reset_index().sort_values('period')

    # Story card
    first_v = float(yearly_filt.iloc[0]['value']) if len(yearly_filt) else 0.0
    last_v  = float(yearly_filt.iloc[-1]['value']) if len(yearly_filt) else 0.0
    chg_pct = (last_v - first_v) / first_v * 100 if first_v else 0.0
    st.markdown(story_card(
        "📖", "THE STORY",
        f"From <b>{int(yearly_filt.iloc[0]['period'])}</b> to <b>{int(yearly_filt.iloc[-1]['period'])}</b>, "
        f"the selected state emissions {'declined' if chg_pct < 0 else 'rose'} by <b>{abs(chg_pct):.1f}%</b>. "
        f"The peak came in <b>{peak_yr}</b> at <b>{peak_val:,.0f} M MT</b>. "
        "The COVID-19 pandemic caused the steepest single-year drop in recorded history in 2020, "
        "followed by a partial rebound. The long-term trend points toward gradual decarbonization "
        "driven by coal plant closures and the rise of renewable energy."
    ), unsafe_allow_html=True)

    fig = go.Figure()

    # Confidence band for filtered data (rolling std)
    if len(yearly_filt) > 5:
        roll_std = yearly_filt['value'].rolling(3, min_periods=1).std().fillna(0)
        upper = yearly_filt['value'] + roll_std
        lower = (yearly_filt['value'] - roll_std).clip(lower=0)
        fig.add_trace(go.Scatter(
            x=list(yearly_filt['period']) + list(yearly_filt['period'])[::-1],
            y=list(upper) + list(lower)[::-1],
            fill='toself', fillcolor='rgba(0,255,127,0.07)',
            line_color='rgba(0,0,0,0)', showlegend=False, hoverinfo='skip', name='Band'
        ))

    # Filtered line
    fig.add_trace(go.Scatter(
        x=yearly_filt['period'], y=yearly_filt['value'],
        mode='lines+markers', name='Selected Filter',
        line=dict(color='#00ff7f', width=2.5),
        marker=dict(size=7, color='#00ff7f', line=dict(color='#050508', width=1.5)),
        hovertemplate='<b>%{x}</b><br>%{y:,.2f} M MT<extra></extra>'
    ))

    # Annotations
    if len(yearly_filt) > 2:
        # Peak
        fig.add_annotation(x=peak_yr, y=peak_val,
            text=f"<b>PEAK {peak_yr}</b><br>{peak_val:,.0f}",
            showarrow=True, arrowhead=2, arrowcolor='#ff00ff',
            font=dict(family='JetBrains Mono', size=10, color='#ff00ff'),
            bgcolor='rgba(8,8,20,0.85)', bordercolor='#ff00ff', ax=40, ay=-50)
        # COVID 2020
        if 2020 in yearly_filt['period'].values:
            covid_val = float(yearly_filt[yearly_filt['period'] == 2020]['value'].iloc[0])
            fig.add_annotation(x=2020, y=covid_val,
                text="<b>COVID-19</b><br>Record drop",
                showarrow=True, arrowhead=2, arrowcolor='#00ffd5',
                font=dict(family='JetBrains Mono', size=10, color='#00ffd5'),
                bgcolor='rgba(8,8,20,0.85)', bordercolor='#00ffd5', ax=-50, ay=-40)

    fig.update_layout(
        title=dict(text='CO₂ EMISSIONS OVER TIME', font=dict(family='Orbitron', size=14, color='#00ff7f'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#fff'),
        xaxis=dict(gridcolor='rgba(0,255,127,0.08)', tickfont=dict(color='#aaa'), title='YEAR',
                   tickformat='d', dtick=5),
        yaxis=dict(gridcolor='rgba(0,255,127,0.08)', tickfont=dict(color='#aaa'), title='MILLION METRIC TONS'),
        legend=dict(font=dict(family='JetBrains Mono', color='#aaa', size=11)),
        hovermode='x unified', height=420, margin=dict(l=10, r=10, t=50, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Change Since 1970", f"{chg_pct:+.1f}%")
    with c2:
        st.metric("Peak Year", f"{peak_yr}", f"{peak_val:,.0f} M MT")
    with c3:
        recent_avg = float(yearly_filt[yearly_filt['period'] >= 2015]['value'].mean())
        st.metric("Avg 2015–2022", f"{recent_avg:,.0f} M MT")

# ── TAB 2: By Sector ─────────────────────────────────────────────────────────
with tab2:
    sector_source = analysis_df
    sector_data = sector_source.groupby('sector-name')['value'].sum().reset_index().sort_values('value', ascending=True)
    if sector_data.empty:
        st.info("No sector data available for the selected filters.")
        st.stop()
    top_sector = sector_data.iloc[-1]['sector-name']
    top_val_s  = sector_data.iloc[-1]['value']

    st.markdown(story_card(
        "🏭", "SECTOR BREAKDOWN",
        f"<b>{top_sector}</b> accounts for the largest cumulative share of US CO₂ emissions. "
        "Transportation has overtaken electricity generation as the top source since 2016, "
        "driven by car dependency and aviation growth. Industrial emissions remain stubbornly "
        "high due to cement, steel, and chemical manufacturing. The residential sector shows "
        "modest declines as building codes and appliances improve."
    ), unsafe_allow_html=True)

    colors = ['#00ff7f', '#00ffd5', '#ff00ff', '#ffaa00', '#00aaff', '#ff5555']
    fig = go.Figure(go.Bar(
        y=sector_data['sector-name'],
        x=sector_data['value'],
        orientation='h',
        marker=dict(
            color=colors[:len(sector_data)],
            line=dict(color='rgba(0,0,0,0.3)', width=1)
        ),
        text=[f"{v:,.0f}" for v in sector_data['value']],
        textposition='outside',
        textfont=dict(family='JetBrains Mono', size=10, color='rgba(255,255,255,0.6)'),
        hovertemplate='<b>%{y}</b><br>%{x:,.2f} M MT<extra></extra>'
    ))
    fig.update_layout(
        title=dict(text='CUMULATIVE EMISSIONS BY SECTOR', font=dict(family='Orbitron', size=14, color='#00ff7f'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#fff'),
        xaxis=dict(gridcolor='rgba(0,255,127,0.08)', tickfont=dict(color='#aaa'), title='MILLION METRIC TONS'),
        yaxis=dict(tickfont=dict(color='#ddd', size=11)),
        height=380, margin=dict(l=10, r=80, t=50, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Sector trend over time
    sector_trend = sector_source.groupby(['period', 'sector-name'])['value'].sum().reset_index()
    top3_sectors = sector_data.tail(3)['sector-name'].tolist()
    fig2 = go.Figure()
    sc_colors = ['#00ff7f', '#ff00ff', '#00ffd5']
    for i, sec in enumerate(top3_sectors):
        d = sector_trend[sector_trend['sector-name'] == sec].sort_values('period')
        fig2.add_trace(go.Scatter(
            x=d['period'], y=d['value'], mode='lines',
            name=sec.replace(' carbon dioxide emissions', ''),
            line=dict(color=sc_colors[i % 3], width=2),
            hovertemplate=f'<b>{sec[:20]}…</b><br>%{{x}}: %{{y:,.2f}} M MT<extra></extra>'
        ))
    fig2.update_layout(
        title=dict(text='TOP 3 SECTORS OVER TIME', font=dict(family='Orbitron', size=13, color='#00ff7f'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#fff'),
        xaxis=dict(gridcolor='rgba(0,255,127,0.08)', tickfont=dict(color='#aaa')),
        yaxis=dict(gridcolor='rgba(0,255,127,0.08)', tickfont=dict(color='#aaa')),
        legend=dict(font=dict(family='JetBrains Mono', color='#aaa', size=10)),
        height=320, margin=dict(l=10, r=10, t=50, b=10)
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── TAB 3: By Fuel ───────────────────────────────────────────────────────────
with tab3:
    fuel_source = analysis_df
    fuel_data = fuel_source.groupby('fuel-name')['value'].sum().reset_index().sort_values('value', ascending=False)
    if fuel_data.empty:
        st.info("No fuel data available for the selected filters.")
        st.stop()
    top_fuel = fuel_data.iloc[0]['fuel-name']

    st.markdown(story_card(
        "⛽", "FUEL MIX",
        f"<b>{top_fuel}</b> is the dominant fuel in the dataset. Coal, once king of American energy, "
        "has seen its share collapse as cheap natural gas and renewables take over. Petroleum remains "
        "dominant in transportation. Natural gas, while cleaner than coal, has expanded significantly "
        "and now represents the largest single source of US power-sector CO₂."
    ), unsafe_allow_html=True)

    f_colors = ['#00ff7f', '#ff00ff', '#00ffd5', '#ffaa00', '#00aaff', '#ff5555', '#aaaaff']
    fig = go.Figure(go.Pie(
        labels=fuel_data['fuel-name'],
        values=fuel_data['value'],
        hole=0.5,
        marker=dict(colors=f_colors[:len(fuel_data)], line=dict(color='#050508', width=2)),
        textinfo='label+percent',
        textfont=dict(family='JetBrains Mono', size=11),
        hovertemplate='<b>%{label}</b><br>%{value:,.2f} M MT (%{percent})<extra></extra>'
    ))
    fig.update_layout(
        title=dict(text='EMISSIONS BY FUEL TYPE', font=dict(family='Orbitron', size=14, color='#00ff7f'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#fff'),
        legend=dict(font=dict(family='JetBrains Mono', color='#aaa', size=11)),
        height=420, margin=dict(l=10, r=10, t=50, b=10)
    )
    fig.add_annotation(text="FUEL<br>SHARE", x=0.5, y=0.5, font=dict(family='Orbitron', size=14, color='#00ff7f'), showarrow=False)
    st.plotly_chart(fig, use_container_width=True)

    # Fuel trend
    fuel_trend = fuel_source.groupby(['period', 'fuel-name'])['value'].sum().reset_index()
    top3_fuels = fuel_data.head(4)['fuel-name'].tolist()
    fig2 = go.Figure()
    for i, f in enumerate(top3_fuels):
        d = fuel_trend[fuel_trend['fuel-name'] == f].sort_values('period')
        fig2.add_trace(go.Scatter(
            x=d['period'], y=d['value'], mode='lines',
            name=f, line=dict(color=f_colors[i % len(f_colors)], width=2),
        ))
    fig2.update_layout(
        title=dict(text='FUEL EMISSIONS TREND OVER TIME', font=dict(family='Orbitron', size=13, color='#00ff7f'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#fff'),
        xaxis=dict(gridcolor='rgba(0,255,127,0.08)', tickfont=dict(color='#aaa')),
        yaxis=dict(gridcolor='rgba(0,255,127,0.08)', tickfont=dict(color='#aaa')),
        legend=dict(font=dict(family='JetBrains Mono', color='#aaa', size=10)),
        height=300, margin=dict(l=10, r=10, t=50, b=10)
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── TAB 4: USA Map ───────────────────────────────────────────────────────────
with tab4:
    # US state abbreviation map
    STATE_ABBR = {
        'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA',
        'Colorado':'CO','Connecticut':'CT','Delaware':'DE','Florida':'FL','Georgia':'GA',
        'Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA',
        'Kansas':'KS','Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD',
        'Massachusetts':'MA','Michigan':'MI','Minnesota':'MN','Mississippi':'MS',
        'Missouri':'MO','Montana':'MT','Nebraska':'NE','Nevada':'NV','New Hampshire':'NH',
        'New Jersey':'NJ','New Mexico':'NM','New York':'NY','North Carolina':'NC',
        'North Dakota':'ND','Ohio':'OH','Oklahoma':'OK','Oregon':'OR','Pennsylvania':'PA',
        'Rhode Island':'RI','South Carolina':'SC','South Dakota':'SD','Tennessee':'TN',
        'Texas':'TX','Utah':'UT','Vermont':'VT','Virginia':'VA','Washington':'WA',
        'West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY',
        'District of Columbia':'DC'
    }

    st.markdown(story_card(
        "🗺️", "GEOGRAPHIC DISTRIBUTION",
        "This map reveals which states are the biggest contributors to US CO₂ emissions. "
        "<b>Texas</b> dominates due to its massive oil & gas sector and large population. "
        "<b>California</b> and <b>Florida</b> follow, though both have aggressive decarbonization targets. "
        "The industrial Midwest (Ohio, Indiana, Pennsylvania) remains a heavy emitter. "
        "States in the Mountain West and New England consistently rank lowest."
    ), unsafe_allow_html=True)

    map_year = st.slider("Select Year", min_value=yr_min, max_value=yr_max, value=yr_max, step=1)

    map_source = utils.filter_detail_rows(df[df['period'] == map_year])
    state_year = map_source.groupby('state-name')['value'].sum().reset_index()
    state_year['abbr'] = state_year['state-name'].map(STATE_ABBR)
    state_year = state_year.dropna(subset=['abbr'])

    fig = go.Figure(go.Choropleth(
        locations=state_year['abbr'],
        z=state_year['value'],
        locationmode='USA-states',
        colorscale=[[0, '#050508'], [0.3, '#003320'], [0.6, '#00cc66'], [1.0, '#00ff7f']],
        colorbar=dict(
            title='M MT CO₂',
            titlefont=dict(family='JetBrains Mono', color='#aaa', size=11),
            tickfont=dict(family='JetBrains Mono', color='#aaa', size=10),
            bgcolor='rgba(5,5,8,0.8)',
            bordercolor='rgba(0,255,127,0.3)',
        ),
        hovertemplate='<b>%{location}</b><br>%{z:,.2f} M MT<extra></extra>',
        marker_line_color='rgba(0,255,127,0.3)',
        marker_line_width=0.8
    ))
    fig.update_layout(
        geo=dict(
            scope='usa',
            bgcolor='rgba(0,0,0,0)',
            lakecolor='rgba(0,0,0,0)',
            landcolor='rgba(10,10,25,0.8)',
            subunitcolor='rgba(0,255,127,0.2)',
            coastlinecolor='rgba(0,255,127,0.2)',
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#fff'),
        title=dict(text=f'CO₂ EMISSIONS BY STATE — {map_year}',
                   font=dict(family='Orbitron', size=14, color='#00ff7f'), x=0.5),
        height=480, margin=dict(l=0, r=0, t=50, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Top/bottom states
    top5 = state_year.nlargest(5, 'value')[['state-name', 'abbr', 'value']]
    bot5 = state_year.nsmallest(5, 'value')[['state-name', 'abbr', 'value']]
    col_t, col_b = st.columns(2)
    with col_t:
        st.markdown(f"**🔴 Top 5 Emitters — {map_year}**")
        st.dataframe(top5.rename(columns={'state-name': 'State', 'abbr': 'Code', 'value': 'M MT CO₂'}),
                     hide_index=True, use_container_width=True)
    with col_b:
        st.markdown(f"**🟢 Lowest 5 Emitters — {map_year}**")
        st.dataframe(bot5.rename(columns={'state-name': 'State', 'abbr': 'Code', 'value': 'M MT CO₂'}),
                     hide_index=True, use_container_width=True)

# ── TAB 5: Top States Bar ─────────────────────────────────────────────────────
with tab5:
    state_source = utils.filter_detail_rows(df)
    state_total = state_source.groupby('state-name')['value'].sum().reset_index().sort_values('value', ascending=False)
    if state_total.empty:
        st.info("No state ranking data available.")
        st.stop()
    top20 = state_total.head(20)
    top_state = top20.iloc[0]['state-name']
    top_state_val = top20.iloc[0]['value']

    st.markdown(story_card(
        "🏆", "STATE RANKINGS",
        f"<b>{top_state}</b> leads all states with <b>{top_state_val:,.0f} M MT</b> of cumulative CO₂ "
        "across the dataset period — nearly double the second-ranked state. "
        "The top 5 states together account for over 35% of all US emissions. "
        "Notice how smaller states that have heavy industrial or energy sectors "
        "(West Virginia, Wyoming) often punch far above their population weight."
    ), unsafe_allow_html=True)

    bar_colors = [f'rgba(0,255,127,{max(0.35, 1 - i * 0.04)})' for i in range(len(top20))]
    bar_colors[0] = '#00ff7f'

    fig = go.Figure(go.Bar(
        y=top20['state-name'][::-1],
        x=top20['value'][::-1],
        orientation='h',
        marker=dict(color=bar_colors[::-1], line=dict(color='rgba(0,0,0,0.2)', width=0.5)),
        text=[f"{v:,.0f}" for v in top20['value'][::-1]],
        textposition='outside',
        textfont=dict(family='JetBrains Mono', size=10, color='rgba(255,255,255,0.55)'),
        hovertemplate='<b>%{y}</b><br>%{x:,.2f} M MT<extra></extra>'
    ))
    fig.update_layout(
        title=dict(text='TOP 20 STATES — CUMULATIVE EMISSIONS', font=dict(family='Orbitron', size=14, color='#00ff7f'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#fff'),
        xaxis=dict(gridcolor='rgba(0,255,127,0.08)', tickfont=dict(color='#aaa'), title='MILLION METRIC TONS'),
        yaxis=dict(tickfont=dict(color='#ddd', size=11)),
        height=540, margin=dict(l=10, r=90, t=50, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("""
<p style="text-align:center; color:rgba(255,255,255,0.2); font-family:'JetBrains Mono',monospace;
          font-size:0.7rem; letter-spacing:2px;">
    DATA SOURCE: U.S. ENERGY INFORMATION ADMINISTRATION (EIA) · UNITS: MILLION METRIC TONS CO₂
</p>
""", unsafe_allow_html=True)
