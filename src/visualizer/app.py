# src/visualizer/app.py (Refactored for Stability and Code Structure)

import requests
import json
import numpy as np
from flask import Flask, render_template
import redis

app = Flask(__name__)

# --- Configuration ---
API_URL = "http://slot-machine-api:8000"
REDIS_HOST = "redis"
REDIS_PORT = 6379
NUM_SAMPLES_FOR_PLOT = 1000
# NEW: Define a fixed Y-axis range for plot stability
PLOT_Y_AXIS_RANGE = [-5, 7]

# Connect to Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

def get_ground_truth_plot():
    """Fetches true arm data from API and returns a full Plotly JSON object."""
    plot = {
        'data': [],
        'layout': {
            'title': '<b>Ground Truth Reward Distributions</b>',
            'yaxis': {'title': 'Reward Value', 'zeroline': True, 'range': PLOT_Y_AXIS_RANGE},
            'xaxis': {'title': 'Slot Machine Arm'}
        }
    }
    try:
        response = requests.get(f"{API_URL}/get_arm_configs")
        response.raise_for_status()
        configs = response.json()
        
        for arm_id, params in sorted(configs.items()):
            samples = np.random.normal(params['mean'], params['std_dev'], NUM_SAMPLES_FOR_PLOT)
            plot['data'].append({'y': list(samples), 'type': 'violin', 'name': f'Arm {arm_id}'})
        return plot
    except Exception as e:
        print(f"Error getting ground truth data: {e}")
        return plot # Return empty plot on error

def get_agent_beliefs_plot():
    """Loads agent beliefs from Redis and returns a full Plotly JSON object."""
    plot = {
        'data': [],
        'layout': {
            'title': '<b>Agent\'s Learned Beliefs</b> (Sampled)',
            'yaxis': {'title': 'Expected Reward (Sampled)', 'zeroline': True, 'range': PLOT_Y_AXIS_RANGE},
            'xaxis': {'title': 'Slot Machine Arm'}
        }
    }
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
            plot['data'].append({'y': list(mus), 'type': 'violin', 'name': f'Arm {arm_id}'})
        return plot
    except Exception as e:
        print(f"Error getting agent beliefs data from Redis: {e}")
        return plot # Return empty plot on error

# The new, correct way
@app.route('/')
def dashboard():
    """Renders the main dashboard page."""
    # We now pass the Python dictionaries directly to the template.
    # The 'tojson' filter in the HTML will handle the conversion.
    ground_truth_plot = get_ground_truth_plot()
    agent_beliefs_plot = get_agent_beliefs_plot()
    
    return render_template(
        'index.html',
        ground_truth_plot_json=ground_truth_plot,
        agent_beliefs_plot_json=agent_beliefs_plot
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)