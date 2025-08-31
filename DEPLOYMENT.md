# 🚀 FRIDAY Deployment Guide

## Overview

FRIDAY is a Flask-based video personalization platform with Celery for background processing. This guide covers deployment to Render and local development setup.

## 🏗️ Architecture

- **Web Service**: Flask application with Gunicorn
- **Worker Service**: Celery worker for video rendering
- **Redis**: Message broker and result backend
- **PostgreSQL**: Primary database
- **File Storage**: Local disk storage for videos and assets

## 🚀 Quick Deploy to Render

### 1. Prerequisites
- GitHub repository with FRIDAY code
- Render account
- Environment variables configured

### 2. Deploy Steps

1. **Fork/Clone Repository**
   ```bash
   git clone https://github.com/your-username/friday-starter.git
   cd friday-starter
   ```

2. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial deployment setup"
   git push origin main
   ```

3. **Deploy on Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml` and deploy all services

### 3. Environment Variables

Set these in Render dashboard:

**Core Settings:**
```
SECRET_KEY=your-secret-key-here
ADMIN_PASSWORD=your-admin-password
USE_DB=1
USE_CELERY=1
```

**Optional (for notifications):**
```
SENDGRID_API_KEY=your-sendgrid-key
EMAIL_FROM=noreply@yourdomain.com
TWILIO_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_FROM=+1234567890
```

## 🛠️ Local Development

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- FFmpeg
- Redis
- PostgreSQL (optional, SQLite for development)

### 2. Setup

```bash
# Clone repository
git clone https://github.com/your-username/friday-starter.git
cd friday-starter

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install frontend dependencies
npm install

# Copy environment template
cp env.example .env
# Edit .env with your settings

# Run database migrations
alembic upgrade head

# Start Redis (if not running)
redis-server

# Start Celery worker (in new terminal)
celery -A celery_worker.celery worker --loglevel=info

# Start Flask application
python app.py
```

### 3. Development Commands

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src

# Format code
black src/
flake8 src/

# Database migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head

# Celery tasks
celery -A celery_worker.celery worker --loglevel=info
celery -A celery_worker.celery beat --loglevel=info  # For scheduled tasks
```

## 📊 Monitoring & Health Checks

### Health Endpoints
- `/health` - Basic health check
- `/diagnostics/` - Detailed system diagnostics
- `/health/celery` - Celery worker status

### Logs
- Application logs: `state/logs/app.log`
- Celery logs: Check worker console output
- Render logs: Available in Render dashboard

## 🔧 Troubleshooting

### Common Issues

1. **Celery Worker Not Starting**
   - Check Redis connection
   - Verify `REDIS_URL` environment variable
   - Check Celery worker logs

2. **Video Rendering Fails**
   - Verify FFmpeg installation
   - Check disk space
   - Review render engine logs

3. **Database Connection Issues**
   - Verify `DATABASE_URL`
   - Run migrations: `alembic upgrade head`
   - Check database permissions

4. **File Upload Issues**
   - Verify `STATE_DIR` permissions
   - Check disk space
   - Ensure upload directories exist

### Debug Mode

Enable debug mode for development:
```bash
export FLASK_ENV=development
export DEBUG=true
python app.py
```

## 🔒 Security Considerations

1. **Environment Variables**
   - Never commit `.env` files
   - Use strong `SECRET_KEY`
   - Set secure `ADMIN_PASSWORD`

2. **Database Security**
   - Use strong database passwords
   - Enable SSL for production databases
   - Regular backups

3. **File Uploads**
   - Validate file types
   - Limit file sizes
   - Scan for malware

## 📈 Scaling

### Horizontal Scaling
- Multiple Celery workers
- Load balancer for web services
- Redis cluster for high availability

### Vertical Scaling
- Increase worker concurrency
- Optimize video rendering
- Database query optimization

## 🔄 CI/CD Pipeline

The repository includes GitHub Actions for:
- Automated testing
- Code quality checks
- Coverage reporting
- Deployment to staging

## 📞 Support

For issues and questions:
1. Check the logs
2. Review this documentation
3. Open a GitHub issue
4. Contact the development team

---

**Happy Deploying! 🎬**
