# src/slot_machine_api/config.py

# This dictionary is designed to be "easy" for the system to solve,
# allowing for quick and clear observation of the MLOps lifecycle.

ARM_CONFIGS = {
    "0": {"mean": 1.5, "std_dev": 0.5},  # A clearly suboptimal, but positive arm.
    
    "1": {"mean": 5.0, "std_dev": 1.0},  # The undisputed BEST arm. Agents will lock onto this very quickly.

    "2": {"mean": 0.5, "std_dev": 0.5},  # Another suboptimal arm.

    "3": {"mean": -1.0, "std_dev": 1.0}, # A clearly bad arm.
    
    "4": {"mean": -3.0, "std_dev": 0.5}  # The undisputed WORST arm.
}