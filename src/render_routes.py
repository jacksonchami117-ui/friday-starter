import os, json, subprocess, csv, datetime as dt, hashlib
import pandas as pd
from flask import Blueprint, request, jsonify, render_template, current_app, flash, redirect, url_for

render_bp = Blueprint('render', __name__, url_prefix='/render')

def _data_dir():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.getenv("DATA_DIR", os.path.join(base, "state"))

def _paths():
    d = _data_dir()
    return {
        "accepted": os.path.join(d, "accepted_leads.csv"),
        "outputs": os.path.join(d, "outputs", "videos"),
        "progress": os.path.join(d, "render_progress.csv"),
    }

STATE_DIR = os.environ.get("STATE_DIR", "state")
OUTPUT_DIR = os.path.join(STATE_DIR, "outputs")
TEMPLATES_DIR = os.path.join(STATE_DIR, "templates")
EXPORTS_DIR = os.path.join(STATE_DIR, "exports")
for d in (OUTPUT_DIR, EXPORTS_DIR): os.makedirs(d, exist_ok=True)

def progress_path(cid): return os.path.join(EXPORTS_DIR, f"{cid}_progress.csv")
def token_for(val): return hashlib.sha1(val.encode()).hexdigest()[:16]

@render_bp.route("/start/<campaign_id>", methods=["POST"])
def start_render(campaign_id):
    manifest_path = os.path.join(TEMPLATES_DIR, f"manifest_{campaign_id}.json")
    if not os.path.exists(manifest_path):
        return jsonify({"error": f"No manifest for {campaign_id}"}), 404

    with open(manifest_path) as f:
        manifest = json.load(f)

    out = os.path.join(OUTPUT_DIR, f"{campaign_id}.mp4")
    thumb = os.path.join(OUTPUT_DIR, f"{campaign_id}.png")

    subprocess.run([
        "ffmpeg", "-f", "lavfi", "-i", "color=c=blue:s=320x240:d=5",
        "-vf", "drawtext=text='Rendered Video':x=(w-text_w)/2:y=(h-text_h)/2:fontsize=24:fontcolor=white",
        out, "-y"
    ])
    subprocess.run(["ffmpeg", "-i", out, "-ss", "00:00:01", "-vframes", "1", thumb, "-y"])

    headers = ["campaign","date","status","video","thumb","share"]
    row = [campaign_id, dt.datetime.utcnow().isoformat(), "done", out, thumb, f"/v/{campaign_id}/{token_for(campaign_id)}"]
    csv_exists = os.path.exists(progress_path(campaign_id))
    with open(progress_path(campaign_id), "a", newline="") as f:
        w = csv.writer(f)
        if not csv_exists: w.writerow(headers)
        w.writerow(row)

    return jsonify({"ok": True, "output": out, "thumb": thumb, "progress": progress_path(campaign_id)})

@render_bp.route("/start", methods=["GET"])
def start_rendering():
    p = _paths()
    if not os.path.exists(p["accepted"]):
        return "<h3>No leads uploaded yet. Upload leads first.</h3>", 400
    try:
        df = pd.read_csv(p["accepted"])
        preview_html = df.head(20).to_html(classes="table", index=False)
        return f"""
        <h2>Render Preview</h2>
        <p>Loaded {len(df)} leads from file.</p>
        <h3>Preview:</h3>
        {preview_html}
        <br><br><a href='/home'>← Back to Dashboard</a>
        """
    except Exception as e:
        current_app.logger.error(f"Error reading leads: {e}")
        return f"<h3>Error reading leads: {e}</h3>", 500

@render_bp.route("/run", methods=["GET", "POST"])
def run_render():
    p = _paths()
    os.makedirs(p["outputs"], exist_ok=True)

    if not os.path.exists(p["accepted"]):
        flash("No leads uploaded yet.", "warning")
        return redirect(url_for("leads.leads_home"))

    # Dummy render: one file per lead
    total, ok = 0, 0
    with open(p["accepted"], newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        rows = list(reader)

    # write progress
    prog_path = p["progress"]
    with open(prog_path, "w", newline="", encoding="utf-8") as f_prog:
        writer = csv.writer(f_prog)
        writer.writerow(["index", "status", "note"])

        for i, row in enumerate(rows, start=1):
            total += 1
            try:
                first = row.get("first_name") or row.get("First Name") or row.get("First") or row.get("Name") or ""
                email = row.get("email") or row.get("Email") or ""
                fname = f"lead_{i:04d}.txt"
                out_path = os.path.join(p["outputs"], fname)
                with open(out_path, "w", encoding="utf-8") as f_out:
                    f_out.write(f"Hello {first or 'there'} ({email}), this is a placeholder render.\n")
                writer.writerow([i, "ok", fname])
                ok += 1
            except Exception as e:
                writer.writerow([i, "error", str(e)])
                current_app.logger.exception("Render error")

    flash(f"Rendered {ok}/{total} outputs (dummy files).", "success")
    return redirect(url_for("exports.explore"))

@render_bp.route("/")
def index():
    return render_template("render.html")
