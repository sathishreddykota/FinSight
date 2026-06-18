# Use official Python runtime with build tools
FROM python:3.11

WORKDIR /app

# Install system dependencies needed for ML packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Install Node for frontend
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Build frontend
WORKDIR /app/frontend
RUN npm install && npm run build

# Go back to root
WORKDIR /app

# Start backend (Railway provides PORT via environment variable)
CMD ["sh", "-c", "uvicorn backend.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
