import os
from flask import Blueprint, render_template, current_app

logs_bp = Blueprint("logs", __name__, url_prefix="/logs")

def _data_dir():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.getenv("DATA_DIR", os.path.join(base, "state"))

@logs_bp.route("/", methods=["GET"])
def logs_viewer():
    """Show last 200 lines from app.log"""
    data_dir = _data_dir()
    log_path = os.path.join(data_dir, "logs", "app.log")
    
    log_lines = []
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                all_lines = f.readlines()
                # Get last 200 lines
                log_lines = all_lines[-200:] if len(all_lines) > 200 else all_lines
                # Remove trailing newlines for display
                log_lines = [line.rstrip() for line in log_lines]
        except Exception as e:
            current_app.logger.error(f"Error reading log file: {e}")
            log_lines = [f"Error reading log file: {e}"]
    else:
        log_lines = ["Log file not found. No logs available yet."]
    
    return render_template("logs.html", log_lines=log_lines, log_path=log_path)