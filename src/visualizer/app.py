# src/visualizer/app.py

import requests
import json
import numpy as np
from flask import Flask, render_template

app = Flask(__name__)

# --- Configuration ---
API_URL = "http://slot-machine-api:8000"
AGENT_STATE_PATH = "/data/agent_state.json"
NUM_SAMPLES_FOR_PLOT = 1000  # Number of samples to draw for visualizing distributions

def get_ground_truth_data():
    """Fetches true arm distributions from the API and formats for Plotly."""
    try:
        response = requests.get(f"{API_URL}/get_arm_configs")
        response.raise_for_status()
        configs = response.json()
        
        plot_data = []
        for arm_id, params in sorted(configs.items()):
            samples = np.random.normal(params['mean'], params['std_dev'], NUM_SAMPLES_FOR_PLOT)
            plot_data.append({'y': list(samples), 'type': 'violin', 'name': f'Arm {arm_id}'})
        return plot_data
    except Exception as e:
        print(f"Error getting ground truth data: {e}")
        return []

def get_agent_beliefs_data():
    """Loads agent beliefs and formats them for Plotly by sampling."""
    try:
        with open(AGENT_STATE_PATH, 'r') as f:
            beliefs = json.load(f)
        
        plot_data = []
        for arm_id, params in sorted(beliefs.items()):
            # Sample from the Normal-Gamma posterior to visualize belief
            tau = np.random.gamma(shape=params['alpha'], scale=1.0/params['beta'], size=NUM_SAMPLES_FOR_PLOT)
            std_devs = 1.0 / np.sqrt(params['nu'] * tau)
            mus = np.random.normal(loc=params['mu'], scale=std_devs)
            plot_data.append({'y': list(mus), 'type': 'violin', 'name': f'Arm {arm_id}'})
        return plot_data
    except FileNotFoundError:
        print("Agent state file not found yet. It will be created shortly.")
        return []
    except Exception as e:
        print(f"Error getting agent beliefs data: {e}")
        return []

@app.route('/')
def dashboard():
    """Renders the main dashboard page."""
    ground_truth_data = get_ground_truth_data()
    agent_beliefs_data = get_agent_beliefs_data()
    
    return render_template(
        'index.html',
        ground_truth_data=ground_truth_data,
        agent_beliefs_data=agent_beliefs_data
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)