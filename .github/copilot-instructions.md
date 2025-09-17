# Friday Martial Arts OS - Development Instructions

**CRITICAL**: Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

Friday is a modular Flask-based video personalization platform with TypeScript frontend, Celery background processing, and FFmpeg video rendering capabilities. The system enables drag-and-drop video editing, lead management, and automated video generation.

## Core Architecture
- **Backend**: Python Flask application with SQLAlchemy ORM and Alembic migrations
- **Frontend**: TypeScript/Node.js with Express server 
- **Database**: PostgreSQL (production) / SQLite (development)
- **Background Processing**: Celery with Redis broker
- **Video Processing**: FFmpeg for rendering and manipulation
- **Authentication**: Flask-Login with admin password authentication

## Working Effectively

### Initial Environment Setup
Always perform these steps in order when starting work on a fresh clone:

```bash
# Install system dependencies
sudo apt-get update && sudo apt-get install -y ffmpeg

# Setup Python environment (takes 40 seconds)
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Setup Node.js environment (takes 4 seconds)
npm install

# Fix TypeScript configuration if needed
# Ensure tsconfig.json has "module": "ESNext" for ES modules compatibility

# Setup database
mkdir -p state
export PYTHONPATH=/home/runner/work/friday-starter/friday-starter
alembic upgrade head

# Environment variables
export ADMIN_PASSWORD=test123
export PYTHONPATH=/home/runner/work/friday-starter/friday-starter
```

### Build Commands

**Python Build & Test** (NEVER CANCEL - set timeout to 3+ minutes):
```bash
source .venv/bin/activate
export PYTHONPATH=/home/runner/work/friday-starter/friday-starter

# Run tests (takes ~2 seconds, may have some expected failures)
pytest --cov=src --cov-report=term-missing -q

# Lint Python code (takes ~1 second, will show many style issues)
flake8 src/ --max-line-length=120
```

**TypeScript Build** (NEVER CANCEL - set timeout to 2+ minutes):
```bash
# Build TypeScript (takes ~3 seconds)
npm run build

# Start production Node server
npm run start
```

### Running the Applications

**Python Flask Application**:
```bash
source .venv/bin/activate
export PYTHONPATH=/home/runner/work/friday-starter/friday-starter
export ADMIN_PASSWORD=test123
python app.py
# Runs on http://localhost:5000
```

**TypeScript Development Server**:
```bash
# Note: Development mode has ES module issues, use production mode
npm run build && npm run start
# Runs on http://localhost:8081
```

**Docker Compose** (if needed):
```bash
docker-compose up
# App on port 8081, PostgreSQL on port 5432
```

## Validation Scenarios

### Manual Testing Requirements
ALWAYS test these workflows after making changes:

1. **Health Check Validation**:
   ```bash
   curl http://localhost:5000/health  # Should return "ok"
   ```

2. **Authentication Flow**:
   - Visit http://localhost:5000/auth/login
   - Login with ADMIN_PASSWORD
   - Verify access to authenticated pages

3. **Core Application Flow**:
   - Access home page (/)
   - Navigate to editor (/editor/)
   - Check diagnostics page (/diagnostics/)

4. **Database Operations**:
   ```bash
   alembic current  # Check migration status
   alembic upgrade head  # Apply migrations
   ```

### Build Timing Expectations
- **NEVER CANCEL builds or long-running commands**
- Python dependency installation: ~40 seconds (set timeout: 120+ seconds)
- Node.js dependency installation: ~4 seconds (set timeout: 60+ seconds) 
- TypeScript compilation: ~3 seconds (set timeout: 60+ seconds)
- Python tests: ~2 seconds (set timeout: 180+ seconds)
- Python linting: ~1 second (set timeout: 60+ seconds)
- Flask app startup: ~2 seconds
- Node.js server startup: ~1 second

## Code Quality & CI

### Pre-commit Validation
Always run these before committing changes:
```bash
source .venv/bin/activate
export PYTHONPATH=/home/runner/work/friday-starter/friday-starter

# Python linting (will show style issues but shouldn't block)
flake8 src/ --max-line-length=120

# Python formatting (optional - black is available)
black src/

# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# TypeScript build
npm run build
```

### CI Pipeline Simulation
The GitHub Actions CI runs these steps:
1. Install system dependencies (ffmpeg)
2. Setup Python 3.11 environment
3. Install Python dependencies
4. Install test dependencies (pytest-flask, pytest-cov)
5. Run pytest with coverage reporting
6. Setup Node.js 20
7. Run npm install && npm run build

## Common Issues & Solutions

### Python Import Issues
- Always set `export PYTHONPATH=/home/runner/work/friday-starter/friday-starter`
- Database models are in `src/db.py`, not individual module files
- Use `source .venv/bin/activate` for all Python commands

### TypeScript/Node.js Issues
- The project uses ES modules (`"type": "module"` in package.json)
- Development server (npm run dev) has module issues - use production mode
- tsconfig.json should have `"module": "ESNext"` for proper compilation

### Database Issues
- Ensure `state/` directory exists before running migrations
- SQLite is used by default for development
- Alembic configuration has been fixed (%%04d format string)

### Test Failures
- Some test failures are expected due to route configuration
- Health tests should pass - these indicate basic Flask functionality
- Focus on maintaining passing health tests when making changes

## Key File Locations

### Configuration Files
- `package.json` - Node.js dependencies and scripts
- `requirements.txt` - Python dependencies
- `tsconfig.json` - TypeScript configuration
- `alembic.ini` - Database migration configuration
- `.github/workflows/ci.yml` - CI pipeline definition

### Application Structure
- `app.py` - Main Flask application entry point
- `src/` - All Python source code (blueprints, models, utilities)
- `src/db.py` - Database models (Lead, Order, User)
- `src/server.ts` - TypeScript Express server
- `templates/` - Jinja2 HTML templates
- `static/` - CSS, JavaScript, and asset files
- `migrations/` - Alembic database migration files
- `tests/` - pytest test files

### Important Directories
- `state/` - Runtime data (database, logs, uploads)
- `dist/` - Compiled TypeScript output
- `.venv/` - Python virtual environment

## Development Workflow

1. **Setup Environment**: Follow "Initial Environment Setup" section
2. **Make Changes**: Edit source files in `src/` or frontend files
3. **Test Locally**: Run the validation scenarios above
4. **Pre-commit Checks**: Run linting and tests
5. **Commit**: Changes are automatically validated by CI

## Known Limitations

- Development TypeScript server has ES module issues - use production build
- Python code has many linting violations (style issues) - these don't block functionality
- Some test routes return 404/302 due to authentication requirements - this is expected
- Database migrations require manual `state/` directory creation
- FFmpeg must be installed system-wide for video processing features

Always prioritize working functionality over perfect code style. The application runs successfully despite linting warnings.