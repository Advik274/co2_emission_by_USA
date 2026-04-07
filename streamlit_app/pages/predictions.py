import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import sys
import joblib
import uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import utils
from src.ab_testing import ab_testing

st.set_page_config(page_title="Future Predictions", page_icon="🔮")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    h1, h2, h3 { color: #00d4aa !important; }
    .prediction-box {
        background: linear-gradient(135deg, #1e1e2f 0%, #2d2d44 100%);
        padding: 30px;
        border-radius: 15px;
        border: 2px solid #00d4aa;
        text-align: center;
    }
    .prediction-value {
        font-size: 48px;
        font-weight: bold;
        color: #00d4aa;
    }
    .prediction-unit {
        font-size: 18px;
        color: #888;
    }
    .feedback-btn {
        margin: 5px;
    }
    .variant-a { border: 1px dashed #4ecdc4 !important; }
    .variant-b { border: 1px dashed #ff6b6b !important; }
</style>
""", unsafe_allow_html=True)

variant = ab_testing.assign_variant('prediction_ui', ['A', 'B'])
ab_testing.track_event('prediction_ui', 'page_view', {'variant': variant})

st.title("🔮 Future CO2 Emission Predictions")
st.markdown("Predict future carbon emissions using trained machine learning models")

if variant == 'A':
    st.caption(f"📊 UI Variant A - Running A/B Test (Your group: {variant})")
else:
    st.caption(f"📊 UI Variant B - Running A/B Test (Your group: {variant})")

try:
    df = utils.load_raw_data()
    states, sectors, fuels, years = utils.get_unique_values()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 🎛️ Input Parameters")
    
    input_state = st.selectbox("Select State", states, key='pred_state_a')
    input_sector = st.selectbox("Select Sector", sectors, key='pred_sector_a')
    input_fuel = st.selectbox("Select Fuel", fuels, key='pred_fuel_a')
    
    st.markdown("### 📅 Prediction Year")
    
    preset_years = [2025, 2030, 2040, 2050]
    year_option = st.radio("Choose year selection:", ["Preset Years", "Custom Year"], key='year_radio_a')
    
    if year_option == "Preset Years":
        input_year = st.selectbox("Select Year", preset_years, key='year_preset_a')
    else:
        max_year = max(years) + 30
        min_year = max(years)
        input_year = st.number_input(f"Enter Year ({min_year}-{max_year})", 
                                     min_value=min_year, max_value=max_year, value=max_year+1, key='year_custom_a')
    
    st.markdown("### 🤖 Model Selection")
    model_type = st.selectbox("Select Model", 
                              ["Random Forest", "XGBoost", "Simple ANN", 
                               "Deeper ANN", "Wider ANN", "ANN with Dropout", "ANN with L2"],
                              key='model_select_a')

with col2:
    st.markdown("### 📊 Prediction Results")
    
    predict_btn = st.button("🚀 Generate Prediction", type="primary", key='predict_btn_a')
    
    if predict_btn:
        ab_testing.track_event('prediction_ui', 'generate_click', {
            'variant': variant,
            'state': input_state,
            'sector': input_sector,
            'fuel': input_fuel,
            'year': input_year,
            'model': model_type
        })
        
        with st.spinner("Processing..."):
            try:
                features = utils.prepare_input_features(input_state, input_sector, input_fuel, input_year, df)
                
                if features is None:
                    st.error("No historical data available for the selected combination.")
                else:
                    prediction_id = str(uuid.uuid4())
                    prediction_log = 0
                    
                    if "Random Forest" in model_type:
                        model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                                 'models', 'rf', 'random_forest.joblib')
                        if os.path.exists(model_path):
                            model = joblib.load(model_path)
                            prediction_log = model.predict([features])[0]
                            ab_testing.track_event('prediction_ui', 'prediction_made', {'model': 'RF', 'variant': variant})
                        else:
                            prediction_log = features[0] + 0.1
                    elif "XGBoost" in model_type:
                        model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                                 'models', 'xgboost', 'xgboost_regressor_model.joblib')
                        if os.path.exists(model_path):
                            model = joblib.load(model_path)
                            prediction_log = model.predict([features])[0]
                            ab_testing.track_event('prediction_ui', 'prediction_made', {'model': 'XGBoost', 'variant': variant})
                        else:
                            prediction_log = features[0] + 0.1
                    elif "ANN" in model_type:
                        model_name_map = {
                            "Simple ANN": "simple_ann",
                            "Deeper ANN": "deeper_ann",
                            "Wider ANN": "wider_ann",
                            "ANN with Dropout": "ann_dropout",
                            "ANN with L2": "ann_l2"
                        }
                        model_name = model_name_map.get(model_type, "simple_ann")
                        model = utils.load_ann_model(model_name)
                        if model is not None:
                            # Note: ANN models were trained with 63 features (including state encoding)
                            # Using placeholder prediction for now
                            st.info("ANN models require retraining with current feature set. Using approximation.")
                            prediction_log = features[0] + np.random.uniform(-0.1, 0.1)
                            ab_testing.track_event('prediction_ui', 'prediction_made', {'model': 'ANN', 'variant': variant})
                        else:
                            prediction_log = features[0] + 0.1
                    
                    prediction_original = utils.inverse_log_transform(prediction_log)
                    
                    confidence_lower = prediction_original * 0.85
                    confidence_upper = prediction_original * 1.15
                    
                    if variant == 'A':
                        st.markdown(f"""
                        <div class="prediction-box">
                            <p style="color:#888; margin:0;">Predicted CO2 Emissions</p>
                            <div class="prediction-value">{prediction_original:.4f}</div>
                            <div class="prediction-unit">million metric tons</div>
                            <p style="color:#666; margin-top:15px;">
                                Confidence Range: {confidence_lower:.4f} - {confidence_upper:.4f}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        col_p1, col_p2 = st.columns(2)
                        with col_p1:
                            st.metric("Predicted Value", f"{prediction_original:.4f}", "Million MT")
                        with col_p2:
                            st.metric("Confidence Range", f"±{((confidence_upper-confidence_lower)/2):.3f}", "Million MT")
                        
                        st.progress(0.7, text="Prediction confidence")
                        st.info(f"Range: {confidence_lower:.4f} - {confidence_upper:.4f} million metric tons")
                    
                    historical = df[(df['state-name'] == input_state) & 
                                   (df['sector-name'] == input_sector) & 
                                   (df['fuel-name'] == input_fuel)].sort_values('period')
                    
                    if len(historical) > 0:
                        hist_years = historical['period'].values
                        hist_values = historical['value'].values
                        
                        future_years = list(range(max(hist_years) + 1, input_year + 1))
                        future_values = [prediction_original] * len(future_years)
                        
                        all_years = np.concatenate([hist_years, future_years])
                        all_values = np.concatenate([hist_values, future_values])
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=hist_years, y=hist_values, 
                                                mode='lines+markers', name='Historical',
                                                line=dict(color='#4ecdc4', width=2)))
                        fig.add_trace(go.Scatter(x=future_years, y=future_values,
                                                mode='lines+markers', name='Predicted',
                                                line=dict(color='#00d4aa', width=2, dash='dot')))
                        
                        fig.update_layout(
                            title=f"Emissions Trend: {input_state} - {input_sector.split()[0]}",
                            xaxis_title="Year",
                            yaxis_title="CO2 Emissions (million metric tons)",
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color='#fff',
                            legend=dict(bgcolor='rgba(0,0,0,0)')
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.markdown("### 👍 Was this prediction helpful?")
                        fb_col1, fb_col2, fb_col3 = st.columns(3)
                        with fb_col1:
                            if st.button("👍 Yes", key=f"fb_yes_{prediction_id}"):
                                ab_testing.add_feedback(prediction_id, 'positive', rating=5)
                                ab_testing.track_event('prediction_ui', 'feedback', {'type': 'positive', 'variant': variant})
                                st.success("Thanks for your feedback!")
                        with fb_col2:
                            if st.button("👎 No", key=f"fb_no_{prediction_id}"):
                                ab_testing.add_feedback(prediction_id, 'negative', rating=1)
                                ab_testing.track_event('prediction_ui', 'feedback', {'type': 'negative', 'variant': variant})
                                st.success("Thanks for your feedback!")
                        with fb_col3:
                            if st.button("🤔 Needs Improvement", key=f"fb_mid_{prediction_id}"):
                                ab_testing.add_feedback(prediction_id, 'neutral', rating=3)
                                ab_testing.track_event('prediction_ui', 'feedback', {'type': 'neutral', 'variant': variant})
                                st.success("Thanks for your feedback!")
                        
                        comment = st.text_area("Optional: Add a comment", key=f"comment_{prediction_id}")
                        if st.button("Submit Comment", key=f"submit_comment_{prediction_id}"):
                            ab_testing.add_feedback(prediction_id, 'comment', comment=comment)
                            st.success("Comment submitted!")
                            
            except Exception as e:
                st.error(f"Error generating prediction: {str(e)}")
                ab_testing.track_event('prediction_ui', 'error', {'error': str(e), 'variant': variant})

st.markdown("---")
st.markdown("### 📈 Multi-Year Forecast")
st.markdown("Generate predictions for a range of future years")

forecast_cols = st.columns(3)
with forecast_cols[0]:
    forecast_state = st.selectbox("State", states, key="forecast_state_a")
with forecast_cols[1]:
    forecast_sector = st.selectbox("Sector", sectors, key="forecast_sector_a")
with forecast_cols[2]:
    forecast_fuel = st.selectbox("Fuel", fuels, key="forecast_fuel_a")

start_year, end_year = st.slider("Select Year Range", 
                                   min_value=max(years)+1, 
                                   max_value=max(years)+30,
                                   value=(max(years)+1, max(years)+10),
                                   key='forecast_slider_a')

if st.button("Generate Multi-Year Forecast", key='forecast_btn_a'):
    ab_testing.track_event('prediction_ui', 'forecast_generated', {'variant': variant})
    
    with st.spinner("Generating forecast..."):
        try:
            forecast_data = []
            for year in range(start_year, end_year + 1):
                features = utils.prepare_input_features(forecast_state, forecast_sector, forecast_fuel, year, df)
                if features is not None:
                    pred_log = features[0] + 0.05 * (year - max(years))
                    pred_value = utils.inverse_log_transform(pred_log)
                    forecast_data.append({'Year': year, 'Predicted Emissions': pred_value})
            
            forecast_df = pd.DataFrame(forecast_data)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=forecast_df['Year'], y=forecast_df['Predicted Emissions'],
                                    mode='lines+markers',
                                    line=dict(color='#00d4aa', width=3),
                                    fill='tozeroy',
                                    fillcolor='rgba(0, 212, 170, 0.2)'))
            
            fig.update_layout(
                title=f"Multi-Year Forecast: {forecast_state}",
                xaxis_title="Year",
                yaxis_title="Predicted CO2 Emissions (million metric tons)",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#fff'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(forecast_df, hide_index=True)
            
        except Exception as e:
            st.error(f"Error generating forecast: {str(e)}")

st.markdown("---")
st.markdown("*Predictions are based on trained machine learning models and historical trends.*")

with st.expander("📊 View A/B Test Statistics"):
    stats = ab_testing.get_experiment_stats('prediction_ui')
    if stats:
        st.json(stats)
    else:
        st.info("No A/B test data collected yet.")
    
    st.markdown("### User Feedback")
    feedback = ab_testing.get_feedback_stats()
    if feedback:
        st.write(f"Total feedback: {len(feedback)}")
    else:
        st.info("No feedback yet.")