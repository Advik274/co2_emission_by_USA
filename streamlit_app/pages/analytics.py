import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ab_testing import ab_testing

st.set_page_config(page_title="Analytics & Insights", page_icon="📈", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    h1, h2, h3 { color: #00d4aa !important; }
    .stat-card {
        background: linear-gradient(135deg, #1e1e2f 0%, #2d2d44 100%);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #00d4aa33;
        text-align: center;
    }
    .insight-box {
        background: #1a1a2e;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #00d4aa;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Analytics & Insights")
st.markdown("A/B test results, user feedback analysis, and usage statistics")

st.markdown("---")

st.markdown("### 🔬 A/B Test Results")

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
            <h3 style="color:#fff; margin:0;">{total_events}</h3>
            <p style="color:#888; margin:0;">Total Events</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <h3 style="color:#fff; margin:0;">{unique_users}</h3>
            <p style="color:#888; margin:0;">Unique Users</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        variant_a_count = variant_counts.get('A', 0)
        st.markdown(f"""
        <div class="stat-card">
            <h3 style="color:#4ecdc4; margin:0;">{variant_a_count}</h3>
            <p style="color:#888; margin:0;">Variant A (Classic)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        variant_b_count = variant_counts.get('B', 0)
        st.markdown(f"""
        <div class="stat-card">
            <h3 style="color:#ff6b6b; margin:0;">{variant_b_count}</h3>
            <p style="color:#888; margin:0;">Variant B (Modern)</p>
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
            go.Pie(labels=list(event_types.keys()), values=list(event_types.values()),
                   hole=0.4, marker_colors=['#00d4aa', '#4ecdc4', '#ff6b6b', '#ffa502'])
        ])
        fig_events.update_layout(
            title='Event Distribution',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#fff'
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
                marker_color='#00d4aa' if variant == 'A' else '#ff6b6b'
            ))
        
        fig_compare.update_layout(
            title='Events by Variant',
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#fff',
            legend=dict(bgcolor='rgba(0,0,0,0)')
        )
        st.plotly_chart(fig_compare, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("### 📊 Conversion Funnel")
    
    funnel_data = {}
    for event in stats['events']:
        e = event.get('event', 'unknown')
        v = event.get('variant', 'unknown')
        if v not in funnel_data:
            funnel_data[v] = {}
        funnel_data[v][e] = funnel_data[v].get(e, 0) + 1
    
    for variant in ['A', 'B']:
        st.markdown(f"#### Variant {variant}")
        if variant in funnel_data:
            for event_name, count in sorted(funnel_data[variant].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len([e for e in stats['events'] if e.get('variant') == variant])) * 100
                st.markdown(f"""
                <div class="insight-box">
                    <strong>{event_name}</strong>: {count} ({percentage:.1f}%)
                </div>
                """, unsafe_allow_html=True)
        st.markdown("---")
    
else:
    st.info("No A/B test data collected yet. The tracking code is ready and will collect data as users interact with the predictions page.")

st.markdown("### 💬 User Feedback Analysis")

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
                   marker_color='#00d4aa')
        ])
        fig_fb.update_layout(
            title='Feedback Distribution',
            xaxis_title='Feedback Type',
            yaxis_title='Count',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#fff'
        )
        st.plotly_chart(fig_fb, use_container_width=True)
    
    with col_fb2:
        positive = len([f for f in feedback if f.get('feedback_type') == 'positive'])
        negative = len([f for f in feedback if f.get('feedback_type') == 'negative'])
        neutral = len([f for f in feedback if f.get('feedback_type') == 'neutral'])
        
        sentiment_data = go.Figure(data=[
            go.Pie(labels=['Positive', 'Negative', 'Neutral'], 
                   values=[positive, negative, neutral],
                   hole=0.4,
                   marker_colors=['#00d4aa', '#ff6b6b', '#ffa502'])
        ])
        sentiment_data.update_layout(
            title='Sentiment Analysis',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#fff'
        )
        st.plotly_chart(sentiment_data, use_container_width=True)
    
    st.markdown("### 📝 Recent Comments")
    
    comments = [f for f in feedback if f.get('comment')]
    if comments:
        for comment in comments[-10:]:
            st.markdown(f"""
            <div class="insight-box">
                <strong>{comment.get('user_id', 'Anonymous')}</strong> 
                <span style="color:#888;">({comment.get('timestamp', '')})</span>
                <p>{comment.get('comment', '')}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No comments yet.")
    
    with st.expander("View All Feedback"):
        feedback_df = pd.DataFrame(feedback)
        st.dataframe(feedback_df, use_container_width=True)
        
        csv = feedback_df.to_csv(index=False)
        st.download_button("Download Feedback CSV", csv, "feedback.csv", "text/csv")

else:
    st.info("No user feedback collected yet.")

st.markdown("---")

st.markdown("### 🚀 Usage Insights")

st.markdown("""
<div class="insight-box">
    <strong>Key Metrics to Track:</strong>
    <ul>
        <li>Prediction generation rate (generations per session)</li>
        <li>Model preference distribution</li>
        <li>State/sector/fuel combination popularity</li>
        <li>Feedback rate (users who provide feedback)</li>
        <li>Variant conversion (page_view → generate_click → prediction_made)</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("### ⚙️ A/B Test Configuration")

col_test1, col_test2 = st.columns(2)

with col_test1:
    st.markdown("""
    **Current Experiment: prediction_ui**
    - **Variant A**: Classic prediction display (box with gradient)
    - **Variant B**: Modern metrics display (Streamlit metrics + progress)
    - **Traffic Split**: 50/50
    """)

with col_test2:
    st.markdown("""
    **Tracked Events:**
    - `page_view`: User visits prediction page
    - `generate_click`: User clicks prediction button
    - `prediction_made`: Prediction successfully generated
    - `feedback`: User provides feedback on prediction
    - `error`: Prediction generation fails
    """)

st.markdown("---")
st.markdown("*Analytics data is stored locally in `data/ab_test_experiments.json` and `data/user_feedback.json`*")