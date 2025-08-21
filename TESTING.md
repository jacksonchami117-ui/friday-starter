# FRIDAY Testing Guide

This document outlines how to test the FRIDAY video outreach system.

## Prerequisites

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (optional):
```bash
export FRIDAY_DEFAULT_USER=admin
export FRIDAY_DEFAULT_PASS=friday123
export SECRET_KEY=your-secret-key
export DATA_DIR=./state
```

## Smoke Tests

### 1. Basic System Startup
```bash
python app.py
```
Expected: Server starts on http://localhost:5000

### 2. Authentication System Test
1. Navigate to http://localhost:5000/auth/login
2. Login with credentials:
   - Username: `admin`
   - Password: `friday123`
3. Verify redirect to dashboard

Expected: Successful login and redirect

### 3. Render System Test
1. Ensure you're logged in
2. Navigate to http://localhost:5000/render/list
3. Click "Start New Render Job"
4. Monitor job status progression: queued → processing → done

Expected: Job completes successfully with output files in `state/outputs/videos/`

### 4. API Endpoints Test
Test the following endpoints:
- `GET /health` - Should return "OK"
- `GET /auth/status` - Check authentication status
- `GET /render/api/jobs` - List render jobs (requires auth)
- `POST /render/start` - Start new render job (requires auth)

## Integration Tests

### 1. Full Workflow Test
1. Start the application
2. Login via `/auth/login`
3. Upload leads data (if available)
4. Start a render job via `/render/list`
5. Monitor job progression via `/render/status/{job_id}`
6. Verify output files are created in `state/outputs/videos/`

### 2. Authentication Flow Test
1. Access protected route without login (should redirect to login)
2. Login with valid credentials
3. Access protected route (should work)
4. Logout
5. Try to access protected route again (should redirect to login)

### 3. Render Queue Test
1. Start multiple render jobs simultaneously
2. Verify they are queued and processed correctly
3. Check that job status updates are reflected in the UI
4. Verify output files are created for each job

## Test Data

### Sample Leads Data
Create a CSV file with the following structure:
```csv
first_name,email
John,john@example.com
Jane,jane@example.com
Bob,bob@example.com
```

Save as `state/uploads/accepted_leads.csv`

## Expected Outputs

### Successful Render Job
- Status progresses: queued → processing → done
- Output files created in `state/outputs/videos/`
- Files named like: `video_john_timestamp_1.mp4`
- Job completion message shows processed count

### System Health
- `/health` returns HTTP 200 with "OK"
- No critical errors in logs
- All protected routes require authentication
- Sessions persist correctly

## Troubleshooting

### Common Issues
1. **Import errors**: Ensure all dependencies are installed
2. **Permission errors**: Check file/directory permissions in `state/` folder
3. **Authentication issues**: Verify environment variables or use defaults
4. **Job failures**: Check logs in `state/logs/app.log`

### Debug Mode
Run with debug enabled:
```bash
FLASK_ENV=development python app.py
```

### Logs Location
Application logs: `state/logs/app.log`
Job data: `state/render_jobs.json`

## Performance Tests

### Load Testing
1. Start multiple render jobs (test concurrency)
2. Upload large lead files (test file handling)
3. Monitor system resource usage
4. Verify system remains responsive

### Stress Testing
1. Create 100+ lead entries
2. Start render job
3. Monitor memory usage and processing time
4. Verify output quality and completeness

## Security Tests

### Authentication Tests
1. Attempt to access protected routes without login
2. Test with invalid credentials
3. Verify session timeout
4. Test CSRF protection (if enabled)

### Input Validation Tests
1. Upload malformed CSV files
2. Test with special characters in lead data
3. Verify file type validation
4. Test file size limits

## Automated Testing

To run automated tests (if available):
```bash
python -m pytest tests/
```

Or using the test runner:
```bash
python -m unittest discover tests/
```

## Deployment Testing

### Local Deployment
```bash
gunicorn app:app --bind 0.0.0.0:5000
```

### Docker Testing
```bash
docker build -t friday-app .
docker run -p 5000:5000 friday-app
```

### Environment Testing
Test with different environment configurations:
- Development
- Production
- Testing

## Monitoring

### Key Metrics to Monitor
- Response times for API endpoints
- Memory usage during render jobs
- File system usage in output directories
- Error rates and types
- Authentication success/failure rates

### Health Checks
Regular checks for:
- Database connectivity (if used)
- File system permissions
- External service dependencies
- System resource availability