# src/orchestrator/Dockerfile

FROM python:3.10-slim
WORKDIR /app

COPY src/orchestrator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/orchestrator/ .

# Run the main orchestrator script
CMD ["python", "-u", "orchestrator.py"]