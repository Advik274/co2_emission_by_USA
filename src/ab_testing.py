import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
import hashlib

class ABTesting:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        self.experiments_file = os.path.join(self.data_dir, 'ab_test_experiments.json')
        self.feedback_file = os.path.join(self.data_dir, 'user_feedback.json')
        
    def _load_json(self, filepath, default=None):
        if default is None:
            default = {}
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except:
                return default
        return default
    
    def _save_json(self, filepath, data):
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_user_id(self):
        if 'user_id' not in st.session_state:
            if 'user_ip' not in st.session_state:
                st.session_state.user_ip = st.context.headers.get('Remote-Addr', 'unknown')
            user_hash = hashlib.md5(f"{st.session_state.user_ip}_{datetime.now().strftime('%Y%m%d')}".encode()).hexdigest()[:8]
            st.session_state.user_id = user_hash
        return st.session_state.user_id
    
    def assign_variant(self, experiment_name, variants=['A', 'B']):
        if f'ab_{experiment_name}' not in st.session_state:
            user_id = self.get_user_id()
            variant_index = int(hashlib.md5(f"{user_id}_{experiment_name}".encode()).hexdigest(), 16) % len(variants)
            st.session_state[f'ab_{experiment_name}'] = variants[variant_index]
        return st.session_state[f'ab_{experiment_name}']
    
    def track_event(self, experiment_name, event_name, metadata=None):
        experiments = self._load_json(self.experiments_file)
        if experiment_name not in experiments:
            experiments[experiment_name] = {'events': [], 'variants': {}}
        
        event = {
            'timestamp': datetime.now().isoformat(),
            'user_id': self.get_user_id(),
            'variant': st.session_state.get(f'ab_{experiment_name}', 'unknown'),
            'event': event_name,
            'metadata': metadata or {}
        }
        experiments[experiment_name]['events'].append(event)
        
        variant = event['variant']
        if variant not in experiments[experiment_name]['variants']:
            experiments[experiment_name]['variants'][variant] = {'total': 0, 'events': {}}
        
        experiments[experiment_name]['variants'][variant]['total'] += 1
        if event_name not in experiments[experiment_name]['variants'][variant]['events']:
            experiments[experiment_name]['variants'][variant]['events'][event_name] = 0
        experiments[experiment_name]['variants'][variant]['events'][event_name] += 1
        
        self._save_json(self.experiments_file, experiments)
    
    def add_feedback(self, prediction_id, feedback_type, rating=None, comment=None):
        feedback_data = self._load_json(self.feedback_file)
        if 'feedback' not in feedback_data:
            feedback_data['feedback'] = []
        
        feedback_data['feedback'].append({
            'timestamp': datetime.now().isoformat(),
            'user_id': self.get_user_id(),
            'prediction_id': prediction_id,
            'feedback_type': feedback_type,
            'rating': rating,
            'comment': comment
        })
        
        self._save_json(self.feedback_file, feedback_data)
        return True
    
    def get_experiment_stats(self, experiment_name):
        experiments = self._load_json(self.experiments_file)
        if experiment_name not in experiments:
            return None
        return experiments[experiment_name]
    
    def get_feedback_stats(self):
        feedback_data = self._load_json(self.feedback_file)
        return feedback_data.get('feedback', [])

    def get_results(self):
        experiments = self._load_json(self.experiments_file)
        results = []
        if 'prediction_ui' in experiments:
            for event in experiments['prediction_ui'].get('events', []):
                if event.get('event') in ('prediction_made', 'generate_click'):
                    metadata = event.get('metadata', {})
                    model = metadata.get('model', 'Unknown')
                    if not model or model == 'Unknown':
                        continue
                    
                    # Normalize model name and map to MSE
                    mse = 0.02
                    if 'Random Forest' in model or 'RF' in model:
                        mse = 0.0072
                        model_name = 'Random Forest'
                    elif 'XGBoost' in model:
                        mse = 0.0132
                        model_name = 'XGBoost'
                    elif 'ANN' in model:
                        mse = 0.0244
                        model_name = 'ANN'
                    else:
                        model_name = model
                        
                    results.append({
                        'timestamp': event.get('timestamp'),
                        'user_id': event.get('user_id'),
                        'variant': event.get('variant'),
                        'model': model_name,
                        'mse': mse
                    })
        return results

ab_testing = ABTesting()