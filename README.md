# Distributed K-Armed Bandit Simulation with a Full MLOps Lifecycle

This project implements a complete, multi-service, distributed simulation of the K-Armed Bandit problem. It serves as a practical, hands-on demonstration of key MLOps and DevOps principles, including containerization, orchestration, state management, convergence detection, concept drift monitoring, and autonomous re-learning.

The system starts with multiple reinforcement learning agents exploring an environment to find the optimal choice. It then automatically detects when the agents have learned enough, switches to a monitoring mode, detects when the environment changes (drift), and triggers a system-wide re-learning cycle, all without human intervention.

---

## Table of Contents

* [Features](#features)
* [System Architecture](#system-architecture)
* [Technology Stack](#technology-stack)
* [Project Structure](#project-structure)
* [Getting Started](#getting-started)

  * [Prerequisites](#prerequisites)
  * [Running with Docker Compose (Local Development)](#running-with-docker-compose)
  * [Deploying to Kubernetes (Minikube)](#deploying-to-kubernetes)
* [Demonstrating the Full MLOps Lifecycle](#demonstrating-the-full-mlops-lifecycle)
* [Future Improvements](#future-improvements)

---

## Features

* **Distributed RL Agents:** Runs multiple Thompson Sampling agents in parallel, all contributing to a shared understanding of the environment.
* **Centralized State Management:** Uses a Redis database as a high-speed, central source of truth for the agents' beliefs, solving race conditions.
* **Live Visualization:** A real-time dashboard built with Flask and Plotly.js that visualizes the ground truth vs. the agents' learned beliefs as they evolve.
* **Autonomous Orchestrator:** A dedicated service that monitors the entire system's state.
* **Convergence Detection:** The orchestrator can determine when the agents have successfully learned the optimal solution.
* **Concept Drift Detection:** After convergence, the orchestrator monitors the environment and can detect when the underlying problem changes (e.g., the best option becomes worse).
* **Autonomous Re-learning:** Upon detecting drift, the system automatically triggers a new, system-wide exploration phase to adapt to the new environment.
* **Containerized Services:** All 5 microservices are fully containerized using Docker for portability and isolation.
* **Production-Ready Manifests:** Includes a complete set of Kubernetes manifests (`Deployments`, `Services`, `ConfigMaps`) for deploying the application to a production-like environment.

---

## System Architecture

The application is composed of five distinct microservices orchestrated to work together:

1. **Slot Machine API (`slot-machine-api`)**: A FastAPI application that simulates the K-armed bandit environment. It provides rewards and has an endpoint to dynamically change the environment to simulate drift.
2. **RL Agent (`rl-agent`)**: A Python-based Thompson Sampling agent. This service is scaled to multiple replicas, each acting independently but sharing knowledge through Redis.
3. **Redis (`redis`)**: The centralized state store. It holds the collective beliefs of all agents, ensuring a consistent and up-to-date understanding of the environment.
4. **Visualizer (`visualizer`)**: A Flask web application that provides a live dashboard, querying both the API (for ground truth) and Redis (for agent beliefs) to render real-time comparison plots.
5. **Orchestrator (`orchestrator`)**: The "brain" of the MLOps system. This service watches the state in Redis to detect convergence and drift, and then orchestrates the system's behavior in response.

---

## Technology Stack

* **Backend:** Python 3.10+
* **API Framework:** FastAPI
* **Web Dashboard:** Flask
* **Reinforcement Learning:** NumPy, SciPy
* **Database / State Store:** Redis
* **Containerization:** Docker
* **Local Orchestration:** Docker Compose
* **Production Orchestration:** Kubernetes
* **Frontend Visualization:** Plotly.js

---

## Project Structure

<details>
<summary> Project Structure</summary>

```
. 
├── README.md
├── build_images.sh
├── docker-compose.yaml
├── docs/
│   └── placeholder.txt
├── kubernetes/
│   ├── agent-configmap.yaml
│   ├── agent-deployment.yaml
│   ├── api-deployment.yaml
│   ├── api-service.yaml
│   ├── debug-pod.yaml
│   ├── orchestrator-configmap.yaml
│   ├── orchestrator-deployment.yaml
│   ├── placeholder.txt
│   ├── redis-deployment.yaml
│   ├── redis-service.yaml
│   ├── visualizer-configmap.yaml
│   ├── visualizer-deployment.yaml
│   └── visualizer-service.yaml
├── port_forward.sh
├── scripts/
│   ├── jenkins/
│   └── placeholder.txt
├── src/
│   ├── orchestrator/
│   │   ├── Dockerfile
│   │   ├── orchestrator.py
│   │   └── requirements.txt
│   ├── rl_agent/
│   │   ├── Dockerfile
│   │   ├── agent.py
│   │   ├── config.py
│   │   ├── drift_detector.py
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── slot_machine_api/
│   │   ├── Dockerfile
│   │   ├── __pycache__/
│   │   ├── config.py
│   │   ├── main.py
│   │   └── requirements.txt
│   └── visualizer/
│       ├── Dockerfile
│       ├── app.py
│       ├── config.py
│       ├── requirements.txt
│       ├── static/
│       └── templates/
└── tests/
    ├── integration/
    │   └── placeholder.txt
    └── unit/
        └── placeholder.txt
```

</details>

---

## Getting Started

### Prerequisites

* Docker & Docker Desktop
* Docker Compose
* `kubectl` (Kubernetes command-line tool)
* Minikube (for local Kubernetes deployment)
* `curl` (for triggering drift)
* For macOS users, `brew install qemu` may be required.

### Running with Docker Compose

This is the simplest way to run the entire application locally.

1. **Clone the repository.**

2. **Build and run the services:**

```bash
docker-compose up --build
```

3. **Access the services:**

* **Live Dashboard:** [http://localhost:5001](http://localhost:5001)
* **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

### Deploying to Kubernetes

1. **Start Minikube:**

```bash
minikube start --driver=qemu2
```

2. **Point Docker to Minikube:**

```bash
eval $(minikube docker-env)
```

3. **Build Docker images:**

```bash
docker build -t slot-machine-api:latest -f src/slot_machine_api/Dockerfile .
docker build -t rl-agent:latest -f src/rl_agent/Dockerfile .
docker build -t visualizer:latest -f src/visualizer/Dockerfile .
docker build -t orchestrator:latest -f src/orchestrator/Dockerfile .
```

4. **Apply Kubernetes manifests:**

```bash
kubectl apply -f kubernetes/
```

5. **Check pods:**

```bash
kubectl get pods -w
```

6. **Port-forward Visualizer:**

```bash
kubectl get pods  # get visualizer pod name
kubectl port-forward <your-visualizer-pod-name> 5001:5000
```

7. **Visit dashboard:** [http://localhost:5001](http://localhost:5001)

---

## Demonstrating the Full MLOps Lifecycle

1. **Convergence Phase**

   * Observe the violin plot converging to the best arm.
   * Orchestrator logs: `>>> SYSTEM CONVERGED ...`

2. **Trigger Drift**

```bash
curl -X POST "http://localhost:8000/update_arm/1" -H "Content-Type: application/json" -d '{"mean": 0.0}'
curl -X POST "http://localhost:8000/update_arm/0" -H "Content-Type: application/json" -d '{"mean": 6.0}'
```

3. **Observe System Response**

   * Logs show: `!!! DRIFT DETECTED !!!`
   * Mode switches to `FORCED_EXPLORATION` → `LEARNING`
   * New convergence completes

---

## Future Improvements

* **CI/CD:** Add Jenkins or GitHub Actions.
* **Monitoring:** Integrate Prometheus + Grafana.
* **Packaging:** Use Helm charts.
* **UI:** Add controls, reset buttons, regret plots, etc.
