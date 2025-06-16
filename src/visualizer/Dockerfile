# src/visualizer/Dockerfile

# 1. Use the same official Python runtime as other services.
FROM python:3.10-slim

# 2. Set the working directory.
WORKDIR /app

# 3. Copy requirements and install dependencies.
COPY src/visualizer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the application source code.
COPY src/visualizer/ .

# 5. Expose the port Flask will run on.
EXPOSE 5000

# 6. Define the command to run the application.
CMD ["python", "-u", "app.py"]