# src/rl_agent/main.py (Final version with reward reporting)

import time
import requests
import sys
import redis
import random

from agent import ThompsonSamplingAgent
from config import API_BASE_URL, REDIS_HOST, REDIS_PORT
API_URL = "http://slot-machine-api:8000"

def get_arm_ids_from_api(api_url: str) -> list[str]:
    """
    Fetches the list of arm IDs from the slot machine API on startup.
    Retries a few times before giving up to handle startup race conditions.
    """
    max_retries = 5
    retry_delay_seconds = 3

    for attempt in range(max_retries):
        try:
            url = f"{api_url}/get_arm_configs"
            print(f"INFO: Contacting API... (Attempt {attempt + 1}/{max_retries})")
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            arm_configs = response.json()
            print("INFO: Successfully connected to API.")
            return list(arm_configs.keys())
        except requests.exceptions.RequestException as e:
            print(f"WARN: Could not connect to API: {e}")
            if attempt < max_retries - 1:
                print(f"WARN: Retrying in {retry_delay_seconds} seconds...")
                time.sleep(retry_delay_seconds)
            else:
                print(f"FATAL: Could not connect to API after {max_retries} attempts.")
                sys.exit(1)
    return []

def main():
    """Main interaction loop for the RL agent."""
    print("--- RL Agent Starting ---")

    arm_ids = get_arm_ids_from_api(API_BASE_URL)
    if not arm_ids:
        print("FATAL: No arms found from API. Exiting.")
        return

    print(f"INFO: Discovered {len(arm_ids)} arms: {', '.join(arm_ids)}")

    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

    agent = ThompsonSamplingAgent(arm_ids=arm_ids, redis_client=redis_client)
    print("INFO: Agent initialized successfully with Redis backend.")

    pull_count = 0
    while True:
        pull_count += 1

        # --- MODIFIED SECTION ---
        # Check the system mode from Redis
        system_mode = redis_client.get("system:mode")
        if system_mode:
            system_mode = system_mode.decode()
        else:
            system_mode = "LEARNING" # Default to learning

        # Agent selects an arm using the appropriate strategy
        selected_arm = agent.select_arm(mode=system_mode)
        # --- END MODIFIED SECTION ---

        try:
            response = requests.get(f"{API_URL}/choose_arm", params={'arm_id': selected_arm})
            response.raise_for_status()
            result = response.json()
            reward = result['reward']

            agent.update_belief(arm_id=selected_arm, reward=reward)
            redis_client.set(f"arm:{selected_arm}:last_reward", reward, ex=20)

            print(f"Loop {pull_count}: Mode={system_mode}. Chose arm {selected_arm}, got reward {reward:.2f}.")

        except requests.exceptions.RequestException as e:
            print(f"ERROR: Could not pull arm from API: {e}")
            time.sleep(5)

        time.sleep(1)

if __name__ == "__main__":
    main()