FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Clone your repository
RUN git clone https://github.com/vijaykumar58/Save-Restricted-Content-BotAi .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install TgCrypto

# Set Python path
ENV PYTHONPATH=/app

# Expose port (though Telegram bot doesn't need external ports)
EXPOSE 8000

CMD ["python", "main.py"]
 
 
 
