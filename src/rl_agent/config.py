# src/rl_agent/config.py (Updated to use Environment Variables)

import os

# The agent will now read its configuration from environment variables.
# We provide the Docker Compose hostnames as default values for local testing.
API_BASE_URL = os.getenv("API_BASE_URL", "http://slot-machine-api:8000")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))