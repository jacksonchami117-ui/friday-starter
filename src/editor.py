import os
import json
from flask import request, jsonify, current_app
from flask import Blueprint
from werkzeug.utils import secure_filename

editor_bp = Blueprint("editor", __name__, url_prefix="/editor")


def _templates_dir():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = current_app.config.get("DATA_DIR", os.path.join(base, "state"))
    path = os.path.join(data_dir, "templates")
    os.makedirs(path, exist_ok=True)
    return path

@editor_bp.route("/", methods=["GET"])
def index():
    return "Editor module (placeholder)."

@editor_bp.route("/save/<campaign_id>", methods=["POST"])
def save_manifest(campaign_id):
    data = request.json
    cid = secure_filename(campaign_id)
    path = os.path.join(_templates_dir(), f"manifest_{cid}.json")
    with open(path, "w", encoding="utf-8", newline="") as f:
        json.dump(data, f, indent=2)
    return jsonify({"ok": True, "path": path})

@editor_bp.route("/load/<campaign_id>", methods=["GET"])
def load_manifest(campaign_id):
    cid = secure_filename(campaign_id)
    path = os.path.join(_templates_dir(), f"manifest_{cid}.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8", newline="") as f:
            return jsonify(json.load(f))
    return jsonify({"error": f"No manifest found for {campaign_id}"}), 404

@editor_bp.route("/list", methods=["GET"])
def list_manifests():
    manifests = []
    tdir = _templates_dir()
    for fn in os.listdir(tdir):
        if fn.startswith("manifest_") and fn.endswith(".json"):
            cid = fn.replace("manifest_", "").replace(".json", "")
            manifests.append(cid)
    return jsonify({"campaigns": manifests})
