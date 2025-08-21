import os
from flask import Blueprint, render_template

bp_logs = Blueprint("logs", __name__, url_prefix="/logs")

def _data_dir():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.getenv("DATA_DIR", os.path.join(base, "state"))

@bp_logs.route("/", methods=["GET"])
def logs_viewer():
    """View application logs with last ~200 lines"""
    d = _data_dir()
    log_path = os.path.join(d, "logs", "app.log")
    
    def tail_logs(path, n=200):
        """Get last n lines from log file"""
        if not os.path.exists(path):
            return ["[No log file found yet]"]
        
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            # Get last n lines, but keep them as strings (strip newlines for clean display)
            tail_lines = lines[-n:] if len(lines) > n else lines
            return [line.rstrip('\n\r') for line in tail_lines]
        except Exception as e:
            return [f"[Error reading log file: {e}]"]
    
    log_lines = tail_logs(log_path, 200)
    
    return render_template("logs.html", 
                         log_lines=log_lines, 
                         log_count=len(log_lines))