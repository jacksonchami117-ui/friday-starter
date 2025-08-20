from flask import Blueprint, render_template

exports_bp = Blueprint("exports", __name__, url_prefix="/exports")

@exports_bp.route("/", methods=["GET"])
def exports_home():
    return render_template("exports.html")
