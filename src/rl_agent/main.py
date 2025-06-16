# src/rl_agent/main.py (Refactored for Redis)

import time
import requests
import sys
import redis

from agent import ThompsonSamplingAgent
from config import API_BASE_URL, REDIS_HOST, REDIS_PORT

# In src/rl_agent/main.py

def get_arm_ids_from_api(api_url: str) -> list[str]:
    """
    Fetches the list of arm IDs from the slot machine API on startup.
    Retries a few times before giving up to handle startup race conditions.
    """
    max_retries = 5
    retry_delay_seconds = 3 # Wait 3 seconds between retries

    for attempt in range(max_retries):
        try:
            url = f"{api_url}/get_arm_configs"
            print(f"INFO: Contacting API... (Attempt {attempt + 1}/{max_retries})")
            response = requests.get(url, timeout=5) # Add a timeout
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
                sys.exit(1) # Exit the script with an error code
    return [] # Should not be reached, but good practice

def main():
    print("--- RL Agent Starting ---")
    
    arm_ids = get_arm_ids_from_api(API_BASE_URL)
    if not arm_ids:
        print("FATAL: No arms found from API. Exiting.")
        return
    print(f"INFO: Discovered {len(arm_ids)} arms: {', '.join(arm_ids)}")

    # NEW: Connect to Redis
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    
    agent = ThompsonSamplingAgent(arm_ids=arm_ids, redis_client=redis_client)
    print("INFO: Agent initialized successfully with Redis backend.")

    pull_count = 0
    while True:
        pull_count += 1
        selected_arm = agent.select_arm()
        
        try:
            response = requests.get(f"{API_BASE_URL}/choose_arm", params={'arm_id': selected_arm})
            response.raise_for_status()
            result = response.json()
            reward = result['reward']
            
            # The update_belief function now handles the atomic update and save to Redis
            agent.update_belief(arm_id=selected_arm, reward=reward)
            
            print(f"Loop {pull_count}: Chose arm {selected_arm}, got reward {reward:.2f}. Beliefs updated in Redis.")

        except requests.exceptions.RequestException as e:
            print(f"ERROR: Could not pull arm from API: {e}")
            time.sleep(5)
        
        time.sleep(1)

if __name__ == "__main__":
    main()