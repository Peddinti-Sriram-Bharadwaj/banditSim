# src/slot_machine_api/config.py

# This dictionary holds a more challenging "ground truth" for our slot machine arms.
# The goal is to make it harder for the Thompson Sampling agent to be certain
# which arm is truly the best without significant exploration.

ARM_CONFIGS = {
    "0": {"mean": 2.8, "std_dev": 0.8},  # The "Safe Bet": Consistently good, but not the best.
    
    "1": {"mean": 3.0, "std_dev": 3.0},  # The "High-Risk, High-Reward" Winner: Best on average, but very volatile.
                                        # Its rewards will frequently overlap with other arms.

    "2": {"mean": 2.2, "std_dev": 0.3},  # The "Good Enough" Trap: Very low variance, so it seems reliable.
                                        # An agent might lock onto this for a while and stop exploring.

    "3": {"mean": 0.5, "std_dev": 5.0},  # The "Lottery Ticket": Almost always bad, but a very high standard
                                        # deviation means it could rarely give a massive payout, confusing the agent.

    "4": {"mean": -0.5, "std_dev": 0.5}  # The Clear Loser: Consistently bad, to ensure the agent can still
                                        # learn to avoid obviously poor choices.
}