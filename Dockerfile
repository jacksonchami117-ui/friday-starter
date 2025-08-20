# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Ensure Python can find src package
ENV PYTHONPATH=/app:/app/src

# Install system dependencies
RUN apt-get update &&     apt-get install -y --no-install-recommends build-essential &&     rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip &&     pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT}"]
