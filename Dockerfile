# Use official Python image as base
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR off
ENV PIP_DISABLE_PIP_VERSION_CHECK on

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Create directory for logs
RUN mkdir -p /app/logs

# Set environment variables for configuration
# (These can be overridden in Koyeb dashboard)
ENV API_ID=your_api_id
ENV API_HASH=your_api_hash
ENV BOT_TOKEN=your_bot_token
ENV MONGO_URI=your_mongodb_uri
ENV OWNER_ID=your_owner_id
ENV LOG_CHANNEL=your_log_channel
ENV FORCE_SUB_CHANNEL=your_force_sub_channel

# Expose port (though Telegram bot doesn't need external ports)
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]