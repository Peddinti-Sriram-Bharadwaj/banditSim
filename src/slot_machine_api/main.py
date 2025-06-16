# src/slot_machine_api/main.py (Updated to allow drift)
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Import the initial arm configurations from our config file
from config import ARM_CONFIGS

# --- State ---
# We copy the imported config into a new variable that can be modified at runtime.
# This is the crucial change that allows us to simulate drift.
current_arm_configs = ARM_CONFIGS.copy()

app = FastAPI(
    title="K-Armed Bandit Simulation: Slot Machine API",
    description="Provides rewards for a simulated multi-armed bandit.",
    version="1.1.0"
)

# Define the request body model for the new endpoint
class ArmUpdate(BaseModel):
    mean: float

@app.get("/")
def read_root():
    """A simple root endpoint to confirm the API is running."""
    return {"message": "Slot Machine API is running. Visit /docs for API documentation."}


@app.get("/get_arm_configs")
def get_arm_configs():
    """Returns the CURRENT true mean and standard deviation for all available arms."""
    return current_arm_configs


@app.get("/choose_arm")
def choose_arm(arm_id: int):
    """Simulates choosing an arm and getting a reward from the CURRENT distribution."""
    arm_id_str = str(arm_id)
    if arm_id_str not in current_arm_configs:
        raise HTTPException(status_code=404, detail=f"Arm ID '{arm_id}' not found.")

    config = current_arm_configs[arm_id_str]
    reward = np.random.normal(loc=config["mean"], scale=config["std_dev"])
    return {"arm_id": arm_id, "reward": reward}


# --- THIS IS THE NEW ENDPOINT ---
@app.post("/update_arm/{arm_id}")
def update_arm_mean(arm_id: int, arm_update: ArmUpdate):
    """
    Updates the mean reward for a specific arm to simulate concept drift.
    """
    arm_id_str = str(arm_id)
    if arm_id_str not in current_arm_configs:
        raise HTTPException(status_code=404, detail=f"Arm ID '{arm_id}' not found.")

    old_mean = current_arm_configs[arm_id_str]['mean']
    current_arm_configs[arm_id_str]['mean'] = arm_update.mean

    print(f"*** CONCEPT DRIFT TRIGGERED MANUALLY FOR ARM {arm_id_str} ***")
    print(f"Arm {arm_id_str} mean changed from {old_mean} to {arm_update.mean}")

    return {"message": f"Arm {arm_id_str} mean updated successfully.", "new_config": current_arm_configs[arm_id_str]}