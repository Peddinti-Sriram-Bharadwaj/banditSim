# src/rl_agent/agent.py

import os
import json
import numpy as np
from scipy.stats import gamma

class ThompsonSamplingAgent:
    """
    An agent that uses Thompson Sampling to solve the K-armed bandit problem
    with Gaussian rewards where both mean and variance are unknown.
    """

    def __init__(self, arm_ids: list[str], state_file_path: str):
        """
        Initializes the agent.

        :param arm_ids: A list of strings identifying each arm.
        :param state_file_path: Path to the JSON file for saving/loading state.
        """
        self.arm_ids = arm_ids
        self.state_file_path = state_file_path
        self.beliefs = {}
        self._load_or_initialize_state()

    def _load_or_initialize_state(self):
        """Loads beliefs from the state file or initializes them if not found."""
        if os.path.exists(self.state_file_path):
            print("INFO: Loading existing agent state.")
            with open(self.state_file_path, 'r') as f:
                self.beliefs = json.load(f)
        else:
            print("INFO: No state file found. Initializing new agent state.")
            # For a Gaussian with unknown mean and variance, the conjugate prior
            # is the Normal-Gamma distribution, defined by 4 parameters.
            # We initialize with weak priors.
            for arm_id in self.arm_ids:
                self.beliefs[arm_id] = {
                    'mu': 0.0,      # Prior mean
                    'nu': 1.0,      # Prior count of observations for mean
                    'alpha': 1.0,   # Prior shape for precision
                    'beta': 1.0,    # Prior rate for precision
                }
            self.save_state()

    def save_state(self):
        """Saves the agent's current beliefs to the state file."""
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.state_file_path), exist_ok=True)
        with open(self.state_file_path, 'w') as f:
            json.dump(self.beliefs, f, indent=4)
        # print(f"DEBUG: Agent state saved to {self.state_file_path}")

    def select_arm(self) -> str:
        """
        Selects an arm by sampling from the posterior distribution of each arm's
        expected reward and choosing the one with the highest sample.
        """
        sampled_means = []
        for arm_id in self.arm_ids:
            params = self.beliefs[arm_id]
            
            # 1. Sample precision (tau) from the Gamma distribution
            # The scale parameter for numpy's gamma is 1/rate (1/beta).
            tau = np.random.gamma(shape=params['alpha'], scale=1.0/params['beta'])
            
            # 2. Sample mean (mu) from the Normal distribution, conditional on tau
            # The scale parameter for numpy's normal is std_dev = 1 / sqrt(nu * tau)
            std_dev = 1.0 / np.sqrt(params['nu'] * tau)
            mu = np.random.normal(loc=params['mu'], scale=std_dev)
            
            sampled_means.append(mu)

        best_arm_index = np.argmax(sampled_means)
        return self.arm_ids[best_arm_index]

    def update_belief(self, arm_id: str, reward: float):
        """
        Updates the belief parameters for the chosen arm based on the observed reward.
        
        :param arm_id: The ID of the arm that was chosen.
        :param reward: The reward received from that arm.
        """
        params = self.beliefs[arm_id]
        mu_prev, nu_prev, alpha_prev, beta_prev = params['mu'], params['nu'], params['alpha'], params['beta']

        # Apply the standard Bayesian update rules for the Normal-Gamma posterior
        params['mu'] = (nu_prev * mu_prev + reward) / (nu_prev + 1)
        params['alpha'] = alpha_prev + 0.5
        params['beta'] = beta_prev + (nu_prev * (reward - mu_prev)**2) / (2 * (nu_prev + 1))
        params['nu'] = nu_prev + 1
        
        self.beliefs[arm_id] = params
        # print(f"DEBUG: Updated arm {arm_id} with reward {reward}. New beliefs: {params}")