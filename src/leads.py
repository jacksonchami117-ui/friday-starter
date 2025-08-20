import os
import csv
import pandas as pd
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename

# Create blueprint
leads_bp = Blueprint("leads", __name__, url_prefix="/leads")

# Allowed file extensions
UPLOAD_EXT = {".csv", ".xlsx"}

# Ensure state folder exists
DATA_DIR = os.getenv("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "state"))
os.makedirs(DATA_DIR, exist_ok=True)
accepted_path = os.path.join(DATA_DIR, "accepted_leads.csv")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names to consistent format."""
    df.columns = [c.strip().title() for c in df.columns]
    return df


@leads_bp.route("/", methods=["GET"])
def leads_home():
    """Show upload form."""
    return render_template("leads.html")


@leads_bp.route("/upload", methods=["POST"])
def upload_leads():
    """Handle CSV/XLSX file upload."""
    if "file" not in request.files:
        flash("No file part", "danger")
        return redirect(url_for("leads.leads_home"))

    f = request.files["file"]
    if f.filename == "":
        flash("No file selected", "danger")
        return redirect(url_for("leads.leads_home"))

    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in UPLOAD_EXT:
        flash("Unsupported file type. Please upload CSV or XLSX.", "danger")
        return redirect(url_for("leads.leads_home"))

    # Save uploaded file
    upload_dir = os.path.join(DATA_DIR, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    save_path = os.path.join(upload_dir, secure_filename(f.filename))
    f.save(save_path)

    # Load into DataFrame
    try:
        if ext == ".csv":
            df = pd.read_csv(save_path)
        else:
            df = pd.read_excel(save_path)
    except Exception as e:
        current_app.logger.error(f"Error reading file: {e}")
        flash(f"Error reading file: {e}", "danger")
        return redirect(url_for("leads.leads_home"))

    # Normalize and save
    df = normalize_columns(df)
    df.to_csv(accepted_path, index=False)

    flash(f"Imported {len(df)} leads successfully.", "success")
    return render_template("leads_confirm.html", rows=len(df), cols=list(df.columns))


@leads_bp.route("/list", methods=["GET"])
def list_leads():
    """Display uploaded leads in table view."""
    if not os.path.exists(accepted_path):
        flash("No leads uploaded yet.", "warning")
        return redirect(url_for("leads.leads_home"))

    try:
        with open(accepted_path, newline="") as f_in:
            reader = csv.DictReader(f_in)
            leads = list(reader)
    except Exception as e:
        current_app.logger.error(f"Error reading saved leads: {e}")
        flash(f"Error reading saved leads: {e}", "danger")
        return redirect(url_for("leads.leads_home"))

    return render_template("leads_list.html", leads=leads)
