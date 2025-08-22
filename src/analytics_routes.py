from flask import Blueprint, render_template, send_file, jsonify
import os, csv

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")

STATE_DIR = os.environ.get("STATE_DIR", "state")
EXPORTS_DIR = os.path.join(STATE_DIR, "exports")

def parse_csv(path):
    rows = []
    if os.path.exists(path):
        with open(path) as f:
            reader = csv.DictReader(f)
            for r in reader: rows.append(r)
    return rows

@analytics_bp.route("/")
def index():
    data = {}
    for fn in os.listdir(EXPORTS_DIR):
        if fn.endswith("_progress.csv"):
            cid = fn.replace("_progress.csv","")
            data[cid] = parse_csv(os.path.join(EXPORTS_DIR, fn))
    return render_template("analytics.html", data=data)

@analytics_bp.route("/csv/<cid>")
def download_csv(cid):
    path = os.path.join(EXPORTS_DIR, f"{cid}_progress.csv")
    if not os.path.exists(path): return jsonify({"error":"no export"}),404
    return send_file(path, as_attachment=True)

@analytics_bp.route("/retry/<cid>", methods=["POST"])
def retry(cid):
    return jsonify({"ok":True,"cid":cid,"message":"Retry triggered"})
