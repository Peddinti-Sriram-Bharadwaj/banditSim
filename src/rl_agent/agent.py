# src/rl_agent/agent.py (Refactored for Redis)

import redis
import numpy as np

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
            print("INFO: No belief state found in Redis. Initializing new state.")
            # Initialize with our tuned 'uninformative' priors
            initial_beliefs = {
                'mu': '0.0', 'nu': '1.0', 'alpha': '0.2', 'beta': '0.2'
            }
            for arm_id in self.arm_ids:
                # Store beliefs for each arm in a Redis Hash
                self.redis.hset(f"arm:{arm_id}", mapping=initial_beliefs)
            print("INFO: New state initialized in Redis.")
        else:
            print("INFO: Existing belief state found in Redis.")

    def select_arm(self) -> str:
        """Selects an arm by sampling from the posterior distribution."""
        sampled_means = []
        for arm_id in self.arm_ids:
            # HGETALL retrieves the hash for an arm's beliefs
            # All values in Redis are stored as bytestrings, so we must decode
            params_raw = self.redis.hgetall(f"arm:{arm_id}")
            params = {k.decode(): float(v.decode()) for k, v in params_raw.items()}

            tau = np.random.gamma(shape=params['alpha'], scale=1.0/params['beta'])
            std_dev = 1.0 / np.sqrt(params['nu'] * tau)
            mu = np.random.normal(loc=params['mu'], scale=std_dev)
            sampled_means.append(mu)

        best_arm_index = np.argmax(sampled_means)
        return self.arm_ids[best_arm_index]

    def update_belief(self, arm_id: str, reward: float):
        """Updates belief parameters in Redis for the chosen arm."""
        arm_key = f"arm:{arm_id}"
        
        # Use a transaction (pipeline) for atomicity
        with self.redis.pipeline() as pipe:
            while True:
                try:
                    # Watch the key for changes from other agents
                    pipe.watch(arm_key)
                    
                    # Get current belief values
                    params_raw = pipe.hgetall(arm_key)
                    params = {k.decode(): float(v.decode()) for k, v in params_raw.items()}
                    mu_prev, nu_prev, alpha_prev, beta_prev = params['mu'], params['nu'], params['alpha'], params['beta']
                    
                    # Start the transaction
                    pipe.multi()

                    # Calculate new values
                    mu_new = (nu_prev * mu_prev + reward) / (nu_prev + 1)
                    alpha_new = alpha_prev + 0.5
                    beta_new = beta_prev + (nu_prev * (reward - mu_prev)**2) / (2 * (nu_prev + 1))
                    nu_new = nu_prev + 1
                    
                    # Set the new values in the hash
                    pipe.hset(arm_key, "mu", mu_new)
                    pipe.hset(arm_key, "nu", nu_new)
                    pipe.hset(arm_key, "alpha", alpha_new)
                    pipe.hset(arm_key, "beta", beta_new)
                    
                    # Execute the transaction
                    pipe.execute()
                    break # Success
                except redis.WatchError:
                    # Another agent modified the key while we were working. Retry.
                    continue