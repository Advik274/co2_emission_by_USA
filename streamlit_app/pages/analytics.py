import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ab_testing import ab_testing

st.set_page_config(page_title="Analytics & Insights", page_icon="📈", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

:root {
    --primary: #00ffd5;
    --secondary: #ff00aa;
    --bg-dark: #050508;
}

.stApp {
    background: linear-gradient(180deg, #050508 0%, #0a0a15 50%, #050508 100%) !important;
    font-family: 'Rajdhani', sans-serif !important;
    color: #ffffff !important;
}

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

h1, h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    background: linear-gradient(90deg, #00ffd5, #00b8a9, #00ffd5);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 3s linear infinite;
}

@keyframes shimmer {
    to { background-position: 200% center; }
}

h1 { font-size: 2rem !important; }

.futuristic-card {
    background: linear-gradient(135deg, rgba(20, 20, 35, 0.9) 0%, rgba(10, 10, 20, 0.95) 100%) !important;
    border: 1px solid rgba(0, 255, 213, 0.2) !important;
    border-radius: 20px !important;
    padding: 25px !important;
    transition: all 0.3s ease !important;
}

.futuristic-card:hover {
    border-color: #00ffd5 !important;
    box-shadow: 0 10px 40px rgba(0, 255, 213, 0.15) !important;
}

.stat-card {
    background: linear-gradient(135deg, rgba(0, 255, 213, 0.1) 0%, rgba(15, 15, 25, 0.95) 100%) !important;
    border: 1px solid rgba(0, 255, 213, 0.3) !important;
    border-radius: 15px !important;
    padding: 25px !important;
    text-align: center;
}

.stat-value {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 2.5rem !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #00ffd5, #00b8a9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.stat-label {
    color: rgba(255, 255, 255, 0.5) !important;
    font-size: 0.8rem !important;
    letter-spacing: 2px !important;
}

.insight-box {
    background: linear-gradient(135deg, rgba(0,255,213,0.1) 0%, rgba(15,15,25,0.95) 100%);
    padding: 15px;
    border-radius: 12px;
    border-left: 3px solid #00ffd5;
    margin: 10px 0;
}
</style>

<div class="bg-grid"></div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; padding: 40px 20px 30px;">
    <h1>Analytics & Insights</h1>
    <p style="color: rgba(255,255,255,0.4); font-size: 1rem; letter-spacing: 4px; margin-top: 10px;">
        A/B TEST RESULTS & USAGE STATISTICS
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("### A/B TEST RESULTS")

stats = ab_testing.get_experiment_stats('prediction_ui')

if stats and stats.get('events'):
    col1, col2, col3, col4 = st.columns(4)
    
    total_events = len(stats['events'])
    unique_users = len(set([e['user_id'] for e in stats['events']]))
    
    variant_counts = {}
    for event in stats['events']:
        v = event.get('variant', 'unknown')
        variant_counts[v] = variant_counts.get(v, 0) + 1
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-value">{total_events}</p>
            <p class="stat-label">TOTAL EVENTS</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-value">{unique_users}</p>
            <p class="stat-label">UNIQUE USERS</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        variant_a = variant_counts.get('A', 0)
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-value" style="background: linear-gradient(135deg, #4ecdc4, #45b7aa); -webkit-background-clip: text;">{variant_a}</p>
            <p class="stat-label">VARIANT A</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        variant_b = variant_counts.get('B', 0)
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-value" style="background: linear-gradient(135deg, #ff00aa, #ff6b9d); -webkit-background-clip: text;">{variant_b}</p>
            <p class="stat-label">VARIANT B</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        event_types = {}
        for event in stats['events']:
            e = event.get('event', 'unknown')
            event_types[e] = event_types.get(e, 0) + 1
        
        fig_events = go.Figure(data=[
            go.Pie(labels=list(event_types.keys()), values=list(event_types.keys()),
                   hole=0.5, marker_colors=['#00ffd5', '#4ecdc4', '#ff00aa', '#ffa502'])
        ])
        fig_events.update_layout(
            title=dict(text='EVENT DISTRIBUTION', font=dict(family='Orbitron', size=14, color='#00ffd5'), x=0.5),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Rajdhani', color='#fff')
        )
        st.plotly_chart(fig_events, use_container_width=True)
    
    with col_chart2:
        variant_event_types = {'A': {}, 'B': {}}
        for event in stats['events']:
            v = event.get('variant', 'unknown')
            e = event.get('event', 'unknown')
            if v in variant_event_types:
                variant_event_types[v][e] = variant_event_types[v].get(e, 0) + 1
        
        events = list(set([e['event'] for e in stats['events']]))
        
        fig_compare = go.Figure()
        for variant in ['A', 'B']:
            values = [variant_event_types[variant].get(e, 0) for e in events]
            fig_compare.add_trace(go.Bar(
                name=f'Variant {variant}',
                x=events,
                y=values,
                marker_color='#00ffd5' if variant == 'A' else '#ff00aa'
            ))
        
        fig_compare.update_layout(
            title=dict(text='EVENTS BY VARIANT', font=dict(family='Orbitron', size=14, color='#00ffd5'), x=0.5),
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Rajdhani', color='#fff'),
            legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#fff'))
        )
        st.plotly_chart(fig_compare, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("### CONVERSION FUNNEL")
    
    funnel_data = {}
    for event in stats['events']:
        e = event.get('event', 'unknown')
        v = event.get('variant', 'unknown')
        if v not in funnel_data:
            funnel_data[v] = {}
        funnel_data[v][e] = funnel_data[v].get(e, 0) + 1
    
    for variant in ['A', 'B']:
        st.markdown(f"**Variant {variant}**")
        if variant in funnel_data:
            for event_name, count in sorted(funnel_data[variant].items(), key=lambda x: x[1], reverse=True):
                st.markdown(f"""
                <div class="insight-box">
                    <strong>{event_name}</strong>: {count}
                </div>
                """, unsafe_allow_html=True)
    
else:
    st.info("No A/B test data yet. Tracking is ready!")

st.markdown("---")

st.markdown("### USER FEEDBACK")

feedback = ab_testing.get_feedback_stats()

if feedback:
    col_fb1, col_fb2 = st.columns(2)
    
    with col_fb1:
        feedback_types = {}
        for f in feedback:
            ft = f.get('feedback_type', 'unknown')
            feedback_types[ft] = feedback_types.get(ft, 0) + 1
        
        fig_fb = go.Figure(data=[
            go.Bar(x=list(feedback_types.keys()), y=list(feedback_types.values()),
                   marker_color='#00ffd5')
        ])
        fig_fb.update_layout(
            title=dict(text='FEEDBACK DISTRIBUTION', font=dict(family='Orbitron', size=14, color='#00ffd5'), x=0.5),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Rajdhani', color='#fff')
        )
        st.plotly_chart(fig_fb, use_container_width=True)
    
    with col_fb2:
        positive = len([f for f in feedback if f.get('feedback_type') == 'positive'])
        negative = len([f for f in feedback if f.get('feedback_type') == 'negative'])
        neutral = len([f for f in feedback if f.get('feedback_type') == 'neutral'])
        
        sentiment_data = go.Figure(data=[
            go.Pie(labels=['Positive', 'Negative', 'Neutral'], 
                   values=[positive, negative, neutral],
                   hole=0.5,
                   marker_colors=['#00ffd5', '#ff00aa', '#ffa502'])
        ])
        sentiment_data.update_layout(
            title=dict(text='SENTIMENT ANALYSIS', font=dict(family='Orbitron', size=14, color='#00ffd5'), x=0.5),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Rajdhani', color='#fff')
        )
        st.plotly_chart(sentiment_data, use_container_width=True)
    
    with st.expander("VIEW ALL FEEDBACK"):
        feedback_df = pd.DataFrame(feedback)
        st.dataframe(feedback_df, use_container_width=True)
        
        csv = feedback_df.to_csv(index=False)
        st.download_button("DOWNLOAD CSV", csv, "feedback.csv", "text/csv")

else:
    st.info("No feedback yet.")

st.markdown("---")

st.markdown("### TRACKED EVENTS")

st.markdown("""
<div class="futuristic-card">
    <table style="width: 100%; color: #fff; font-family: 'Rajdhani', sans-serif;">
        <tr style="border-bottom: 1px solid rgba(0,255,213,0.2);">
            <td style="padding: 12px; color: #00ffd5;">page_view</td>
            <td style="padding: 12px; color: #888;">User visits prediction page</td>
        </tr>
        <tr style="border-bottom: 1px solid rgba(0,255,213,0.2);">
            <td style="padding: 12px; color: #00ffd5;">generate_click</td>
            <td style="padding: 12px; color: #888;">User clicks prediction button</td>
        </tr>
        <tr style="border-bottom: 1px solid rgba(0,255,213,0.2);">
            <td style="padding: 12px; color: #00ffd5;">prediction_made</td>
            <td style="padding: 12px; color: #888;">Prediction successfully generated</td>
        </tr>
        <tr>
            <td style="padding: 12px; color: #00ffd5;">feedback</td>
            <td style="padding: 12px; color: #888;">User provides feedback</td>
        </tr>
    </table>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("Data stored locally in data/ab_test_experiments.json")