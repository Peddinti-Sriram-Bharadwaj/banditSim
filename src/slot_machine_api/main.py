# src/slot_machine_api/main.py
import numpy as np
from fastapi import FastAPI, HTTPException

# Import the arm configurations from our config file
from config import ARM_CONFIGS

app = FastAPI(
    title="K-Armed Bandit Simulation: Slot Machine API",
    description="Provides rewards for a simulated multi-armed bandit.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    """A simple root endpoint to confirm the API is running."""
    return {"message": "Slot Machine API is running. Visit /docs for API documentation."}


@app.get("/get_arm_configs")
def get_arm_configs():
    """Returns the true mean and standard deviation for all available arms."""
    return ARM_CONFIGS


@app.get("/choose_arm")
def choose_arm(arm_id: int):
    """
    Simulates choosing an arm and getting a reward.

    - **arm_id**: The integer ID of the arm to pull.
    - **Returns**: A reward sampled from the arm's Gaussian distribution.
    """
    # Convert int to string to match the keys in our config dictionary
    arm_id_str = str(arm_id)

    if arm_id_str not in ARM_CONFIGS:
        raise HTTPException(
            status_code=404, 
            detail=f"Arm ID '{arm_id}' not found. Available arms: {list(ARM_CONFIGS.keys())}"
        )

    config = ARM_CONFIGS[arm_id_str]
    mean = config["mean"]
    std_dev = config["std_dev"]

    # Sample a reward from a Gaussian (normal) distribution
    reward = np.random.normal(loc=mean, scale=std_dev)

    return {"arm_id": arm_id, "reward": reward}