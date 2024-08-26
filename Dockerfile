# Use the official Python image from the Docker Hub
FROM python:3.10-slim-buster

# Install system dependencies
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    awscli \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Define the command to run the application
CMD ["python3", "app.py"]
