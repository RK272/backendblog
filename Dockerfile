FROM python:3.10-slim-buster

# Install system dependencies
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    portaudio19-dev \
    gcc \
    python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Install awscli via pip
RUN pip install --no-cache-dir awscli

# Set the working directory
WORKDIR /app

# Copy the application files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install PyAudio (if still needed separately)
# RUN pip install --no-cache-dir pyaudio  # Comment this out if pyaudio is already in requirements.txt

# Define the command to run the application
CMD ["python3", "app.py"]
