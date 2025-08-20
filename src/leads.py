
import os
import csv
import re
import json
import pandas as pd
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename

leads_bp = Blueprint("leads", __name__, url_prefix="/leads")

UPLOAD_EXT = {".csv", ".xlsx"}

def _data_dir():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.getenv("DATA_DIR", os.path.join(base, "state"))

def _paths():
    d = _data_dir()
    return {
        "uploads": os.path.join(d, "uploads"),
        "accepted": os.path.join(d, "accepted_leads.csv"),
        "rejected": os.path.join(d, "rejected_leads.csv"),
        "map_json": os.path.join(d, "column_map.json"),
    }

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(c).strip() for c in df.columns]
    return df

def validate_row(row: dict):
    reasons = []
    # Required presence
    required_any = ["email", "Email", "e-mail"]
    if not any(row.get(k, "").strip() for k in row.keys() if k in required_any):
        reasons.append("Missing email")
    # Rough email check
    email_val = None
    for k in ["Email", "email", "E-mail"]:
        if k in row:
            email_val = str(row.get(k, "")).strip()
            break
    if email_val and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email_val):
        reasons.append("Invalid email format")
    return reasons

@leads_bp.route("/", methods=["GET"])
def leads_home():
    return render_template("leads.html")

@leads_bp.route("/upload", methods=["POST"])
def upload_leads():
    paths = _paths()
    os.makedirs(paths["uploads"], exist_ok=True)

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

    save_path = os.path.join(paths["uploads"], secure_filename(f.filename))
    f.save(save_path)

    # Read file
    try:
        if ext == ".csv":
            df = pd.read_csv(save_path)
        else:
            df = pd.read_excel(save_path)
    except Exception as e:
        current_app.logger.error(f"Error reading file: {e}")
        flash(f"Error reading file: {e}", "danger")
        return redirect(url_for("leads.leads_home"))

    df = normalize_columns(df)

    # Validate
    accepted_rows, rejected_rows = [], []
    for _, row in df.iterrows():
        data = row.to_dict()
        reasons = validate_row(data)
        if reasons:
            data["Reason"] = "; ".join(reasons)
            rejected_rows.append(data)
        else:
            accepted_rows.append(data)

    # Write accepted
    acc_cols = list(df.columns)
    if accepted_rows:
        with open(paths["accepted"], "w", newline="", encoding="utf-8") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=acc_cols)
            writer.writeheader()
            for r in accepted_rows:
                writer.writerow({k: r.get(k, "") for k in acc_cols})

    # Write rejected
    rej_cols = list(df.columns) + (["Reason"] if "Reason" not in df.columns else [])
    if rejected_rows:
        with open(paths["rejected"], "w", newline="", encoding="utf-8") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=rej_cols)
            writer.writeheader()
            for r in rejected_rows:
                writer.writerow({k: r.get(k, "") for k in rej_cols})

    flash(f"Uploaded {len(df)} rows → Accepted: {len(accepted_rows)}, Rejected: {len(rejected_rows)}", "success")
    return render_template(
        "leads_confirm.html",
        rows=len(accepted_rows),
        rejected=len(rejected_rows),
        cols=list(df.columns)
    )

@leads_bp.route("/list", methods=["GET"])
def list_leads():
    paths = _paths()
    if not os.path.exists(paths["accepted"]):
        flash("No leads uploaded yet.", "warning")
        return redirect(url_for("leads.leads_home"))

    with open(paths["accepted"], newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        leads = list(reader)

    return render_template("leads_list.html", leads=leads)

@leads_bp.route("/rejected", methods=["GET"])
def list_rejected():
    paths = _paths()
    if not os.path.exists(paths["rejected"]):
        flash("No rejected leads to show.", "info")
        return redirect(url_for("leads.leads_home"))

    with open(paths["rejected"], newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        rows = list(reader)

    return render_template("leads_rejected.html", rows=rows)

# --- Column Mapping ---
SYSTEM_FIELDS = ["first_name", "email", "phone", "website"]

@leads_bp.route("/mapping", methods=["GET", "POST"])
def mapping():
    paths = _paths()
    if not os.path.exists(paths["accepted"]):
        flash("Please upload leads first.", "warning")
        return redirect(url_for("leads.leads_home"))

    # Load accepted headers
    with open(paths["accepted"], newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        headers = reader.fieldnames or []

    # If POST, save mapping
    if request.method == "POST":
        mapping = {}
        for field in SYSTEM_FIELDS:
            csv_col = request.form.get(field)  # may be ""
            mapping[field] = csv_col or ""

        # Save mapping JSON
        with open(paths["map_json"], "w", encoding="utf-8") as f:
            json.dump(mapping, f, indent=2)

        # Apply mapping: rename columns if mapped
        df = pd.read_csv(paths["accepted"])
        rename_map = {}
        for sys_field, csv_col in mapping.items():
            if csv_col and csv_col in df.columns:
                rename_map[csv_col] = sys_field
        if rename_map:
            # Backup original
            backup_path = paths["accepted"].replace(".csv", "_original.csv")
            try:
                if not os.path.exists(backup_path):
                    os.replace(paths["accepted"], backup_path)
                else:
                    # If backup exists, just read accepted
                    pass
            except Exception:
                pass
            df = pd.read_csv(backup_path) if os.path.exists(backup_path) else df
            df = df.rename(columns=rename_map)
            df.to_csv(paths["accepted"], index=False)

        flash("Column mapping saved.", "success")
        return redirect(url_for("leads.list_leads"))

    # Auto-suggest mapping (exact matches ignoring case/space)
    suggestions = {}
    lowered = {h.lower().replace(" ", ""): h for h in headers}
    for f in SYSTEM_FIELDS:
        key = f.lower().replace("_", "")
        suggestions[f] = lowered.get(key, "")

    # If we have an existing map, load it to pre-select
    existing = {}
    if os.path.exists(paths["map_json"]):
        try:
            existing = json.load(open(paths["map_json"], "r", encoding="utf-8"))
        except Exception:
            existing = {}

    return render_template(
        "mapping.html",
        headers=headers,
        system_fields=SYSTEM_FIELDS,
        suggestions=suggestions,
        existing=existing
    )
