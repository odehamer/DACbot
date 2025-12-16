# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for audio and ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY tiktoklive.py .

# Create directory for logs
RUN mkdir -p /app/logs

# Note: Environment variables should be set at runtime via Azure Container Instances configuration
# Do not set DISCORD_TOKEN or DISCORD_CHANNEL_ID here for security reasons

# Run the bot
CMD ["python", "-u", "main.py"]
