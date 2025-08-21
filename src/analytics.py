import os
import json
import logging
import random
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, current_app

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")

def _data_dir():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.getenv("DATA_DIR", os.path.join(base, "state"))

def _paths():
    d = _data_dir()
    return {
        "analytics": os.path.join(d, "analytics.json"),
        "logs": os.path.join(d, "logs"),
    }

# Mock data generators for analytics
def generate_mock_metrics():
    """Generate mock analytics data"""
    
    # Generate date series (last 30 days)
    dates = []
    for i in range(29, -1, -1):
        date = datetime.now() - timedelta(days=i)
        dates.append(date.strftime('%Y-%m-%d'))
    
    # Lead processing metrics
    lead_processing = {
        'dates': dates,
        'processed': [random.randint(50, 200) for _ in dates],
        'accepted': [random.randint(30, 150) for _ in dates],
        'rejected': [random.randint(10, 50) for _ in dates],
    }
    
    # Video generation metrics  
    video_generation = {
        'dates': dates,
        'generated': [random.randint(10, 80) for _ in dates],
        'success_rate': [random.randint(80, 98) for _ in dates],
        'avg_time_minutes': [random.randint(120, 300) for _ in dates],
    }
    
    # System performance
    system_performance = {
        'dates': dates,
        'cpu_usage': [random.randint(20, 80) for _ in dates],
        'memory_usage': [random.randint(30, 85) for _ in dates],
        'disk_usage': [random.randint(10, 60) for _ in dates],
    }
    
    # Lead sources distribution
    lead_sources = {
        'labels': ['Website Forms', 'Email Campaign', 'Social Media', 'Referrals', 'Direct Upload'],
        'data': [random.randint(50, 300) for _ in range(5)]
    }
    
    # Video types distribution
    video_types = {
        'labels': ['Product Demo', 'Testimonial', 'Explainer', 'Social Media', 'Training'],
        'data': [random.randint(20, 150) for _ in range(5)]
    }
    
    # Processing time distribution
    processing_time_dist = {
        'labels': ['< 1 hour', '1-2 hours', '2-4 hours', '4-8 hours', '> 8 hours'],
        'data': [random.randint(10, 100) for _ in range(5)]
    }
    
    return {
        'lead_processing': lead_processing,
        'video_generation': video_generation,
        'system_performance': system_performance,
        'lead_sources': lead_sources,
        'video_types': video_types,
        'processing_time_distribution': processing_time_dist,
        'summary_stats': {
            'total_leads_processed': sum(lead_processing['processed']),
            'total_videos_generated': sum(video_generation['generated']),
            'avg_success_rate': sum(video_generation['success_rate']) / len(video_generation['success_rate']),
            'avg_processing_time': sum(video_generation['avg_time_minutes']) / len(video_generation['avg_time_minutes']),
            'current_cpu_usage': random.randint(20, 80),
            'current_memory_usage': random.randint(30, 85),
            'current_disk_usage': random.randint(10, 60),
        }
    }

@analytics_bp.route("/")
def analytics_dashboard():
    """Main analytics dashboard"""
    try:
        return render_template("analytics/dashboard.html")
    except Exception as e:
        current_app.logger.exception("Analytics dashboard failed")
        return f"Analytics dashboard error: {str(e)}", 500

@analytics_bp.route("/data")
def analytics_data():
    """API endpoint to get all analytics data"""
    try:
        metrics = generate_mock_metrics()
        return jsonify({
            'status': 'success',
            'data': metrics,
            'generated_at': datetime.now().isoformat()
        })
    except Exception as e:
        current_app.logger.exception("Analytics data API failed")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@analytics_bp.route("/leads")
def leads_analytics():
    """Lead processing analytics data"""
    try:
        metrics = generate_mock_metrics()
        return jsonify({
            'status': 'success',
            'data': {
                'processing': metrics['lead_processing'],
                'sources': metrics['lead_sources'],
                'summary': {
                    'total_processed': metrics['summary_stats']['total_leads_processed'],
                    'acceptance_rate': round(
                        sum(metrics['lead_processing']['accepted']) / 
                        sum(metrics['lead_processing']['processed']) * 100, 1
                    )
                }
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@analytics_bp.route("/videos")  
def videos_analytics():
    """Video generation analytics data"""
    try:
        metrics = generate_mock_metrics()
        return jsonify({
            'status': 'success',
            'data': {
                'generation': metrics['video_generation'],
                'types': metrics['video_types'],
                'processing_time': metrics['processing_time_distribution'],
                'summary': {
                    'total_generated': metrics['summary_stats']['total_videos_generated'],
                    'avg_success_rate': round(metrics['summary_stats']['avg_success_rate'], 1),
                    'avg_processing_time': round(metrics['summary_stats']['avg_processing_time'], 1)
                }
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@analytics_bp.route("/performance")
def performance_analytics():
    """System performance analytics data"""
    try:
        metrics = generate_mock_metrics()
        return jsonify({
            'status': 'success',
            'data': {
                'system': metrics['system_performance'],
                'current': {
                    'cpu': metrics['summary_stats']['current_cpu_usage'],
                    'memory': metrics['summary_stats']['current_memory_usage'],
                    'disk': metrics['summary_stats']['current_disk_usage']
                }
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@analytics_bp.route("/export")
def export_analytics():
    """Export analytics data as JSON"""
    try:
        export_type = request.args.get('type', 'all')
        metrics = generate_mock_metrics()
        
        if export_type == 'leads':
            data = {
                'lead_processing': metrics['lead_processing'],
                'lead_sources': metrics['lead_sources']
            }
        elif export_type == 'videos':
            data = {
                'video_generation': metrics['video_generation'],
                'video_types': metrics['video_types'],
                'processing_time_distribution': metrics['processing_time_distribution']
            }
        elif export_type == 'performance':
            data = {
                'system_performance': metrics['system_performance']
            }
        else:
            data = metrics
        
        return jsonify({
            'status': 'success',
            'export_type': export_type,
            'data': data,
            'exported_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500