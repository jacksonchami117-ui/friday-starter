from flask import Blueprint, render_template

editor_bp = Blueprint("editor", __name__, url_prefix="/editor")

@editor_bp.route("/", methods=["GET"])
def editor_home():
    return render_template("editor.html")
