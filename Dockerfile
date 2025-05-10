FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first for better caching
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install TgCrypto  # Explicitly install TgCrypto

# Copy all files
COPY . .

# Environment variables (override these in Koyeb)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port (though Telegram bot doesn't need external ports)
EXPOSE 8000

CMD ["python", "main.py"]




 
