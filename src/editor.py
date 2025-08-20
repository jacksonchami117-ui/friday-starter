
from flask import Blueprint

editor_bp = Blueprint("editor", __name__, url_prefix="/editor")

@editor_bp.route("/", methods=["GET"])
def editor_home():
    return "Editor module (placeholder)."
