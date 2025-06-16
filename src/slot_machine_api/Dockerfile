# src/slot_machine_api/Dockerfile (Corrected Version)

# 1. Use an official lightweight Python image as the base.
FROM python:3.10-slim

# 2. Set the working directory inside the container.
WORKDIR /app

# 3. Copy the requirements file from its specific location within the build context.
COPY src/slot_machine_api/requirements.txt .

# 4. Install the Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the application's source code from its specific location.
COPY src/slot_machine_api/ .

# 6. Expose port 8000 to allow communication with the app.
EXPOSE 8000

# 7. Define the command to run the application when the container starts.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]