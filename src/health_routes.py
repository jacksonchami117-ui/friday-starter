import os
import subprocess
import shutil
from flask import Blueprint, render_template, current_app, redirect, url_for
from flask_login import current_user
from src.auth import ADMIN_PASSWORD

health_bp = Blueprint("health_ui", __name__, url_prefix="/health")

def get_ffmpeg_version():
    """Get FFmpeg version for health check"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        if result.returncode == 0:
            first_line = result.stdout.split('\n')[0]
            return first_line
        return "FFmpeg not found"
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return "FFmpeg not available"

def get_disk_usage(path: str):
    """Get disk usage for given path"""
    try:
        total, used, free = shutil.disk_usage(path)
        return {
            "total": total // (1024**3),  # GB
            "used": used // (1024**3),
            "free": free // (1024**3),
            "percent": int((used / total) * 100) if total > 0 else 0
        }
    except Exception:
        return {"error": "Unable to get disk usage"}

def get_redis_status():
    """Check Redis connection"""
    try:
        import redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        r = redis.Redis.from_url(redis_url)
        r.ping()
        return {"status": "connected", "url": redis_url}
    except ImportError:
        return {"status": "redis library not installed"}
    except Exception as e:
        return {"status": "disconnected", "error": str(e)}

def get_celery_status():
    """Check Celery worker status"""
    if not os.getenv("USE_CELERY") == "1":
        return {"status": "disabled"}
    
    try:
        from celery_worker import celery
        stats = celery.control.inspect().stats()
        if stats:
            active_workers = len(stats)
            return {"status": "active", "workers": active_workers, "details": stats}
        return {"status": "no workers"}
    except ImportError:
        return {"status": "celery not available"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def get_queue_depth():
    """Get render queue depth"""
    if not os.getenv("USE_CELERY") == "1":
        return {"status": "celery disabled"}
    
    try:
        from celery_worker import celery
        inspect = celery.control.inspect()
        active = inspect.active()
        reserved = inspect.reserved()
        
        total_active = sum(len(tasks) for tasks in (active or {}).values())
        total_reserved = sum(len(tasks) for tasks in (reserved or {}).values())
        
        return {
            "active": total_active,
            "reserved": total_reserved,
            "total": total_active + total_reserved
        }
    except Exception as e:
        return {"error": str(e)}

@health_bp.route("/", methods=["GET"])
def health_check():
    """Simple health check endpoint"""
    return "ok", 200

@health_bp.route("/ui", methods=["GET"])
def health_ui():
    """Health dashboard UI"""
    # Check if admin login is required
    if ADMIN_PASSWORD:
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
    
    # Gather health information
    data_dir = current_app.config.get("DATA_DIR", "state")
    
    health_data = {
        "ffmpeg": get_ffmpeg_version(),
        "disk": get_disk_usage(data_dir),
        "redis": get_redis_status(),
        "celery": get_celery_status(),
        "queue": get_queue_depth(),
        "data_dir": data_dir,
        "s3_enabled": bool(os.getenv("S3_BUCKET"))
    }
    
    # Get error log tail
    from src.diagnostics_routes import tail_lines
    log_path = os.path.join(data_dir, "logs", "app.log")
    error_logs = tail_lines(log_path, n=20)
    
    return render_template("health_ui.html", health=health_data, error_logs=error_logs)
