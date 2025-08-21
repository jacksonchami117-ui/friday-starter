"""
Metrics module for FRIDAY system.
Handles application metrics and monitoring.
"""

import time
import psutil
from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify, current_app
from src.auth import login_required
from src.store import get_data_store

metrics_bp = Blueprint('metrics', __name__, url_prefix='/metrics')

class MetricsCollector:
    """Collects and tracks application metrics."""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        
    def record_request(self, endpoint=None, method=None, status_code=None, response_time=None):
        """Record a request metric."""
        self.request_count += 1
        
        if status_code and status_code >= 400:
            self.error_count += 1
        
        # Store in database
        store = get_data_store()
        store.store_metric('request', 'count', 1, {
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'response_time': response_time
        })
    
    def record_job_metric(self, job_type, status, processing_time=None):
        """Record job processing metrics."""
        store = get_data_store()
        store.store_metric('job', f'{job_type}_{status}', 1, {
            'job_type': job_type,
            'status': status,
            'processing_time': processing_time
        })
    
    def get_system_metrics(self):
        """Get current system metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_gb': memory.used / (1024**3),
                'memory_total_gb': memory.total / (1024**3),
                'disk_percent': disk.percent,
                'disk_used_gb': disk.used / (1024**3),
                'disk_total_gb': disk.total / (1024**3),
                'uptime_seconds': time.time() - self.start_time
            }
        except Exception as e:
            current_app.logger.error(f"Error getting system metrics: {e}")
            return {
                'cpu_percent': 0,
                'memory_percent': 0,
                'memory_used_gb': 0,
                'memory_total_gb': 0,
                'disk_percent': 0,
                'disk_used_gb': 0,
                'disk_total_gb': 0,
                'uptime_seconds': time.time() - self.start_time
            }
    
    def get_application_metrics(self):
        """Get application-specific metrics."""
        store = get_data_store()
        
        # Get job metrics for last 24 hours
        job_metrics = store.get_metrics('job', hours=24)
        
        job_counts = {
            'total': len(job_metrics),
            'successful': len([m for m in job_metrics if 'done' in m['metric_name']]),
            'failed': len([m for m in job_metrics if 'failed' in m['metric_name']]),
            'processing': len([m for m in job_metrics if 'processing' in m['metric_name']])
        }
        
        # Get request metrics
        request_metrics = store.get_metrics('request', hours=24)
        
        return {
            'total_requests': self.request_count,
            'total_errors': self.error_count,
            'recent_requests': len(request_metrics),
            'job_counts': job_counts,
            'error_rate': (self.error_count / max(self.request_count, 1)) * 100
        }

# Global metrics collector
metrics_collector = MetricsCollector()

def get_metrics_collector():
    """Get the metrics collector instance."""
    return metrics_collector

@metrics_bp.route('/')
@login_required
def metrics_dashboard():
    """Display metrics dashboard."""
    collector = get_metrics_collector()
    
    system_metrics = collector.get_system_metrics()
    app_metrics = collector.get_application_metrics()
    
    return render_template('metrics_dashboard.html', 
                         system_metrics=system_metrics,
                         app_metrics=app_metrics)

@metrics_bp.route('/api/system')
@login_required
def api_system_metrics():
    """API endpoint for system metrics."""
    collector = get_metrics_collector()
    return jsonify(collector.get_system_metrics())

@metrics_bp.route('/api/application')
@login_required
def api_application_metrics():
    """API endpoint for application metrics."""
    collector = get_metrics_collector()
    return jsonify(collector.get_application_metrics())

@metrics_bp.route('/api/jobs')
@login_required
def api_job_metrics():
    """API endpoint for job metrics."""
    store = get_data_store()
    job_metrics = store.get_metrics('job', hours=24)
    
    return jsonify({
        'metrics': job_metrics,
        'summary': {
            'total': len(job_metrics),
            'by_type': {},
            'by_status': {}
        }
    })

def record_request_metric(endpoint, method, status_code, response_time):
    """Helper function to record request metrics."""
    metrics_collector.record_request(endpoint, method, status_code, response_time)

def record_job_metric(job_type, status, processing_time=None):
    """Helper function to record job metrics."""
    metrics_collector.record_job_metric(job_type, status, processing_time)