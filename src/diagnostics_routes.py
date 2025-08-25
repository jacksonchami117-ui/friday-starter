import os
from collections import deque
from flask import Blueprint, render_template

diagnostics_bp = Blueprint("diagnostics", __name__, url_prefix="/diagnostics")

def _data_dir():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.getenv("DATA_DIR", os.path.join(base, "state"))

@diagnostics_bp.route("/", methods=["GET"], endpoint="diagnostics_home")
@diagnostics_bp.route("", methods=["GET"])
def diagnostics_home():
    d = _data_dir()
    log_path = os.path.join(d, "logs", "app.log")
    accepted = os.path.join(d, "accepted_leads.csv")
    rejected = os.path.join(d, "rejected_leads.csv")
    outputs = os.path.join(d, "outputs", "videos")

    def tail(path, n=50):
        if not os.path.exists(path):
            return ["(no logs yet)"]
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return list(deque(f, maxlen=n))

    counts = {
        "accepted": 0,
        "rejected": 0,
        "outputs": 0,
    }
    if os.path.exists(accepted):
        with open(accepted, newline="", encoding="utf-8") as f:
            counts["accepted"] = max(sum(1 for _ in f) - 1, 0)
    if os.path.exists(rejected):
        with open(rejected, newline="", encoding="utf-8") as f:
            counts["rejected"] = max(sum(1 for _ in f) - 1, 0)
    if os.path.exists(outputs):
        counts["outputs"] = len([n for n in os.listdir(outputs) if os.path.isfile(os.path.join(outputs, n))])

    return render_template("diagnostics.html", log_tail=tail(log_path, 80), counts=counts)


