import os
import pandas as pd
from flask import Blueprint, render_template, request, redirect, url_for

leads_bp = Blueprint('leads', __name__, url_prefix='/leads')

DATA_DIR = os.getenv("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "state"))
os.makedirs(DATA_DIR, exist_ok=True)

@leads_bp.route("/", methods=["GET"])
def leads_home():
    # Show the upload form
    return render_template("leads.html")

@leads_bp.route("/upload", methods=["POST"])
def upload_leads():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    save_path = os.path.join(DATA_DIR, "accepted_leads.csv")
    file.save(save_path)

    # Optional: validate CSV
    try:
        df = pd.read_csv(save_path)
        print(f"Uploaded CSV with {len(df)} rows")
    except Exception as e:
        return f"Error reading CSV: {str(e)}", 400

    # ✅ After upload, redirect to main dashboard
    return redirect(url_for("index"))
