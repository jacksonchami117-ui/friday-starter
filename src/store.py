"""
Store module for FRIDAY system.
Handles data storage and persistence.
"""

import os
import json
import pickle
import sqlite3
from datetime import datetime
from contextlib import contextmanager
from flask import current_app

class DataStore:
    """Simple data store for application data."""
    
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, 'friday.db')
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database."""
        os.makedirs(self.data_dir, exist_ok=True)
        
        with self.get_connection() as conn:
            # Jobs table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data TEXT
                )
            ''')
            
            # Metrics table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metric_type TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    metadata TEXT
                )
            ''')
            
            # Settings table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context management."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()
    
    def store_job(self, job_id, job_type, status, data=None):
        """Store job information."""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO jobs (id, type, status, data, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (job_id, job_type, status, json.dumps(data) if data else None))
            conn.commit()
    
    def get_job(self, job_id):
        """Get job by ID."""
        with self.get_connection() as conn:
            row = conn.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
            if row:
                job = dict(row)
                if job['data']:
                    job['data'] = json.loads(job['data'])
                return job
        return None
    
    def get_jobs(self, status=None, limit=100):
        """Get jobs with optional status filter."""
        with self.get_connection() as conn:
            if status:
                rows = conn.execute('''
                    SELECT * FROM jobs WHERE status = ? 
                    ORDER BY created_at DESC LIMIT ?
                ''', (status, limit)).fetchall()
            else:
                rows = conn.execute('''
                    SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?
                ''', (limit,)).fetchall()
            
            jobs = []
            for row in rows:
                job = dict(row)
                if job['data']:
                    job['data'] = json.loads(job['data'])
                jobs.append(job)
            
            return jobs
    
    def update_job_status(self, job_id, status, data=None):
        """Update job status."""
        with self.get_connection() as conn:
            if data:
                conn.execute('''
                    UPDATE jobs SET status = ?, data = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (status, json.dumps(data), job_id))
            else:
                conn.execute('''
                    UPDATE jobs SET status = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (status, job_id))
            conn.commit()
    
    def store_metric(self, metric_type, metric_name, value, metadata=None):
        """Store a metric."""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO metrics (metric_type, metric_name, value, metadata)
                VALUES (?, ?, ?, ?)
            ''', (metric_type, metric_name, float(value), json.dumps(metadata) if metadata else None))
            conn.commit()
    
    def get_metrics(self, metric_type=None, hours=24, limit=1000):
        """Get metrics with optional filtering."""
        with self.get_connection() as conn:
            if metric_type:
                rows = conn.execute('''
                    SELECT * FROM metrics 
                    WHERE metric_type = ? AND timestamp > datetime('now', '-{} hours')
                    ORDER BY timestamp DESC LIMIT ?
                '''.format(hours), (metric_type, limit)).fetchall()
            else:
                rows = conn.execute('''
                    SELECT * FROM metrics 
                    WHERE timestamp > datetime('now', '-{} hours')
                    ORDER BY timestamp DESC LIMIT ?
                '''.format(hours), (limit,)).fetchall()
            
            metrics = []
            for row in rows:
                metric = dict(row)
                if metric['metadata']:
                    metric['metadata'] = json.loads(metric['metadata'])
                metrics.append(metric)
            
            return metrics
    
    def get_setting(self, key, default=None):
        """Get a setting value."""
        with self.get_connection() as conn:
            row = conn.execute('SELECT value FROM settings WHERE key = ?', (key,)).fetchone()
            if row:
                return json.loads(row['value'])
        return default
    
    def set_setting(self, key, value):
        """Set a setting value."""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, json.dumps(value)))
            conn.commit()
    
    def cleanup_old_data(self, days=30):
        """Clean up old data."""
        with self.get_connection() as conn:
            # Clean old metrics
            conn.execute('''
                DELETE FROM metrics 
                WHERE timestamp < datetime('now', '-{} days')
            '''.format(days))
            
            # Clean old completed jobs
            conn.execute('''
                DELETE FROM jobs 
                WHERE status IN ('done', 'failed') 
                AND updated_at < datetime('now', '-{} days')
            '''.format(days))
            
            conn.commit()


class FileStore:
    """File-based storage for larger data."""
    
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.files_dir = os.path.join(data_dir, 'files')
        os.makedirs(self.files_dir, exist_ok=True)
    
    def store_file(self, key, data, binary=False):
        """Store data to file."""
        file_path = os.path.join(self.files_dir, f"{key}.{'bin' if binary else 'json'}")
        
        if binary:
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
        else:
            with open(file_path, 'w') as f:
                json.dump(data, f, default=str, indent=2)
    
    def load_file(self, key, binary=False, default=None):
        """Load data from file."""
        file_path = os.path.join(self.files_dir, f"{key}.{'bin' if binary else 'json'}")
        
        if not os.path.exists(file_path):
            return default
        
        try:
            if binary:
                with open(file_path, 'rb') as f:
                    return pickle.load(f)
            else:
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            current_app.logger.error(f"Error loading file {key}: {e}")
            return default
    
    def delete_file(self, key, binary=False):
        """Delete stored file."""
        file_path = os.path.join(self.files_dir, f"{key}.{'bin' if binary else 'json'}")
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False


# Global store instances
data_store = None
file_store = None

def get_data_store():
    """Get or create data store instance."""
    global data_store
    if data_store is None:
        data_dir = current_app.config.get('DATA_DIR', 'state')
        data_store = DataStore(data_dir)
    return data_store

def get_file_store():
    """Get or create file store instance."""
    global file_store
    if file_store is None:
        data_dir = current_app.config.get('DATA_DIR', 'state')
        file_store = FileStore(data_dir)
    return file_store