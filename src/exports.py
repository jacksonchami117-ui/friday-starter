import os, csv, zipfile
from datetime import datetime
from flask import Blueprint, render_template, send_file, current_app, flash

exports_bp = Blueprint("exports", __name__, url_prefix="/exports")

# Map messy names -> clean names
COLUMN_MAP = {
    "first name": "First",
    "firstname": "First",
    "last name": "Last",
    "lastname": "Last",
    "phone number": "Phone",
    "phone": "Phone",
    "email": "Email",
    "website": "Website",
}

def normalize(row: dict) -> dict:
    fixed = {}
    for k,v in row.items():
        key = k.strip().lower()
        fixed[COLUMN_MAP.get(key, k.strip())] = v
    return fixed

@exports_bp.route("", methods=["GET"])
def exports_home():
    data_dir = current_app.config["DATA_DIR"]
    path = os.path.join(data_dir, "render_progress.csv")
    exports = []
    if os.path.exists(path):
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            exports = [normalize(r) for r in reader]
    return render_template("exports.html", exports=exports)

@exports_bp.route("/download/instantly.csv")
def download_instantly():
    data_dir = current_app.config["DATA_DIR"]
    path = os.path.join(data_dir, "render_progress.csv")
    if not os.path.exists(path):
        flash("No rendered videos yet", "danger")
        return render_template("exports.html", exports=[])

    out_file = os.path.join(data_dir, "instantly_export.csv")
    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            r = normalize(r)
            rows.append({
                "First": r.get("First",""),
                "Last": r.get("Last",""),
                "Email": r.get("Email",""),
                "thumbnailEmbed": f'<img src="{r.get("thumbnail","")}" width="200">'
            })

    with open(out_file,"w",newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=["First","Last","Email","thumbnailEmbed"])
        writer.writeheader()
        writer.writerows(rows)

    return send_file(out_file, as_attachment=True)
