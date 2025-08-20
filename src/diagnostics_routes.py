from flask import Blueprint, render_template

diagnostics_bp = Blueprint("diagnostics", __name__, url_prefix="/diagnostics")

@diagnostics_bp.route("/", methods=["GET"])
def diagnostics_home():
    return render_template("diagnostics.html")
