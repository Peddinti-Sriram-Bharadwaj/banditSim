# Distributed K-Armed Bandit Simulation with a Full MLOps Lifecycle

This project implements a complete, multi-service, distributed simulation of the K-Armed Bandit problem. It serves as a practical, hands-on demonstration of key MLOps and DevOps principles, including containerization, orchestration, state management, convergence detection, concept drift monitoring, and autonomous re-learning.

The system starts with multiple reinforcement learning agents exploring an environment to find the optimal choice. It then automatically detects when the agents have learned enough, switches to a monitoring mode, detects when the environment changes (drift), and triggers a system-wide re-learning cycle, all without human intervention.

***

## Table of Contents
- [Features](#features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Running with Docker Compose (Local Development)](#running-with-docker-compose)
  - [Deploying to Kubernetes (Minikube)](#deploying-to-kubernetes)
- [Demonstrating the Full MLOps Lifecycle](#demonstrating-the-full-mlops-lifecycle)
- [Future Improvements](#future-improvements)

***

## Features

- **Distributed RL Agents:** Runs multiple Thompson Sampling agents in parallel, all contributing to a shared understanding of the environment.
- **Centralized State Management:** Uses a Redis database as a high-speed, central source of truth for the agents' beliefs, solving race conditions.
- **Live Visualization:** A real-time dashboard built with Flask and Plotly.js that visualizes the ground truth vs. the agents' learned beliefs as they evolve.
- **Autonomous Orchestrator:** A dedicated service that monitors the entire system's state.
- **Convergence Detection:** The orchestrator can determine when the agents have successfully learned the optimal solution.
- **Concept Drift Detection:** After convergence, the orchestrator monitors the environment and can detect when the underlying problem changes (e.g., the best option becomes worse).
- **Autonomous Re-learning:** Upon detecting drift, the system automatically triggers a new, system-wide exploration phase to adapt to the new environment.
- **Containerized Services:** All 5 microservices are fully containerized using Docker for portability and isolation.
- **Production-Ready Manifests:** Includes a complete set of Kubernetes manifests (`Deployments`, `Services`, `ConfigMaps`) for deploying the application to a production-like environment.

***

## System Architecture

The application is composed of five distinct microservices orchestrated to work together:

1.  **Slot Machine API (`slot-machine-api`)**: A FastAPI application that simulates the K-armed bandit environment. It provides rewards and has an endpoint to dynamically change the environment to simulate drift.
2.  **RL Agent (`rl-agent`)**: A Python-based Thompson Sampling agent. This service is scaled to multiple replicas, each acting independently but sharing knowledge through Redis.
3.  **Redis (`redis`)**: The centralized state store. It holds the collective beliefs of all agents, ensuring a consistent and up-to-date understanding of the environment.
4.  **Visualizer (`visualizer`)**: A Flask web application that provides a live dashboard, querying both the API (for ground truth) and Redis (for agent beliefs) to render real-time comparison plots.
5.  **Orchestrator (`orchestrator`)**: The "brain" of the MLOps system. This service watches the state in Redis to detect convergence and drift, and then orchestrates the system's behavior in response.

***

## Technology Stack

- **Backend:** Python 3.10+
- **API Framework:** FastAPI
- **Web Dashboard:** Flask
- **Reinforcement Learning:** NumPy, SciPy
- **Database / State Store:** Redis
- **Containerization:** Docker
- **Local Orchestration:** Docker Compose
- **Production Orchestration:** Kubernetes
- **Frontend Visualization:** Plotly.js

***

## Project Structure
Of course. It's essential to update the documentation with these real-world debugging steps and alternative commands. A good README reflects the reality of making the project work.

I will update the "Deploying to Kubernetes" section to include the troubleshooting steps for Minikube on macOS and the kubectl port-forward command as the primary way to access the service.

Here is the complete, final version of the README.md file.

Markdown
# Distributed K-Armed Bandit Simulation with a Full MLOps Lifecycle

This project implements a complete, multi-service, distributed simulation of the K-Armed Bandit problem. It serves as a practical, hands-on demonstration of key MLOps and DevOps principles, including containerization, orchestration, state management, convergence detection, concept drift monitoring, and autonomous re-learning.

The system starts with multiple reinforcement learning agents exploring an environment to find the optimal choice. It then automatically detects when the agents have learned enough, switches to a monitoring mode, detects when the environment changes (drift), and triggers a system-wide re-learning cycle, all without human intervention.

***

## Table of Contents
- [Features](#features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Running with Docker Compose (Local Development)](#running-with-docker-compose)
  - [Deploying to Kubernetes (Minikube)](#deploying-to-kubernetes)
- [Demonstrating the Full MLOps Lifecycle](#demonstrating-the-full-mlops-lifecycle)
- [Future Improvements](#future-improvements)

***

## Features

- **Distributed RL Agents:** Runs multiple Thompson Sampling agents in parallel, all contributing to a shared understanding of the environment.
- **Centralized State Management:** Uses a Redis database as a high-speed, central source of truth for the agents' beliefs, solving race conditions.
- **Live Visualization:** A real-time dashboard built with Flask and Plotly.js that visualizes the ground truth vs. the agents' learned beliefs as they evolve.
- **Autonomous Orchestrator:** A dedicated service that monitors the entire system's state.
- **Convergence Detection:** The orchestrator can determine when the agents have successfully learned the optimal solution.
- **Concept Drift Detection:** After convergence, the orchestrator monitors the environment and can detect when the underlying problem changes (e.g., the best option becomes worse).
- **Autonomous Re-learning:** Upon detecting drift, the system automatically triggers a new, system-wide exploration phase to adapt to the new environment.
- **Containerized Services:** All 5 microservices are fully containerized using Docker for portability and isolation.
- **Production-Ready Manifests:** Includes a complete set of Kubernetes manifests (`Deployments`, `Services`, `ConfigMaps`) for deploying the application to a production-like environment.

***

## System Architecture

The application is composed of five distinct microservices orchestrated to work together:

1.  **Slot Machine API (`slot-machine-api`)**: A FastAPI application that simulates the K-armed bandit environment. It provides rewards and has an endpoint to dynamically change the environment to simulate drift.
2.  **RL Agent (`rl-agent`)**: A Python-based Thompson Sampling agent. This service is scaled to multiple replicas, each acting independently but sharing knowledge through Redis.
3.  **Redis (`redis`)**: The centralized state store. It holds the collective beliefs of all agents, ensuring a consistent and up-to-date understanding of the environment.
4.  **Visualizer (`visualizer`)**: A Flask web application that provides a live dashboard, querying both the API (for ground truth) and Redis (for agent beliefs) to render real-time comparison plots.
5.  **Orchestrator (`orchestrator`)**: The "brain" of the MLOps system. This service watches the state in Redis to detect convergence and drift, and then orchestrates the system's behavior in response.

***

## Technology Stack

- **Backend:** Python 3.10+
- **API Framework:** FastAPI
- **Web Dashboard:** Flask
- **Reinforcement Learning:** NumPy, SciPy
- **Database / State Store:** Redis
- **Containerization:** Docker
- **Local Orchestration:** Docker Compose
- **Production Orchestration:** Kubernetes
- **Frontend Visualization:** Plotly.js

***

## Project Structure

.
├── kubernetes/                      # Kubernetes manifests for all services
│   ├── api-deployment.yaml
│   ├── api-service.yaml
│   ├── agent-configmap.yaml
│   ├── agent-deployment.yaml
│   ├── orchestrator-deployment.yaml
│   ├── orchestrator-configmap.yaml
│   ├── redis-deployment.yaml
│   ├── redis-service.yaml
│   ├── visualizer-deployment.yaml
│   └── visualizer-service.yaml
│
├── src/                             # Source code for all microservices
│   ├── slot_machine_api/            # FastAPI-based environment simulator
│   │   ├── main.py
│   │   ├── bandit.py
│   │   └── Dockerfile
│   │
│   ├── rl_agent/                    # Thompson Sampling agent logic
│   │   ├── agent.py
│   │   ├── utils.py
│   │   └── Dockerfile
│   │
│   ├── visualizer/                  # Flask + Plotly.js real-time dashboard
│   │   ├── app.py
│   │   ├── templates/
│   │   └── Dockerfile
│   │
│   └── orchestrator/                # System state watcher and controller
│       ├── orchestrator.py
│       ├── state_utils.py
│       └── Dockerfile
│
├── docker-compose.yaml              # Local development orchestrator
├── requirements.txt                 # Shared Python dependencies (if any)
└── README.md                        # You're reading it!



***

## Getting Started

### Prerequisites
- Docker & Docker Desktop
- Docker Compose
- `kubectl` (Kubernetes command-line tool)
- Minikube (for local Kubernetes deployment)
- `curl` (for triggering drift)
- For macOS users, `brew install qemu` may be required.

### Running with Docker Compose
This is the simplest way to run the entire application locally.

1.  **Clone the repository.**

2.  **Build and run the services:** From the root of the project directory, run:
    ```bash
    docker-compose up --build
    ```

3.  **Access the services:**
    - **Live Dashboard:** Open your browser to `http://localhost:5001`
    - **API Docs:** Open your browser to `http://localhost:8000/docs`

### Deploying to Kubernetes
These steps will deploy the application to a local Minikube cluster.

1.  **Start Minikube (Recommended for macOS):**
    If you encounter networking issues with the default driver on macOS, using the `qemu2` driver is more stable.
    ```bash
    # First-time setup with QEMU driver
    minikube start --driver=qemu2
    ```
    *If you ever encounter persistent startup errors, a full reset (`minikube delete --all && minikube start ...`) is the best solution.*

2.  **Point your Docker CLI to Minikube's daemon:** This allows you to build images directly into your cluster's environment.
    ```bash
    eval $(minikube docker-env)
    ```

3.  **Build all custom images:**
    ```bash
    docker build -t slot-machine-api:latest -f src/slot_machine_api/Dockerfile .
    docker build -t rl-agent:latest -f src/rl_agent/Dockerfile .
    docker build -t visualizer:latest -f src/visualizer/Dockerfile .
    docker build -t orchestrator:latest -f src/orchestrator/Dockerfile .
    ```

4.  **Apply all Kubernetes manifests:** This single command creates all deployments, services, and config maps.
    ```bash
    kubectl apply -f kubernetes/
    ```

5.  **Check the status:** Wait for all pods to be in the `Running` state.
    ```bash
    kubectl get pods -w
    ```

6.  **Access the Visualizer using Port-Forwarding:**
    The `minikube service` command can be unreliable with some drivers. The most robust way to access the dashboard is with `kubectl port-forward`.

    a. **Find your visualizer pod name:**
    ```bash
    kubectl get pods
    ```
    Look for the pod starting with `visualizer-deployment-...`.

    b. **Start forwarding:** In a **new terminal window**, run the following command, replacing `<your-visualizer-pod-name>` with the name from the previous step.
    ```bash
    # Example: kubectl port-forward visualizer-deployment-857c6dfc6b-vp96p 5001:5000
    kubectl port-forward <your-visualizer-pod-name> 5001:5000
    ```
    This command will hang, which means it's actively forwarding traffic.

    c. **Open your browser:** Navigate to `http://localhost:5001` to view the live dashboard.

***

## Demonstrating the Full MLOps Lifecycle

Once the system is running (either with Docker Compose or Kubernetes), you can test the full autonomous cycle.

1.  **Phase 1: Convergence**
    - Open the visualizer dashboard. Watch the "Agent's Learned Beliefs" plot.
    - The agents will quickly identify the best arm, and the violin plot will become tall and narrow around its true mean.
    - Check the container logs. The `orchestrator` will eventually print `>>> SYSTEM CONVERGED ...`.

2.  **Phase 2: Trigger Concept Drift**
    - The system is now in `DRIFT_MONITORING` mode. Let's make the best arm worse and a suboptimal arm better.
    - Open another new terminal and run these `curl` commands:
      ```bash
      # Nerf the current best arm (e.g., Arm 1)
      curl -X POST "http://localhost:8000/update_arm/1" -H "Content-Type: application/json" -d '{"mean": 0.0}'
      
      # Buff a different arm (e.g., Arm 0) to be the new best
      curl -X POST "http://localhost:8000/update_arm/0" -H "Content-Type: application/json" -d '{"mean": 6.0}'
      ```

3.  **Phase 3: Observe Drift Detection & Re-Learning**
    - Go back to the logs from `kubectl` or `docker-compose`. The agents exploiting the old best arm will now receive poor rewards.
    - The `orchestrator` will notice this change and print `!!! DRIFT DETECTED !!!`.
    - Immediately after, it will trigger the `handle_drift` function, which resets all beliefs and puts the system into `FORCED_EXPLORATION` mode.
    - You will see the agents choosing arms randomly for 30 seconds.
    - After 30 seconds, the system will return to `LEARNING` mode and will now quickly converge on the new best arm. The cycle is complete.

***

## Future Improvements

- **CI/CD Pipeline:** Implement a Jenkins or GitHub Actions pipeline to automate testing, image building/pushing, and deployment to Kubernetes.
- **Metrics & Monitoring:** Integrate Prometheus client libraries into the Python apps to expose metrics, and build a Grafana dashboard to monitor system health and model performance over time.
- **Helm Charts:** Package the Kubernetes manifests into a Helm chart for easier, more configurable deployments.
- **Advanced UI:** Enhance the visualizer to include more plots (e.g., cumulative reward/regret) and user controls (e.g., a "reset" button).