# FRIDAY Starter System

A modular Flask application for personalized video outreach and lead management with notifications, admin tools, analytics, and database persistence.

## Features

### Core Modules
- **Leads** — Upload CSV/XLSX files, validate, process accepted vs rejected leads
- **Orders** — Order management and processing (placeholder module)  
- **Render** — Generate personalized videos per lead using FFmpeg
- **Exports** — Export data for Instantly/Smartlead CSV + batch ZIP files
- **Diagnostics** — Package logs/CSVs for system debugging
- **Editor** — Drag/drop video segments, save template manifests

### New Feature Packs
- **Notifications** — Email/SMS notifications with env-configurable providers
- **Admin Tools** — User, job, and lead management interfaces
- **Analytics** — Performance dashboard with Chart.js visualizations  
- **Database Persistence** — SQLite storage with CSV fallback mode

## Environment Variables

### Core Configuration
- `SECRET_KEY` — Flask secret key (default: "dev-secret-key")
- `DATA_DIR` — Data storage directory (default: "./state")  
- `PORT` — Server port (default: 5000)
- `SAFE_MODE` — Enable safe mode startup (default: "0")

### Database Configuration
- `USE_DB` — Enable database persistence (default: "0", set to "1" to enable)
  - When enabled: Uses SQLite database for lead/job/video storage
  - When disabled: Falls back to CSV file storage

### Notifications Configuration
- `NOTIFICATIONS_ENABLED` — Enable/disable notifications globally (default: "1")
- `EMAIL_PROVIDER` — Email provider: "smtp", "sendgrid" (default: "smtp")
- `SMS_PROVIDER` — SMS provider: "twilio", "aws-sns" (default: "twilio")

### Provider-Specific Settings
#### SMTP Email
- `SMTP_SERVER` — SMTP server hostname
- `SMTP_PORT` — SMTP server port
- `SMTP_USERNAME` — SMTP username
- `SMTP_PASSWORD` — SMTP password
- `SMTP_TLS` — Enable TLS (default: "1")

#### SendGrid
- `SENDGRID_API_KEY` — SendGrid API key

#### Twilio SMS
- `TWILIO_ACCOUNT_SID` — Twilio Account SID
- `TWILIO_AUTH_TOKEN` — Twilio Auth Token
- `TWILIO_FROM_PHONE` — Twilio phone number

#### AWS SNS
- `AWS_ACCESS_KEY_ID` — AWS access key
- `AWS_SECRET_ACCESS_KEY` — AWS secret key
- `AWS_REGION` — AWS region for SNS

## Quick Start

### Local Development

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   sudo apt-get install -y ffmpeg  # For video processing
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run the Application**
   ```bash
   python app.py
   ```

4. **Access the System**
   - Main interface: http://localhost:5000
   - Dashboard: http://localhost:5000/dashboard
   - Analytics: http://localhost:5000/analytics
   - Admin Tools: http://localhost:5000/admin/users

### Database Setup

To enable database persistence:

```bash
export USE_DB=1
python app.py
```

The system will automatically:
- Create SQLite database at `{DATA_DIR}/db/friday.db`
- Initialize schema for leads, jobs, videos, analytics
- Migrate existing CSV data when available

### Docker Deployment

```bash
docker-compose up -d
```

### Production Deployment

```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# With environment variables
USE_DB=1 NOTIFICATIONS_ENABLED=1 gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Architecture

### Data Storage
- **CSV Mode** (default): Stores data in CSV files under `{DATA_DIR}/`
- **Database Mode** (USE_DB=1): Uses SQLite with automatic CSV migration

### Directory Structure
```
state/                  # Default DATA_DIR
├── uploads/           # Uploaded lead files
├── outputs/          
│   ├── videos/       # Generated videos
│   └── thumbs/       # Video thumbnails
├── logs/             # Application logs
├── batches/          # Batch processing data
├── assets/           # Media assets
├── templates/        # Dynamic templates
├── db/               # SQLite databases
│   └── friday.db     # Main database file
├── accepted_leads.csv # Validated leads (CSV mode)
└── rejected_leads.csv # Invalid leads
```

### Blueprints
- `/leads` — Lead upload and management
- `/orders` — Order processing
- `/render` — Video generation
- `/exports` — Data export functionality  
- `/diagnostics` — System diagnostics
- `/editor` — Video template editor
- `/notify` — Notification management
- `/admin` — Admin interfaces
- `/analytics` — Analytics dashboard

## API Endpoints

### System
- `GET /health` — Health check
- `GET /api/data-source` — Current data source info

### Notifications
- `POST /notify/toggle` — Toggle session notifications
- `GET /notify/status` — Get notification status
- `POST /notify/test` — Test notification sending

### Admin
- `GET /admin/users` — User management interface
- `GET /admin/jobs` — Job management interface  
- `GET /admin/leads` — Lead management interface
- `POST /admin/api/job/{id}/cancel` — Cancel job
- `POST /admin/api/job/{id}/restart` — Restart job
- `POST /admin/api/user/{id}/toggle` — Toggle user status

### Analytics
- `GET /analytics` — Analytics dashboard
- `GET /analytics/api/performance` — Performance metrics
- `GET /analytics/api/lead-status` — Lead distribution
- `GET /analytics/api/video-types` — Video type stats

## Development

### Testing
See [TESTING.md](TESTING.md) for comprehensive testing instructions.

### Adding New Features
1. Create blueprint in `src/new_feature.py`
2. Register blueprint in `app.py`
3. Add templates in `templates/`
4. Update navigation in `templates/base.html`
5. Add tests and update documentation

## License
MIT License - see LICENSE file for details.
