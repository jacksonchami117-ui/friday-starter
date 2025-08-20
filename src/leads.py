import os
import csv
import pandas as pd
from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename

leads_bp = Blueprint("leads", __name__, url_prefix="/leads")

UPLOAD_EXT = {".csv", ".xlsx"}

# Map messy CSV headers to clean names
COLUMN_MAP = {
    "first name": "First",
    "firstname": "First",
    "last name": "Last",
    "lastname": "Last",
    "phone number": "Phone",
    "phone": "Phone",
    "business": "Business",
    "address": "Address",
    "email": "Email",
    "website": "Website",
}

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    new_cols = []
    for c in df.columns:
        key = c.strip().lower()
        new_cols.append(COLUMN_MAP.get(key, c.strip()))
    df.columns = new_cols
    return df

@leads_bp.route("", methods=["GET", "POST"])
def leads_home():
    data_dir = current_app.config["DATA_DIR"]
    upload_dir = os.path.join(data_dir, "uploads")
    accepted_path = os.path.join(data_dir, "accepted_leads.csv")

    leads = []
    if request.method == "POST":
        f = request.files.get("file")
        if not f:
            flash("No file provided", "danger")
            return redirect(url_for("leads.leads_home"))

        ext = os.path.splitext(f.filename)[1].lower()
        if ext not in UPLOAD_EXT:
            flash("Unsupported file type", "danger")
            return redirect(url_for("leads.leads_home"))

        save_path = os.path.join(upload_dir, secure_filename(f.filename))
        f.save(save_path)

        if ext == ".csv":
            df = pd.read_csv(save_path)
        else:
            df = pd.read_excel(save_path)

        df = normalize_columns(df)

        # Save accepted leads only (no rejection logic yet)
        df.to_csv(accepted_path, index=False)

        flash(f"Imported {len(df)} leads.", "success")

    if os.path.exists(accepted_path):
        with open(accepted_path, newline="") as f_in:
            reader = csv.DictReader(f_in)
            leads = list(reader)

    return render_template("leads.html", leads=leads)
