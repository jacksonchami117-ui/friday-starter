# FRIDAY Deployment Guide

This guide covers deployment options for the FRIDAY video outreach system.

## Deployment Options

### 1. Local Development

**Prerequisites:**
- Python 3.8+
- pip package manager
- FFmpeg (for video processing)

**Setup:**
```bash
# Clone repository
git clone <repository-url>
cd friday-starter

# Install dependencies
pip install -r requirements.txt

# Set environment variables (optional)
export FRIDAY_DEFAULT_USER=admin
export FRIDAY_DEFAULT_PASS=your-secure-password
export SECRET_KEY=your-secret-key
export DATA_DIR=./state

# Run application
python app.py
```

**Access:** http://localhost:5000

### 2. Production Deployment

**Environment Variables:**
```bash
export FLASK_ENV=production
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
export FRIDAY_DEFAULT_USER=your_admin_user
export FRIDAY_DEFAULT_PASS=your_secure_password
```

**Run with Gunicorn:**
```bash
gunicorn app:app --bind 0.0.0.0:5000 --workers 2
```

## Security Considerations

1. Change default authentication credentials
2. Use strong SECRET_KEY in production
3. Enable HTTPS in production environments
4. Regular security updates

## Monitoring

- Health check: GET /health
- Authentication status: GET /auth/status
- System metrics: GET /metrics (requires auth)

## File Structure

- Application data: `state/` directory
- Logs: `state/logs/app.log`
- Output videos: `state/outputs/videos/`
- Job data: `state/render_jobs.json`