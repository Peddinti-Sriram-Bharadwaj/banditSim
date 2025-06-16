# src/orchestrator/orchestrator.py

import redis
import numpy as np
import time
import json
import sys

# --- Configuration ---
REDIS_HOST = "redis"
REDIS_PORT = 6379
API_URL = "http://slot-machine-api:8000" # To get the list of arms
CHECK_INTERVAL_SECONDS = 10              # How often to check for convergence
CONVERGENCE_THRESHOLD = 0.01             # Sum of belief changes must be below this
CONVERGENCE_DURATION_CHECKS = 5          # Must be stable for this many consecutive checks

class ConvergenceDetector:
    def __init__(self, redis_client, arm_ids):
        self.redis = redis_client
        self.arm_ids = arm_ids
        self.previous_beliefs = self._get_current_beliefs()
        self.consecutive_stable_checks = 0
        self.has_converged = False

    def _get_current_beliefs(self):
        """Fetches the full belief state from Redis."""
        beliefs = {}
        for arm_id in self.arm_ids:
            raw_belief = self.redis.hgetall(f"arm:{arm_id}")
            if raw_belief: # Ensure belief exists before processing
                beliefs[arm_id] = {k: float(v) for k, v in raw_belief.items()}
        return beliefs

    def check(self):
        """Checks for convergence and returns True if converged, False otherwise."""
        if self.has_converged:
            # Don't re-evaluate if we already declared convergence
            return True

        current_beliefs = self._get_current_beliefs()
        
        # Don't check if either state is empty (can happen at startup)
        if not current_beliefs or not self.previous_beliefs:
            self.previous_beliefs = current_beliefs
            return False

        # Calculate the total change in belief means ('mu')
        total_change = 0
        for arm_id in self.arm_ids:
            if arm_id in current_beliefs and arm_id in self.previous_beliefs:
                change = abs(current_beliefs[arm_id]['mu'] - self.previous_beliefs[arm_id]['mu'])
                total_change += change
        
        print(f"INFO: Beliefs change since last check: {total_change:.6f}")

        if total_change < CONVERGENCE_THRESHOLD:
            self.consecutive_stable_checks += 1
            print(f"INFO: Stable check #{self.consecutive_stable_checks}/{CONVERGENCE_DURATION_CHECKS}.")
        else:
            # Reset counter if change is too high
            self.consecutive_stable_checks = 0
            print("INFO: Beliefs are still changing. Resetting stability counter.")
            
        # Update the state for the next check
        self.previous_beliefs = current_beliefs

        if self.consecutive_stable_checks >= CONVERGENCE_DURATION_CHECKS:
            self.has_converged = True
            return True
        
        return False

def get_arm_ids():
    """Gets the list of arm IDs from the API, since it's the source of truth."""
    # We use a simple requests call here for simplicity
    import requests
    try:
        response = requests.get(f"{API_URL}/get_arm_configs")
        response.raise_for_status()
        return sorted(response.json().keys())
    except Exception as e:
        print(f"ORCHESTRATOR FATAL: Could not get arm IDs from API: {e}", file=sys.stderr)
        return None

def main():
    print("--- Orchestrator Service Starting ---")
    time.sleep(15) # Wait a bit for other services to be ready

    arm_ids = get_arm_ids()
    if not arm_ids:
        sys.exit(1) # Exit if we can't get the configuration

    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    detector = ConvergenceDetector(redis_client=redis_client, arm_ids=arm_ids)
    print("INFO: Orchestrator initialized. Monitoring for convergence...")

    while True:
        if detector.check():
            print("\n" + "="*50)
            print(">>> SYSTEM CONVERGED: The agents have finished learning.")
            print(">>> In a production system, an action like scaling down agents would be triggered now.")
            print("="*50 + "\n")
            # In a real system, you might break the loop or switch to drift detection mode.
            # For our simulation, we'll just let it continue checking.
        
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()