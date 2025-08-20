
import os
import csv
import zipfile
from flask import Blueprint, render_template, send_from_directory, current_app, redirect, url_for, flash

exports_bp = Blueprint("exports", __name__, url_prefix="/exports")

def _data_dir():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.getenv("DATA_DIR", os.path.join(base, "state"))

def _paths():
    d = _data_dir()
    return {
        "outputs": os.path.join(d, "outputs", "videos"),
        "zip_path": os.path.join(d, "outputs", "videos_batch.zip"),
        "accepted": os.path.join(d, "accepted_leads.csv"),
        "export_csv": os.path.join(d, "outputs", "exports.csv"),
    }

@exports_bp.route("/", methods=["GET"])
def explore():
    p = _paths()
    os.makedirs(p["outputs"], exist_ok=True)
    files = []
    for name in sorted(os.listdir(p["outputs"])):
        fp = os.path.join(p["outputs"], name)
        if os.path.isfile(fp):
            files.append({"name": name, "size": os.path.getsize(fp)})
    return render_template("exports.html", files=files)

@exports_bp.route("/zip", methods=["POST"])
def make_zip():
    p = _paths()
    os.makedirs(os.path.dirname(p["zip_path"]), exist_ok=True)
    with zipfile.ZipFile(p["zip_path"], "w", zipfile.ZIP_DEFLATED) as z:
        for name in os.listdir(p["outputs"]):
            fp = os.path.join(p["outputs"], name)
            if os.path.isfile(fp):
                z.write(fp, arcname=name)
    flash("Created batch ZIP.", "success")
    return redirect(url_for("exports.explore"))

@exports_bp.route("/download/<path:filename>")
def download_file(filename):
    p = _paths()
    return send_from_directory(p["outputs"], filename, as_attachment=True)

@exports_bp.route("/export_csv", methods=["POST"])
def make_export_csv():
    p = _paths()
    if not os.path.exists(p["accepted"]):
        flash("No accepted leads to export.", "warning")
        return redirect(url_for("exports.explore"))

    with open(p["accepted"], newline="", encoding="utf-8") as f_in:
        rows = list(csv.DictReader(f_in))

    os.makedirs(os.path.dirname(p["export_csv"]), exist_ok=True)
    with open(p["export_csv"], "w", newline="", encoding="utf-8") as f_out:
        if rows:
            writer = csv.DictWriter(f_out, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        else:
            f_out.write("")
    flash("Created exports.csv.", "success")
    return redirect(url_for("exports.explore"))
