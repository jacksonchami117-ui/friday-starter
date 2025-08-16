from flask import Flask, render_template, request
import os, json
from datetime import datetime

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(BASE_DIR, "state")

def load_json(name, default):
    path = os.path.join(STATE_DIR, name)
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default

@app.route("/")
def intro():
    return render_template("intro.html", title="Initiating FRIDAY protocol…")

@app.route("/dashboard")
def dashboard():
    projects = load_json("projects.json", [])
    sops     = load_json("sops.json", [])
    decisions= load_json("decisions.json", [])
    runs     = load_json("runs.json", [])
    pending_decisions = len([d for d in decisions if not d.get("resolved")])
    return render_template("dashboard.html",
                           title="FRIDAY Dashboard",
                           projects=projects, sops=sops,
                           decisions=decisions, runs=runs,
                           pending_decisions=pending_decisions)

@app.route("/projects")
def projects_page():
    projects = load_json("projects.json", [])
    return render_template("list.html", title="Projects", items=projects, kind="project")

@app.route("/sops")
def sops_page():
    sops = load_json("sops.json", [])
    return render_template("list.html", title="SOPs", items=sops, kind="sop")

@app.route("/decisions")
def decisions_page():
    decisions = load_json("decisions.json", [])
    return render_template("list.html", title="Decisions", items=decisions, kind="decision")

@app.route("/runs")
def runs_page():
    runs = load_json("runs.json", [])
    return render_template("list.html", title="Runs", items=runs, kind="run")

@app.route("/settings")
def settings_page():
    return render_template("settings.html", title="Settings")

@app.get("/healthz")
def healthz():
    return {"ok": True, "ts": datetime.utcnow().isoformat() + "Z"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
