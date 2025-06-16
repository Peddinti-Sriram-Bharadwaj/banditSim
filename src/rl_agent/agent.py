# src/rl_agent/agent.py (Final version with all modes)

import redis
import numpy as np
import random

class ThompsonSamplingAgent:
    def __init__(self, arm_ids: list[str], redis_client: redis.Redis):
        self.arm_ids = arm_ids
        self.redis = redis_client
        self._initialize_state_in_redis()

    def _initialize_state_in_redis(self):
        """Checks if beliefs exist in Redis for arm '0', if not, initializes all."""
        # Use a transaction to check and set initial values atomically if needed.
        pipe = self.redis.pipeline()
        pipe.exists(f"arm:{self.arm_ids[0]}")
        exists = pipe.execute()[0]

        if not exists:
            print("INFO: No belief state found in Redis. Initializing new agent state.")
            initial_beliefs = {'mu': '0.0', 'nu': '1.0', 'alpha': '0.2', 'beta': '0.2'}
            for arm_id in self.arm_ids:
                self.redis.hset(f"arm:{arm_id}", mapping=initial_beliefs)
            print("INFO: New state initialized in Redis.")
        else:
            print("INFO: Existing belief state found in Redis.")

    def select_arm(self, mode="LEARNING", epsilon=0.05) -> str:
        """
        Selects an arm based on the current system mode.
        """
        # --- NEW: Logic to handle all system modes ---
        if mode == "FORCED_EXPLORATION":
            # In this mode, ignore all beliefs and just pick a random arm.
            return random.choice(self.arm_ids)
        
        if mode == "MONITORING" and random.random() < epsilon:
            # In monitoring mode, 5% of the time, explore a random arm.
            return random.choice(self.arm_ids)
        # -----------------------------------------------

        # Otherwise (in LEARNING mode or for the 95% exploitation in MONITORING),
        # use Thompson Sampling as before.
        sampled_means = []
        for arm_id in self.arm_ids:
            params_raw = self.redis.hgetall(f"arm:{arm_id}")
            if not params_raw: continue # Skip if arm beliefs somehow don't exist
            
            params = {k.decode('utf-8'): float(v.decode('utf-8')) for k, v in params_raw.items()}

            tau = np.random.gamma(shape=params['alpha'], scale=1.0/params['beta'])
            std_dev = 1.0 / np.sqrt(params['nu'] * tau)
            mu = np.random.normal(loc=params['mu'], scale=std_dev)
            sampled_means.append(mu)

        if not sampled_means:
            return random.choice(self.arm_ids) # Fallback if no beliefs were found

        best_arm_index = np.argmax(sampled_means)
        return self.arm_ids[best_arm_index]

    def update_belief(self, arm_id: str, reward: float):
        """Updates belief parameters in Redis for the chosen arm using a transaction."""
        arm_key = f"arm:{arm_id}"
        
        with self.redis.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(arm_key)
                    
                    params_raw = pipe.hgetall(arm_key)
                    if not params_raw: break # Exit if the key was deleted mid-op
                        
                    params = {k.decode('utf-8'): float(v.decode('utf-8')) for k, v in params_raw.items()}
                    mu_prev, nu_prev, alpha_prev, beta_prev = params['mu'], params['nu'], params['alpha'], params['beta']
                    
                    pipe.multi()

                    mu_new = (nu_prev * mu_prev + reward) / (nu_prev + 1)
                    alpha_new = alpha_prev + 0.5
                    beta_new = beta_prev + (nu_prev * (reward - mu_prev)**2) / (2 * (nu_prev + 1))
                    nu_new = nu_prev + 1
                    
                    pipe.hset(arm_key, "mu", mu_new)
                    pipe.hset(arm_key, "nu", nu_new)
                    pipe.hset(arm_key, "alpha", alpha_new)
                    pipe.hset(arm_key, "beta", beta_new)
                    
                    pipe.execute()
                    break
                except redis.WatchError:
                    continue # Retry if another agent changed the key