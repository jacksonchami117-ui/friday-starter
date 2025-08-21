
import os
import csv
import zipfile
from datetime import datetime
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
        "rejected": os.path.join(d, "rejected_leads.csv"),
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

@exports_bp.route("/export_accepted_csv", methods=["POST"])
def export_accepted_csv():
    """Export accepted leads with date-stamped filename"""
    p = _paths()
    if not os.path.exists(p["accepted"]):
        flash("No accepted leads to export.", "warning")
        return redirect(url_for("exports.explore"))

    # Generate date-stamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"accepted_{timestamp}.csv"
    export_path = os.path.join(p["outputs"], filename)

    # Read and write CSV
    with open(p["accepted"], newline="", encoding="utf-8") as f_in:
        rows = list(csv.DictReader(f_in))

    os.makedirs(p["outputs"], exist_ok=True)
    with open(export_path, "w", newline="", encoding="utf-8") as f_out:
        if rows:
            writer = csv.DictWriter(f_out, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        else:
            f_out.write("")
    
    flash(f"Created {filename}.", "success")
    return redirect(url_for("exports.explore"))

@exports_bp.route("/export_rejected_csv", methods=["POST"])
def export_rejected_csv():
    """Export rejected leads with date-stamped filename"""
    p = _paths()
    if not os.path.exists(p["rejected"]):
        flash("No rejected leads to export.", "warning")
        return redirect(url_for("exports.explore"))

    # Generate date-stamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"rejected_{timestamp}.csv"
    export_path = os.path.join(p["outputs"], filename)

    # Read and write CSV
    with open(p["rejected"], newline="", encoding="utf-8") as f_in:
        rows = list(csv.DictReader(f_in))

    os.makedirs(p["outputs"], exist_ok=True)
    with open(export_path, "w", newline="", encoding="utf-8") as f_out:
        if rows:
            writer = csv.DictWriter(f_out, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        else:
            f_out.write("")
    
    flash(f"Created {filename}.", "success")
    return redirect(url_for("exports.explore"))

@exports_bp.route("/export_accepted_xlsx", methods=["POST"])
def export_accepted_xlsx():
    """Export accepted leads as XLSX with date-stamped filename"""
    p = _paths()
    if not os.path.exists(p["accepted"]):
        flash("No accepted leads to export.", "warning")
        return redirect(url_for("exports.explore"))

    # Check if openpyxl is available
    try:
        import pandas as pd
        import openpyxl
    except ImportError:
        flash("XLSX export requires openpyxl. Please install it or use CSV export instead.", "warning")
        return redirect(url_for("exports.explore"))

    # Generate date-stamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"accepted_{timestamp}.xlsx"
    export_path = os.path.join(p["outputs"], filename)

    # Read CSV and export to XLSX
    try:
        df = pd.read_csv(p["accepted"])
        os.makedirs(p["outputs"], exist_ok=True)
        df.to_excel(export_path, index=False, engine='openpyxl')
        flash(f"Created {filename}.", "success")
    except Exception as e:
        current_app.logger.error(f"XLSX export error: {e}")
        flash("XLSX export failed. Please try CSV export instead.", "danger")
    
    return redirect(url_for("exports.explore"))

@exports_bp.route("/export_rejected_xlsx", methods=["POST"])
def export_rejected_xlsx():
    """Export rejected leads as XLSX with date-stamped filename"""
    p = _paths()
    if not os.path.exists(p["rejected"]):
        flash("No rejected leads to export.", "warning")
        return redirect(url_for("exports.explore"))

    # Check if openpyxl is available
    try:
        import pandas as pd
        import openpyxl
    except ImportError:
        flash("XLSX export requires openpyxl. Please install it or use CSV export instead.", "warning")
        return redirect(url_for("exports.explore"))

    # Generate date-stamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"rejected_{timestamp}.xlsx"
    export_path = os.path.join(p["outputs"], filename)

    # Read CSV and export to XLSX
    try:
        df = pd.read_csv(p["rejected"])
        os.makedirs(p["outputs"], exist_ok=True)
        df.to_excel(export_path, index=False, engine='openpyxl')
        flash(f"Created {filename}.", "success")
    except Exception as e:
        current_app.logger.error(f"XLSX export error: {e}")
        flash("XLSX export failed. Please try CSV export instead.", "danger")
    
    return redirect(url_for("exports.explore"))
