# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Prevent Python from writing .pyc files & enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Make sure Python can always find your code and the src package
ENV PYTHONPATH=/app:/app/src

# Install system dependencies (needed for pandas, psycopg2, ffmpeg, etc.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        ffmpeg \
        libpq-dev \
        && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Set default port
ENV PORT=8000
EXPOSE 8000

# Run Gunicorn with the Flask app
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT}"]
