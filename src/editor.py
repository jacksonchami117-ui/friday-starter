from flask import Blueprint

editor_bp = Blueprint("editor", __name__, url_prefix="/editor")

@editor_bp.route("/", methods=["GET"])
def editor_home():
    return "Editor module (placeholder)."

@editor_bp.route("/save/<campaign_id>", methods=["POST"])
def save_manifest(campaign_id):
    data = request.json
    path = os.path.join(TEMPLATES_DIR, f"manifest_{campaign_id}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return jsonify({"ok": True, "path": path})

@editor_bp.route("/load/<campaign_id>", methods=["GET"])
def load_manifest(campaign_id):
    path = os.path.join(TEMPLATES_DIR, f"manifest_{campaign_id}.json")
    if os.path.exists(path):
        with open(path) as f:
            return jsonify(json.load(f))
    return jsonify({"error": f"No manifest found for {campaign_id}"}), 404

@editor_bp.route("/list", methods=["GET"])
def list_manifests():
    manifests = []
    for fn in os.listdir(TEMPLATES_DIR):
        if fn.startswith("manifest_") and fn.endswith(".json"):
            cid = fn.replace("manifest_", "").replace(".json", "")
            manifests.append(cid)
    return jsonify({"campaigns": manifests})

from flask import Blueprint

editor_bp = Blueprint("editor", __name__, url_prefix="/editor")

@editor_bp.route("/", methods=["GET"])
def editor_home():
    return "Editor module (placeholder)."
