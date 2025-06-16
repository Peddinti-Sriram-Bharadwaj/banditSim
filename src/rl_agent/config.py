# src/rl_agent/config.py

# The base URL of the slot machine API.
# When we run this with Docker Compose, 'slot-machine-api' will be the
# resolvable hostname for the API service.
API_BASE_URL = "http://slot-machine-api:8000"

# The local path inside the container where the agent's state will be saved.
# We will mount a Docker volume to this path.
STATE_FILE_PATH = "/data/agent_state.json"