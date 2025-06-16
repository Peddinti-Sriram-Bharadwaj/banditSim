# src/rl_agent/main.py

import time
import requests
import sys

from agent import ThompsonSamplingAgent
from config import API_BASE_URL, STATE_FILE_PATH

def get_arm_ids_from_api(api_url: str) -> list[str]:
    """
    Fetches the list of arm IDs from the slot machine API on startup.
    If it fails, the agent cannot start, so we exit.
    """
    try:
        url = f"{api_url}/get_arm_configs"
        print(f"INFO: Contacting API to get arm configurations from {url}...")
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        arm_configs = response.json()
        return list(arm_configs.keys())
    except requests.exceptions.RequestException as e:
        print(f"FATAL: Could not connect to API to get arm configs: {e}")
        print(f"Is the Slot Machine API service running and accessible at {api_url}?")
        sys.exit(1) # Exit the script with an error code

def main():
    """The main interaction loop for the reinforcement learning agent."""
    print("--- RL Agent Starting ---")

    # 1. Discover the available arms from the API. This is crucial.
    arm_ids = get_arm_ids_from_api(API_BASE_URL)
    if not arm_ids:
        print("FATAL: No arms were found from the API. Exiting.")
        return
    
    print(f"INFO: Discovered {len(arm_ids)} arms: {', '.join(arm_ids)}")

    # 2. Initialize the agent with the discovered arms and state file path.
    agent = ThompsonSamplingAgent(arm_ids=arm_ids, state_file_path=STATE_FILE_PATH)
    print("INFO: Agent initialized successfully.")

    # 3. Start the main learning loop. This will run forever.
    pull_count = 0
    while True:
        pull_count += 1
        print(f"\n--- Loop Iteration #{pull_count} ---")

        # a. Agent selects an arm based on its current beliefs.
        selected_arm = agent.select_arm()
        print(f"ACTION: Agent chose to pull arm: {selected_arm}")

        try:
            # b. Call the API to "pull" the selected arm.
            response = requests.get(f"{API_BASE_URL}/choose_arm", params={'arm_id': selected_arm})
            response.raise_for_status()
            result = response.json()
            reward = result['reward']
            print(f"RESULT: API returned a reward of {reward:.2f}")

            # c. Agent updates its belief based on the outcome.
            agent.update_belief(arm_id=selected_arm, reward=reward)

            # d. Agent saves its new, smarter state.
            agent.save_state()
            print(f"STATUS: Beliefs for arm {selected_arm} updated and state saved.")

        except requests.exceptions.RequestException as e:
            print(f"ERROR: Could not pull arm from API: {e}")
            # If the API is down, wait a bit before retrying.
            time.sleep(5)
        
        # Wait a moment before the next pull to control the simulation speed.
        time.sleep(1)

if __name__ == "__main__":
    main()