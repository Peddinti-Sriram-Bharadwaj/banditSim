# src/orchestrator/orchestrator.py (Final Polished Version)

import redis
import numpy as np
import time
import sys
import requests
from collections import deque
import os

# --- Configuration ---
# --- MODIFIED: Read config from environment variables ---
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
API_URL = os.getenv("API_BASE_URL", "http://slot-machine-api:8000")
# --------------------------------------------------------
REDIS_PORT = 6379
CHECK_INTERVAL_SECONDS = 10
CONVERGENCE_THRESHOLD = 0.01
CONVERGENCE_DURATION_CHECKS = 5
DRIFT_WINDOW_SIZE = 50
DRIFT_THRESHOLD_FACTOR = 0.7
FORCED_EXPLORATION_SECONDS = 30 # Duration for the re-learning phase

class SystemMonitor:
    def __init__(self, redis_client, arm_ids):
        self.redis = redis_client
        self.arm_ids = arm_ids
        self.mode = "CONVERGENCE_DETECTION"
        self.previous_beliefs = self._get_current_beliefs()
        self.consecutive_stable_checks = 0
        self.converged_best_arm = None
        self.converged_belief_mean = None
        self.recent_rewards = deque(maxlen=DRIFT_WINDOW_SIZE)

    def _get_current_beliefs(self):
        beliefs = {}
        for arm_id in self.arm_ids:
            raw_belief = self.redis.hgetall(f"arm:{arm_id}")
            if raw_belief:
                beliefs[arm_id] = {k: float(v) for k, v in raw_belief.items()}
        return beliefs

    def check_convergence(self):
        current_beliefs = self._get_current_beliefs()
        if not current_beliefs or not self.previous_beliefs:
            self.previous_beliefs = current_beliefs
            return

        total_change = sum(
            abs(current_beliefs[arm_id]['mu'] - self.previous_beliefs[arm_id]['mu'])
            for arm_id in self.arm_ids
            if arm_id in current_beliefs and arm_id in self.previous_beliefs
        )
        print(f"INFO (CONVERGENCE): Beliefs change: {total_change:.6f}")

        if total_change < CONVERGENCE_THRESHOLD:
            self.consecutive_stable_checks += 1
            print(f"INFO (CONVERGENCE): Stable check #{self.consecutive_stable_checks}/{CONVERGENCE_DURATION_CHECKS}.")
        else:
            self.consecutive_stable_checks = 0

        self.previous_beliefs = current_beliefs

        if self.consecutive_stable_checks >= CONVERGENCE_DURATION_CHECKS:
            self.handle_convergence(current_beliefs)

    def handle_convergence(self, converged_beliefs):
        if not converged_beliefs: return
        
        self.converged_best_arm = max(converged_beliefs, key=lambda arm: converged_beliefs[arm]['mu'])
        self.converged_belief_mean = converged_beliefs[self.converged_best_arm]['mu']
        self.mode = "DRIFT_MONITORING"
        self.redis.set("system:mode", "MONITORING")

        # FIXED: Added 'f' for f-string formatting
        print("\n" + "="*60)
        print(f">>> SYSTEM CONVERGED on Arm {self.converged_best_arm} with believed mean {self.converged_belief_mean:.2f}")
        print(">>> SWITCHING TO DRIFT MONITORING MODE.")
        print("="*60 + "\n")

    def check_drift(self):
        last_reward_str = self.redis.get(f"arm:{self.converged_best_arm}:last_reward")
        if last_reward_str:
            self.recent_rewards.append(float(last_reward_str))
            self.redis.delete(f"arm:{self.converged_best_arm}:last_reward")

        if len(self.recent_rewards) < DRIFT_WINDOW_SIZE:
            print(f"INFO (DRIFT): Collecting rewards for baseline... ({len(self.recent_rewards)}/{DRIFT_WINDOW_SIZE})")
            return

        current_avg_reward = sum(self.recent_rewards) / len(self.recent_rewards)
        drift_threshold = self.converged_belief_mean * DRIFT_THRESHOLD_FACTOR
        
        print(f"INFO (DRIFT): Monitoring Arm {self.converged_best_arm}. Current Avg Reward: {current_avg_reward:.2f}, Drift Threshold: < {drift_threshold:.2f}")
        
        if current_avg_reward < drift_threshold:
            self.handle_drift()

    def handle_drift(self):
        avg_reward = sum(self.recent_rewards) / len(self.recent_rewards) if self.recent_rewards else 0
        drift_threshold_value = self.converged_belief_mean * DRIFT_THRESHOLD_FACTOR
        
        # FIXED: Added 'f' for f-string formatting
        print("\n" + "!"*60)
        print(f">>> DRIFT DETECTED on Arm {self.converged_best_arm}!")
        print(f">>> Average reward {avg_reward:.2f} is below the threshold of {drift_threshold_value:.2f}.")
        print(f">>> TRIGGERING SYSTEM-WIDE FORCED EXPLORATION for {FORCED_EXPLORATION_SECONDS} seconds.")
        print("!"*60 + "\n")

        # FIXED: Set mode to FORCED_EXPLORATION with an expiry for a clear re-learning phase.
        self.redis.set("system:mode", "FORCED_EXPLORATION", ex=FORCED_EXPLORATION_SECONDS)
        
        initial_beliefs = {'mu': '0.0', 'nu': '1.0', 'alpha': '0.2', 'beta': '0.2'}
        for arm_id in self.arm_ids:
            self.redis.hset(f"arm:{arm_id}", mapping=initial_beliefs)
        
        self.mode = "CONVERGENCE_DETECTION"
        self.previous_beliefs = self._get_current_beliefs()
        self.consecutive_stable_checks = 0
        self.recent_rewards.clear()
        self.converged_best_arm = None
        self.converged_belief_mean = None

    def run(self):
        if self.mode == "CONVERGENCE_DETECTION":
            self.check_convergence()
        elif self.mode == "DRIFT_MONITORING":
            self.check_drift()

def get_arm_ids_from_api(api_url: str):
    try:
        response = requests.get(f"{api_url}/get_arm_configs")
        response.raise_for_status()
        return sorted(response.json().keys())
    except Exception as e:
        print(f"ORCHESTRATOR FATAL: Could not get arm IDs from API: {e}", file=sys.stderr)
        return None

def main():
    print("--- Orchestrator Service Starting (v2.2 Final) ---")
    time.sleep(15)
    arm_ids = get_arm_ids_from_api(API_URL)
    if not arm_ids: sys.exit(1)
    
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    monitor = SystemMonitor(redis_client=redis_client, arm_ids=arm_ids)
    print("INFO: Orchestrator initialized. Monitoring for convergence...")

    while True:
        try:
            monitor.run()
        except Exception as e:
            print(f"ERROR in monitor loop: {e}", file=sys.stderr)
        
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()