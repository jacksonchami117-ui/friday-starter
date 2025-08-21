# FRIDAY System Testing Guide

This document provides comprehensive testing procedures for the FRIDAY system, covering smoke tests, feature validation, and integration testing.

## Prerequisites

1. **Environment Setup**
   ```bash
   pip install -r requirements.txt
   export DATA_DIR=./test_data
   export USE_DB=0  # Start with CSV mode
   ```

2. **Test Data Directory**
   ```bash
   mkdir -p test_data/{uploads,outputs/videos,outputs/thumbs,logs,batches,assets,templates,db}
   ```

## Smoke Tests

### 1. Basic Application Startup

**Objective**: Verify the application starts without errors

**Steps**:
1. Start the application: `python app.py`
2. Verify startup messages in logs
3. Check health endpoint: `curl http://localhost:5000/health`
4. Access main interface: http://localhost:5000

**Expected Results**:
- Application starts on port 5000
- Health endpoint returns "OK"  
- Main interface loads without errors
- Navigation menu is visible

### 2. Data Source Configuration

**Objective**: Test both CSV and database modes

**CSV Mode Test**:
```bash
export USE_DB=0
python app.py
```
- Visit http://localhost:5000/dashboard
- Verify "Data Source" shows "CSV Files"
- Check that directories are created under DATA_DIR

**Database Mode Test**:
```bash
export USE_DB=1
python app.py
```
- Visit http://localhost:5000/dashboard  
- Verify "Data Source" shows "SQLite Database"
- Check that database file is created at `{DATA_DIR}/db/friday.db`

### 3. Core Navigation

**Objective**: Verify all main navigation links work

**Steps**:
1. Visit each navigation link:
   - Dashboard: http://localhost:5000/dashboard
   - Projects: http://localhost:5000/projects (may show 404, that's expected)
   - SOPs: http://localhost:5000/sops (may show 404, that's expected) 
   - Decisions: http://localhost:5000/decisions (may show 404, that's expected)
   - Runs: http://localhost:5000/runs (may show 404, that's expected)
   - Analytics: http://localhost:5000/analytics
   - Settings: http://localhost:5000/settings (may show 404, that's expected)

**Expected Results**:
- Dashboard loads with notifications panel and data source info
- Analytics loads with charts (may show placeholders without Chart.js CDN)
- 404 pages for unimplemented features are acceptable

## Feature Pack Testing

### Feature Pack 1: Notifications

**Test Notification Toggle**:
1. Visit http://localhost:5000/dashboard
2. Click "Notifications" toggle button
3. Verify button text changes between "Enabled" and "Disabled"
4. Check success message appears

**Test Notification Status API**:
```bash
curl http://localhost:5000/notify/status
```
Expected: JSON response with notification status

**Test Notification Providers**:
```bash
# Test email notification (stub)
curl -X POST http://localhost:5000/notify/test \
  -H "Content-Type: application/json" \
  -d '{"type": "email", "to_email": "test@example.com"}'

# Test SMS notification (stub)  
curl -X POST http://localhost:5000/notify/test \
  -H "Content-Type: application/json" \
  -d '{"type": "sms", "to_phone": "+1234567890"}'
```

### Feature Pack 2: Admin Tools

**Test Admin Users Interface**:
1. Visit http://localhost:5000/admin/users
2. Verify user table loads with mock data
3. Test user status toggle (should show confirmation)
4. Verify statistics cards show correct counts

**Test Admin Jobs Interface**:
1. Visit http://localhost:5000/admin/jobs  
2. Verify job table with different statuses
3. Test job actions (cancel/restart buttons)
4. Verify auto-refresh for running jobs (wait 30 seconds)

**Test Admin Leads Interface**:
1. Visit http://localhost:5000/admin/leads
2. Verify leads table (may be empty initially)
3. Test filter dropdown and search functionality
4. Test bulk selection and actions

### Feature Pack 3: Analytics

**Test Analytics Dashboard**:
1. Visit http://localhost:5000/analytics
2. Verify summary cards show metrics
3. Check that charts load (may show placeholders without CDN)
4. Test refresh button
5. Verify data table shows performance data

**Test Analytics API Endpoints**:
```bash
# Test each API endpoint
curl http://localhost:5000/analytics/api/performance
curl http://localhost:5000/analytics/api/lead-status  
curl http://localhost:5000/analytics/api/video-types
curl http://localhost:5000/analytics/api/processing-times
curl http://localhost:5000/analytics/api/lead-sources
curl http://localhost:5000/analytics/api/resource-usage
curl http://localhost:5000/analytics/api/summary
```

### Feature Pack 4: Database Persistence

**Test Database Initialization**:
```bash
export USE_DB=1
python app.py
```
1. Check logs for database initialization messages
2. Verify database file exists: `ls -la test_data/db/friday.db`
3. Check data source API: `curl http://localhost:5000/api/data-source`

**Test Lead Upload with Database**:
1. Create test CSV file:
   ```bash
   cat > test_leads.csv << EOF
   name,email,company
   John Smith,john@example.com,TechCorp
   Jane Doe,jane@example.com,InnovateCo
   EOF
   ```
2. Upload via leads interface: http://localhost:5000/leads
3. Check leads list: http://localhost:5000/leads/list
4. Verify data in database (if sqlite3 available):
   ```bash
   sqlite3 test_data/db/friday.db "SELECT * FROM leads;"
   ```

**Test CSV Fallback**:
```bash
export USE_DB=0
python app.py
```
1. Upload same test CSV
2. Verify CSV files created in test_data/
3. Check leads list still works

## Integration Testing

### Lead Processing Workflow

**Full Lead Processing Test**:
1. Start with fresh data directory
2. Upload lead CSV file
3. Verify leads appear in admin interface
4. Check analytics show updated metrics  
5. Test notification system with lead events

### Cross-Feature Integration

**Dashboard Integration Test**:
1. Upload leads (database or CSV mode)
2. Visit dashboard - verify data source indicator
3. Toggle notifications - verify state persists
4. Visit analytics - verify lead data appears
5. Check admin interfaces show consistent data

### Error Handling

**Database Error Handling**:
1. Set USE_DB=1 but make database directory read-only
2. Upload leads - should fallback to CSV with warning
3. Restore permissions and verify recovery

**File System Error Handling**:
1. Make uploads directory read-only
2. Try uploading leads - should show error message
3. Restore permissions

## Performance Testing

### Load Testing

**Basic Load Test**:
```bash
# Install ab (Apache Bench) if available
apt-get install apache2-utils

# Test dashboard performance
ab -n 100 -c 10 http://localhost:5000/dashboard

# Test analytics API
ab -n 100 -c 10 http://localhost:5000/analytics/api/summary
```

### Memory Usage
Monitor memory usage during:
- Large CSV uploads (1000+ leads)
- Analytics dashboard with large datasets  
- Multiple concurrent admin operations

## Regression Testing

Before deploying changes, run this checklist:

- [ ] Application starts in both CSV and DB modes
- [ ] Health endpoint responds  
- [ ] Dashboard loads with all panels
- [ ] Lead upload works in both modes
- [ ] Notifications can be toggled
- [ ] Admin interfaces load without errors
- [ ] Analytics dashboard displays data
- [ ] Navigation between all implemented features works
- [ ] Error messages are user-friendly
- [ ] No console errors in browser developer tools

## Test Data Cleanup

After testing:
```bash
# Remove test data
rm -rf test_data/

# Reset environment
unset USE_DB
unset DATA_DIR
```

## Automated Testing

For continuous integration, create a test script:

```bash
#!/bin/bash
# test_smoke.sh

set -e

export DATA_DIR=./test_data
mkdir -p $DATA_DIR

echo "Testing CSV mode..."
export USE_DB=0
python -c "
import requests
import subprocess
import time
import os

# Start server in background
proc = subprocess.Popen(['python', 'app.py'])
time.sleep(3)

try:
    # Test health endpoint
    resp = requests.get('http://localhost:5000/health')
    assert resp.status_code == 200
    assert resp.text == 'OK'
    
    # Test dashboard
    resp = requests.get('http://localhost:5000/dashboard')  
    assert resp.status_code == 200
    
    print('CSV mode tests passed')
finally:
    proc.terminate()
"

echo "Testing database mode..."
export USE_DB=1
python -c "
import requests
import subprocess
import time

proc = subprocess.Popen(['python', 'app.py'])
time.sleep(3)

try:
    resp = requests.get('http://localhost:5000/api/data-source')
    assert resp.status_code == 200
    data = resp.json()
    assert data['using_database'] == True
    
    print('Database mode tests passed')
finally:
    proc.terminate()
"

rm -rf $DATA_DIR
echo "All smoke tests passed!"
```

Run with: `bash test_smoke.sh`

## Troubleshooting

### Common Issues

1. **Port 5000 in use**: Change PORT environment variable
2. **Permission denied on data directory**: Check directory permissions
3. **Chart.js not loading**: Check internet connection for CDN access
4. **Database locked**: Ensure no other processes are using the database
5. **CSV upload fails**: Check file permissions and format

### Debug Mode

Enable debug logging:
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

### Log Analysis

Check application logs for errors:
```bash
tail -f {DATA_DIR}/logs/app.log
```