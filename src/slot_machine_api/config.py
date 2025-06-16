# src/slot_machine_api/config.py

# This dictionary holds the "ground truth" for our slot machine arms.
# Each arm is defined by a mean (mu) and a standard deviation (sigma),
# which control the Gaussian (normal) distribution of its rewards.
#
# A higher mean indicates a better arm on average.
# A higher standard deviation indicates more risk/variance in the rewards.

ARM_CONFIGS = {
    "0": {"mean": 2.5, "std_dev": 1.0},
    "1": {"mean": 3.5, "std_dev": 1.5},  # The best arm, but with some risk
    "2": {"mean": 1.0, "std_dev": 0.5},  # A safe, but low-reward arm
    "3": {"mean": 0.0, "std_dev": 2.0},  # A high-risk, low-reward arm
    "4": {"mean": -1.0, "std_dev": 0.2}  # A consistently bad arm
}