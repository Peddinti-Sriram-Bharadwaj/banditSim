# src/rl_agent/Dockerfile

# 1. Use the same official Python runtime as the API for consistency.
FROM python:3.10-slim

# 2. Set the working directory in the container.
WORKDIR /app

# 3. Copy the requirements file first to leverage Docker's layer caching.
COPY src/rl_agent/requirements.txt .

# 4. Install the Python dependencies (numpy, scipy, requests).
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the agent's source code into the working directory.
COPY src/rl_agent/ .

# 6. Define the command to run the application when the container starts.
# The '-u' flag ensures that print statements are sent straight to stdout
# without being buffered, which is good for viewing logs in real time.
CMD ["python", "-u", "main.py"]