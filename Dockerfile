# Use official Python runtime
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Install Node for frontend (if needed)
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

# Build frontend
WORKDIR /app/frontend
RUN npm install && npm run build

# Go back to root
WORKDIR /app

# Start backend (Railway provides PORT via environment variable)
CMD ["sh", "-c", "uvicorn backend.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
