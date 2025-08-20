import os
import pandas as pd
from flask import Blueprint, render_template, current_app

render_bp = Blueprint('render', __name__, url_prefix='/render')

DATA_DIR = os.getenv("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "state"))
LEADS_FILE = os.path.join(DATA_DIR, "accepted_leads.csv")

@render_bp.route("/start", methods=["GET"])
def start_rendering():
    """Start rendering from uploaded leads."""
    if not os.path.exists(LEADS_FILE):
        return "<h3>No leads uploaded yet. Upload leads first.</h3>", 400

    try:
        df = pd.read_csv(LEADS_FILE)

        # For now just preview what’s inside
        preview_html = df.head(20).to_html(classes="table", index=False)

        return f"""
        <h2>Rendering Started</h2>
        <p>Loaded {len(df)} leads from file.</p>
        <h3>Preview of leads:</h3>
        {preview_html}
        <br><br>
        <a href='/home'>← Back to Dashboard</a>
        """
    except Exception as e:
        current_app.logger.error(f"Error reading leads: {e}")
        return f"<h3>Error reading leads: {e}</h3>", 500
