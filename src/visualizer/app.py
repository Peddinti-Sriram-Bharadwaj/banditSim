# src/visualizer/app.py (Refactored for Real-Time Updates)

import requests
import json
import numpy as np
from flask import Flask, render_template, jsonify
import redis

app = Flask(__name__)

# --- Configuration ---
API_URL = "http://slot-machine-api:8000"
REDIS_HOST = "redis"
REDIS_PORT = 6379
NUM_SAMPLES_FOR_PLOT = 1000
PLOT_Y_AXIS_RANGE = [-5, 8] # Slightly increased range for the new 'easy' config

# Connect to Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

def get_ground_truth_plot_data():
    """Fetches true arm data from API and returns Plotly data traces."""
    data_traces = []
    try:
        response = requests.get(f"{API_URL}/get_arm_configs")
        response.raise_for_status()
        configs = response.json()
        
        for arm_id, params in sorted(configs.items()):
            samples = np.random.normal(params['mean'], params['std_dev'], NUM_SAMPLES_FOR_PLOT)
            data_traces.append({'y': list(samples), 'type': 'violin', 'name': f'Arm {arm_id}'})
        return data_traces
    except Exception as e:
        print(f"Error getting ground truth data: {e}")
        return data_traces

def get_agent_beliefs_plot_data():
    """Loads agent beliefs from Redis and returns Plotly data traces."""
    data_traces = []
    try:
        response = requests.get(f"{API_URL}/get_arm_configs")
        response.raise_for_status()
        arm_ids = sorted(response.json().keys())

        for arm_id in arm_ids:
            params_raw = redis_client.hgetall(f"arm:{arm_id}")
            if not params_raw: continue
                
            params = {k: float(v) for k, v in params_raw.items()}
            
            tau = np.random.gamma(shape=params['alpha'], scale=1.0/params['beta'], size=NUM_SAMPLES_FOR_PLOT)
            std_devs = 1.0 / np.sqrt(params['nu'] * tau)
            mus = np.random.normal(loc=params['mu'], scale=std_devs)
            data_traces.append({'y': list(mus), 'type': 'violin', 'name': f'Arm {arm_id}'})
        return data_traces
    except Exception as e:
        print(f"Error getting agent beliefs data from Redis: {e}")
        return data_traces

@app.route('/')
def dashboard():
    """Renders the main dashboard HTML shell."""
    # This route now only serves the static page.
    # The data will be fetched by JavaScript.
    return render_template('index.html')

# NEW: Data-only endpoint for JavaScript to call
@app.route('/data')
def get_plot_data():
    """Returns all plot data as a single JSON object."""
    ground_truth_data = get_ground_truth_plot_data()
    agent_beliefs_data = get_agent_beliefs_plot_data()
    
    # We still define the layout here to keep the frontend simple
    ground_truth_layout = {
        'title': '<b>Ground Truth Reward Distributions</b>',
        'yaxis': {'title': 'Reward Value', 'zeroline': True, 'range': PLOT_Y_AXIS_RANGE},
        'xaxis': {'title': 'Slot Machine Arm'}
    }
    
    agent_beliefs_layout = {
        'title': '<b>Agent\'s Learned Beliefs</b> (Sampled)',
        'yaxis': {'title': 'Expected Reward (Sampled)', 'zeroline': True, 'range': PLOT_Y_AXIS_RANGE},
        'xaxis': {'title': 'Slot Machine Arm'}
    }
    
    return jsonify({
        'ground_truth': {'data': ground_truth_data, 'layout': ground_truth_layout},
        'agent_beliefs': {'data': agent_beliefs_data, 'layout': agent_beliefs_layout}
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)