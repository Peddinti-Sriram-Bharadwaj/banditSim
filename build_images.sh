docker build -t slot-machine-api:latest -f src/slot_machine_api/Dockerfile .
docker build -t rl-agent:latest -f src/rl_agent/Dockerfile .
docker build -t visualizer:latest -f src/visualizer/Dockerfile .
docker build -t orchestrator:latest -f src/orchestrator/Dockerfile .