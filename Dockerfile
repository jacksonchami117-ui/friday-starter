# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Ensure Python can find src package
ENV PYTHONPATH=/app:/app/src

RUN apt-get update -y && apt-get install -y --no-install-recommends \
	ffmpeg \
	fonts-dejavu-core \
	&& rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

ENV PORT=8000
ENV STATE_DIR=/data/state
VOLUME ["/data"]
EXPOSE 10000

CMD ["sh","-c","exec gunicorn app:app -w 1 -k gthread --threads 8 --timeout 240 -b 0.0.0.0:${PORT:-10000}"]
