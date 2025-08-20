import os
import pandas as pd
from flask import Blueprint, render_template, request, redirect, url_for, current_app

leads_bp = Blueprint("leads", __name__, url_prefix="/leads")

DATA_DIR = os.getenv("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "state"))
os.makedirs(DATA_DIR, exist_ok=True)


@leads_bp.route("/", methods=["GET"])
def leads_home():
    """Show the leads upload page"""
    return render_template("leads.html")


@leads_bp.route("/upload", methods=["POST"])
def upload_leads():
    """Handle CSV upload"""
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    # Save uploaded CSV
    save_path = os.path.join(DATA_DIR, "accepted_leads.csv")
    file.save(save_path)

    # Try reading with pandas
    try:
        df = pd.read_csv(save_path)
        rows = len(df)
        cols = list(df.columns)
    except Exception as e:
        return f"Error reading CSV: {str(e)}", 400

    # Show confirmation page
    return render_template(
        "leads_confirm.html",
        rows=rows,
        cols=cols
    )
